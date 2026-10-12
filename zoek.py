"""Auto voor Annemarie: elektrisch of plug-in hybride, max EUR 8.000, Nederland.

Haalt aanbod op van AutoScout24.nl en Marktplaats, filtert microcars, accuhuur,
schade en gewone (niet-plug-in) hybrides eruit, geeft elke auto een score op
betrouwbaarheid model + bouwjaar + kilometerstand en schrijft docs/data.json.
Draait dagelijks via GitHub Actions (zie .github/workflows/dagelijks.yml).
"""
import json
import re
import sys
import time
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import requests
from bs4 import BeautifulSoup

MAX_PRIJS = 8000
MIN_PRIJS = 1500          # lager = lease, huur, bod of nep
MAX_KM = 260000
MIN_JAAR = 2010
TZ = ZoneInfo('Europe/Amsterdam')

ROOT = Path(__file__).parent
DATA = ROOT / 'docs' / 'data.json'
GEZIEN = ROOT / 'docs' / 'gezien.json'

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                  '(KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36',
    'Accept-Language': 'nl-NL,nl;q=0.9',
}

# Microcars, brommobielen, quadricycles en bestelbussen: nooit tonen.
UITSLUITEN = [
    'ami', 'rocks-e', 'rocks e', 'twizy', 'biro', 'estrima', 'aixam', 'ligier', 'microcar',
    'chatenet', 'microlino', 'tazzari', 'topolino', 'brommobiel', '45 km', '45km', 'bellier',
    'jdm', 'casalini', 'kewet', 'buddy', 'reva', 'think city', 'goupil', 'club car',
    'streetscooter', 'c-zero', 'czero', 'ion', 'i-miev', 'imiev', 'fortwo', 'for two',
    'kangoo', 'ducato', 'e-nv200', 'env200', 'bestel', 'express', 'maxi', 'cargo', 'vito',
    'e-ducato', 'master', 'transit', 'golfkar', 'quad', 'renault fluence',
]
# Accu niet bij de koop inbegrepen (maandelijkse huur) of overige ellende.
ELLENDE = [
    'huur accu', 'huuraccu', 'accuhuur', 'accu huur', 'ex accu', 'ex. accu', 'excl accu',
    'excl. accu', 'exclusief accu', 'zonder accu', 'accu moet', 'batterijhuur', 'huurbatterij',
    'schade', 'defect', 'export', 'opknapper', 'niet rijdend', 'starten niet', 'motor kapot',
    'huren', 'renting', 'onderdelen', 'sloop', 'accupakket moet',
]
# Handelaren in schadeauto's die schade niet altijd in de advertentie zetten. Aanvullen als er
# een kapotte auto in de lijst opduikt.
SCHADE_VERKOPERS = ['mettler', 'schade', 'damage', 'bdw', 'export', 'demontage', 'sloperij']

# Woorden die zeggen dat de accu wél gekocht is (heft "accu" in ELLENDE niet op, wel informatief).
KOOPACCU = ['koopaccu', 'koop accu', 'incl accu', 'incl. accu', 'inclusief accu', 'accu in eigendom']

# Betrouwbaarheid per model, 1-10 (eigen inschatting op basis van ANWB/TÜV/ADAC-pech- en
# gebruikerservaringen; voor EV's weegt accuveroudering mee). (merk, modelwoord) -> (score, soort, toelichting)
# Dit is ook de toelatingslijst: een model dat hier niet staat, komt niet op de site.
MODELLEN = [
    # Elektrisch
    ('hyundai', 'ioniq', 9.0, None, 'Zeer betrouwbaar, zuinig, accu houdt goed stand'),
    ('kia', 'niro', 8.5, None, 'Betrouwbaar, ruim, 7 jaar fabrieksgarantie (check overdraagbaar)'),
    ('hyundai', 'kona', 8.5, None, 'Betrouwbaar, goede actieradius'),
    ('volkswagen', 'e-golf', 8.5, 'EV', 'Degelijk, geen bekende accuproblemen'),
    ('volkswagen', 'golf', 8.0, None, ''),
    ('volkswagen', 'e-up', 8.0, 'EV', 'Klein maar echte auto, simpel en betrouwbaar'),
    ('volkswagen', 'up', 8.0, None, ''),
    ('skoda', 'citigo', 8.0, None, 'Zelfde techniek als VW e-Up'),
    ('seat', 'mii', 8.0, None, 'Zelfde techniek als VW e-Up'),
    ('kia', 'soul', 7.5, None, 'Betrouwbaar, ruim instappen; 27 kWh-accu veroudert sneller'),
    ('opel', 'ampera-e', 8.0, 'EV', 'Grote accu; check terugroepactie accu uitgevoerd'),
    ('nissan', 'leaf', 7.0, 'EV', 'Simpele techniek; accu zonder koeling, check SoH (accustaat)'),
    ('bmw', 'i3', 6.5, None, 'Licht en sterk (carbon); onderhoud bij BMW duur'),
    ('renault', 'zoe', 6.5, 'EV', 'Alleen met koopaccu tonen; check laadsysteem'),
    ('dacia', 'spring', 6.0, 'EV', 'Eenvoudig, klein, laag vermogen'),
    ('fiat', '500e', 5.5, 'EV', 'Meestal Amerikaanse import; onderdelen lastig'),
    ('peugeot', 'e-208', 7.5, 'EV', ''),
    ('mercedes', 'b 250e', 5.5, 'EV', 'Tesla-aandrijving; reparaties duur'),
    ('mercedes-benz', 'b 250e', 5.5, 'EV', 'Tesla-aandrijving; reparaties duur'),
    ('ford', 'focus', 5.5, None, 'Weinig verkocht, onderdelen lastig'),
    ('tesla', 'model s', 5.0, 'EV', 'Prachtig, maar reparaties (scherm, aandrijving) zeer duur'),
    ('smart', 'forfour', 5.5, 'EV', 'Klein, 4 zitplaatsen'),
    ('renault', 'twingo', 6.5, 'EV', ''),
    ('mazda', 'mx-30', 7.5, 'EV', ''),
    # Plug-in hybride
    ('toyota', 'prius', 9.5, None, 'Toyota-hybride: de betrouwbaarste techniek die er is'),
    ('mitsubishi', 'outlander', 7.0, 'PHEV', 'Robuuste techniek, ruime SUV; verbruik hoog als je niet laadt'),
    ('chevrolet', 'volt', 7.5, 'PHEV', 'Aandrijving zeer betrouwbaar, accu houdt goed stand'),
    ('opel', 'ampera', 7.5, 'PHEV', 'Zelfde techniek als Chevrolet Volt'),
    ('ford', 'c-max', 7.0, None, 'Ford-hybridesysteem met e-CVT, degelijk'),
    ('kia', 'optima', 7.5, None, ''),
    ('hyundai', 'sonata', 7.0, None, ''),
    ('volkswagen', 'passat', 6.0, None, 'GTE: complexe techniek (DSG + accu)'),
    ('audi', 'a3', 6.0, None, 'e-tron: complexe techniek (S tronic + accu)'),
    ('bmw', '225xe', 6.0, 'PHEV', ''),
    ('bmw', '330e', 6.0, 'PHEV', ''),
    ('bmw', '2-serie', 6.0, None, ''),
    ('bmw', '3-serie', 6.0, None, ''),
    ('bmw', 'x5', 4.5, None, 'Onderhoud en reparaties zeer duur'),
    ('mini', 'countryman', 5.5, None, ''),
    ('volvo', 'v60', 4.5, None, 'D6 dieselhybride: bekend om storingen, dure reparaties'),
    ('volvo', 'xc90', 4.5, None, 'T8: complex, dure reparaties'),
    ('volvo', 'v90', 5.0, None, ''),
    ('volvo', 's90', 5.0, None, ''),
    ('mercedes', 'c 350', 5.0, None, ''),
    ('mercedes-benz', 'c 350', 5.0, None, ''),
    ('porsche', 'cayenne', 4.0, None, 'Reparaties extreem duur'),
    ('porsche', 'panamera', 4.0, None, 'Reparaties extreem duur'),
    ('peugeot', '3008', 6.0, None, ''),
    ('peugeot', '508', 5.0, None, ''),
]

# Echte automerken. Model onbekend maar merk hier = neutrale score; merk niet hier = weg
# (vangt de vele Chinese microcars en brommobielen af).
GANGBARE_MERKEN = {
    'alfa romeo', 'audi', 'bmw', 'byd', 'chevrolet', 'citroen', 'citroën', 'cupra', 'dacia', 'ds',
    'fiat', 'ford', 'honda', 'hyundai', 'jaguar', 'jeep', 'kia', 'land rover', 'lexus', 'lynk & co',
    'mazda', 'mercedes', 'mercedes-benz', 'mg', 'mini', 'mitsubishi', 'nissan', 'opel', 'peugeot',
    'polestar', 'porsche', 'renault', 'seat', 'skoda', 'smart', 'subaru', 'suzuki', 'tesla',
    'toyota', 'volkswagen', 'volvo',
}

# Merkvoorkeur van Annemarie (leeg = alle merken). Bijv. ['Toyota', 'Kia'] geeft die merken
# een bonus van MERK_BONUS punten; ze blijven ook met andere merken vergeleken.
MERK_VOORKEUR = []
MERK_BONUS = 5

# Woorden die een plug-in hybride verraden (nodig omdat "hybride" ook gewone hybrides bevat).
PHEV_WOORDEN = re.compile(
    r'plug[\s-]?in|\bphev\b|\bgte\b|e-tron|\benergi\b|\b\d{3}x?e\b|\bt8\b|\bd6\b|twin engine|'
    r'e-hybrid|\bvolt\b|\bampera\b|\brex\b|range extender|recharge|\b40e\b|\bi8\b|\bt6 awd\b',
    re.I)


def norm(s):
    return re.sub(r'\s+', ' ', (s or '').lower()).strip()


def bevat(tekst, woorden):
    """Woordgrens-match zodat 'ion' niet in 'navigation' en 'ami' niet in 'familie' matcht."""
    for w in woorden:
        if re.search(r'(?<![a-z0-9])' + re.escape(w) + r'(?![a-z0-9])', tekst):
            return w
    return None


def zoek_model(merk, tekst):
    merk = norm(merk)
    for m, model, score, soort, uitleg in MODELLEN:
        if m == merk and re.search(r'(?<![a-z0-9])' + re.escape(model) + r'(?![a-z0-9])', tekst):
            return score, soort, uitleg
    if merk in GANGBARE_MERKEN:
        return 5.5, None, 'Model niet in de lijst: neutrale betrouwbaarheid'
    return None  # onbekend merk: bijna altijd een microcar of brommobiel


# ---------------------------------------------------------------- AutoScout24

def autoscout24():
    uit = []
    # E = elektrisch, 2 = elektro/benzine, 3 = elektro/diesel
    for fuel in ['E', '2', '3']:
        for pagina in range(1, 21):
            url = (f'https://www.autoscout24.nl/lst?atype=C&cy=NL&fuel={fuel}&priceto={MAX_PRIJS}'
                   f'&pricefrom={MIN_PRIJS}&fregfrom={MIN_JAAR}&kmto={MAX_KM}&damaged_listing=exclude&sort=age&desc=1&page={pagina}')
            try:
                r = requests.get(url, headers=HEADERS, timeout=30)
                r.raise_for_status()
                tag = BeautifulSoup(r.text, 'html.parser').find('script', id='__NEXT_DATA__')
                pp = json.loads(tag.string)['props']['pageProps']
            except Exception as e:
                print(f'  AS24 fuel={fuel} p{pagina}: {e}')
                break
            for L in pp.get('listings', []):
                v, t = L.get('vehicle', {}), L.get('tracking', {})
                jaar = re.search(r'(\d{4})', t.get('firstRegistration') or '')
                imgs = L.get('images') or []
                uit.append({
                    'id': 'as24_' + L['id'],
                    'bron': 'AutoScout24',
                    'merk': v.get('make') or '',
                    'model': v.get('model') or '',
                    'titel': f"{v.get('make', '')} {v.get('model', '')} {v.get('modelVersionInput') or ''}".strip(),
                    'prijs': int(t.get('price') or L.get('price', {}).get('priceRaw') or 0),
                    'km': int(t['mileage']) if str(t.get('mileage', '')).isdigit() else None,
                    'jaar': int(jaar.group(1)) if jaar else None,
                    'brandstof': v.get('fuel') or '',
                    'plaats': (L.get('location') or {}).get('city', '').title(),
                    'verkoper': (L.get('seller') or {}).get('companyName') or 'Particulier',
                    'url': 'https://www.autoscout24.nl' + L.get('url', ''),
                    'foto': imgs[0].replace('/250x188.webp', '/480x360.webp') if imgs else '',
                })
            if pagina >= (pp.get('numberOfPages') or 1):
                break
            time.sleep(1)
    print(f'AutoScout24: {len(uit)} advertenties')
    return uit


# ---------------------------------------------------------------- Marktplaats

MERK_SLUG = {'volkswagen': 'Volkswagen', 'mercedes-benz': 'Mercedes-Benz', 'bmw': 'BMW',
             'mini': 'MINI', 'kia': 'Kia', 'ds': 'DS'}

def marktplaats():
    uit = []
    for brandstof in ['Elektrisch', 'Hybride ElektrischBenzine', 'Hybride ElektrischDiesel']:
        offset = 0
        while offset < 1000:
            url = ('https://www.marktplaats.nl/lrp/api/search?l1CategoryId=91&limit=100'
                   f'&offset={offset}&attributeRanges[]=PriceCents:{MIN_PRIJS * 100}:{MAX_PRIJS * 100}'
                   f'&attributeRanges[]=constructionYear:{MIN_JAAR}:null'
                   f'&attributesByKey[]=fuel:{brandstof}&viewOptions=list-view&sortBy=SORT_INDEX&sortOrder=DECREASING')
            try:
                r = requests.get(url, headers=HEADERS, timeout=30)
                r.raise_for_status()
                j = r.json()
            except Exception as e:
                print(f'  Marktplaats {brandstof} offset {offset}: {e}')
                break
            lijst = j.get('listings') or []
            for x in lijst:
                attr = {a['key']: a.get('value') for a in x.get('attributes', [])}
                prijs = (x.get('priceInfo') or {}).get('priceCents') or 0
                if (x.get('priceInfo') or {}).get('priceType') not in ('FIXED', 'MIN_BID', 'NEGOTIABLE', None):
                    continue
                vip = x.get('vipUrl') or ''
                delen = vip.split('/')          # /v/auto-s/<merk>/m123-titel
                slug = delen[3] if len(delen) > 3 else ''
                if slug in ('bestelauto-s', 'vrachtwagens', 'campers', 'oldtimers', 'aanhangers'):
                    continue
                merk = MERK_SLUG.get(slug, slug.replace('-', ' ').title())
                imgs = x.get('imageUrls') or []
                uit.append({
                    'id': 'mp_' + x['itemId'],
                    'bron': 'Marktplaats',
                    'merk': merk,
                    'model': attr.get('model') or '',
                    'titel': x.get('title', ''),
                    'beschrijving': x.get('categorySpecificDescription', ''),
                    'prijs': prijs // 100,
                    'km': int(attr['mileage']) if str(attr.get('mileage', '')).isdigit() else None,
                    'jaar': int(attr['constructionYear']) if str(attr.get('constructionYear', '')).isdigit() else None,
                    'brandstof': {'Elektrisch': 'Elektrisch'}.get(brandstof, 'Hybride'),
                    'plaats': (x.get('location') or {}).get('cityName', ''),
                    'verkoper': (x.get('sellerInformation') or {}).get('sellerName', ''),
                    'url': 'https://www.marktplaats.nl' + vip if vip.startswith('/') else vip,
                    'foto': ('https:' + imgs[0].replace('$_82', '$_84')) if imgs else '',
                })
            if len(lijst) < 100:
                break
            offset += 100
            time.sleep(1)
    print(f'Marktplaats: {len(uit)} advertenties')
    return uit


# ---------------------------------------------------------------- filter en score

def beoordeel(a):
    """Geeft de auto terug met score, of None als hij afvalt."""
    tekst = norm(f"{a['merk']} {a['model']} {a['titel']} {a.get('beschrijving', '')}")
    titel = norm(f"{a['merk']} {a['model']} {a['titel']}")
    if not (MIN_PRIJS <= a['prijs'] <= MAX_PRIJS):
        return None
    if not a['jaar'] or a['jaar'] < MIN_JAAR or a['km'] is None or a['km'] > MAX_KM:
        return None
    if bevat(titel, UITSLUITEN) or bevat(tekst, ELLENDE):
        return None
    if any(w in norm(a.get('verkoper')) for w in SCHADE_VERKOPERS):
        return None

    # Goedkope ZOE's hebben bijna altijd een huuraccu ("ex accu", "(ex)"): alleen met koopaccu.
    if re.search(r'\bzoe\b', titel) and not bevat(tekst, KOOPACCU):
        return None
    model = zoek_model(a['merk'], titel)
    if not model:
        return None
    betrouwbaar, soort, uitleg = model
    elektrisch = 'elektrisch' in norm(a['brandstof']) and '/' not in a['brandstof']
    if elektrisch:
        a['soort'] = 'Elektrisch'
    elif soort == 'PHEV' or PHEV_WOORDEN.search(titel):
        a['soort'] = 'Plug-in hybride'
    else:
        return None  # gewone hybride, niet stekkerbaar

    # Score 0-100: betrouwbaarheid 45%, bouwjaar 30%, kilometerstand 25%.
    jaar_s = max(0.0, min(10.0, (a['jaar'] - 2010) / 1.0))       # 2010 = 0, 2020+ = 10
    km_s = max(0.0, 10.0 - a['km'] / 25000)                      # 0 km = 10, 250.000 km = 0
    a['score'] = 4.5 * betrouwbaar + 3.0 * jaar_s + 2.5 * km_s
    a['betrouwbaarheid'] = betrouwbaar
    a['toelichting'] = uitleg

    if norm(a['merk']) in {norm(m) for m in MERK_VOORKEUR}:
        a['score'] += MERK_BONUS

    let_op = []
    soh = re.search(r'soh\D{0,3}(\d{2,3})\s*%', tekst)
    if soh:
        a['soh'] = int(soh.group(1))
        if a['soh'] < 80:
            a['score'] -= (80 - a['soh']) * 0.5
            let_op.append(f"Accu versleten (SoH {a['soh']}%)")
    if a['soort'] == 'Elektrisch':
        if not soh:
            let_op.append('Vraag accurapport (SoH)')
        if bevat(tekst, KOOPACCU):
            let_op.append('Koopaccu')
    if a['km'] > 180000:
        let_op.append('Hoge kilometerstand')
    a['let_op'] = let_op
    a['score'] = round(a['score'], 1)
    a.pop('beschrijving', None)
    return a


# Schadetaal in de volledige advertentietekst. Geen los "schade": veel dealers hebben een
# disclaimer met dat woord. "Verrijdbaar/movable" is typische taal van schadehandelaren.
DETAIL_SCHADE = [
    'schadeauto', 'schadevoertuig', 'schade aan', 'met schade', 'lichte schade', 'lichte voorschade',
    'voorschade', 'achterschade', 'zijschade', 'flankschade', 'hagelschade', 'waterschade',
    'brandschade', 'stormschade', 'accuschade', 'motorschade', 'aanrijding', 'ongeval', 'verrijdbaar',
    'movable', 'damaged', 'total loss', 'niet rijdend', 'niet rijdbaar', 'opknapper', 'defect',
    'airbag eruit', 'airbags eruit', 'airbag uit', 'gerepareerde schade', 'schadehistorie',
]
DETAIL_AANTAL = 40


def detail_tekst(a):
    r = requests.get(a['url'], headers=HEADERS, timeout=30)
    r.raise_for_status()
    soup = BeautifulSoup(r.text, 'html.parser')
    if a['bron'] == 'AutoScout24':
        L = json.loads(soup.find('script', id='__NEXT_DATA__').string)['props']['pageProps']['listingDetails']
        schade = (L.get('vehicle') or {}).get('condition', {}).get('damage') or {}
        if schade.get('isCurrentlyDamaged') or schade.get('hadAccident') or schade.get('accidentFree') is False:
            return 'schadeauto'
        return BeautifulSoup(L.get('description') or '', 'html.parser').get_text(' ')
    blok = soup.find(attrs={'data-collapsable': 'description'})
    return blok.get_text(' ') if blok else ''


def controleer_details(autos):
    """Leest de volledige advertentie van de beste kandidaten en gooit schadeauto's eruit."""
    goed = []
    for a in autos[:DETAIL_AANTAL]:
        try:
            woord = bevat(norm(detail_tekst(a)), DETAIL_SCHADE)
        except requests.HTTPError as e:
            woord = 'verkocht' if e.response.status_code in (404, 410) else None
        except Exception as e:
            print(f"  detail {a['id']}: {e}")
            woord = None
        if woord:
            print(f"  weg ({woord}): {a['titel'][:60]}")
        else:
            goed.append(a)
        time.sleep(0.7)
    return goed + autos[DETAIL_AANTAL:]


def ontdubbel(autos):
    """Zelfde auto op AutoScout24 en Marktplaats: houd de eerste."""
    gezien, uit = set(), []
    for a in autos:
        sleutel = (norm(a['merk']), a['jaar'], round(a['km'] / 1000), round(a['prijs'] / 100))
        if sleutel in gezien:
            continue
        gezien.add(sleutel)
        uit.append(a)
    return uit


def main():
    nu = datetime.now(TZ)
    ruw = autoscout24() + marktplaats()
    if not ruw:
        print('Geen enkele advertentie opgehaald, oude data blijft staan.')
        sys.exit(1)

    autos = ontdubbel([a for a in (beoordeel(a) for a in ruw) if a])
    autos.sort(key=lambda a: (-a['score'], a['prijs']))
    autos = controleer_details(autos)

    gezien = json.loads(GEZIEN.read_text('utf-8')) if GEZIEN.exists() else {}
    vandaag = nu.date().isoformat()
    eerste_dag = not gezien or min(gezien.values()) >= vandaag   # dan is alles "nieuw": geen label
    for a in autos:
        gezien.setdefault(a['id'], vandaag)
        a['eerst_gezien'] = gezien[a['id']]
        a['nieuw'] = gezien[a['id']] == vandaag and not eerste_dag
    # Alleen ids bewaren die nog online staan of korter dan 60 dagen geleden gezien zijn.
    actief = {a['id'] for a in autos}
    gezien = {k: v for k, v in gezien.items()
              if k in actief or (nu.date() - datetime.fromisoformat(v).date()).days < 60}

    DATA.parent.mkdir(exist_ok=True)
    DATA.write_text(json.dumps({
        'bijgewerkt': nu.strftime('%Y-%m-%d %H:%M'),
        'aantal_bekeken': len(ruw),
        'aantal': len(autos),
        'autos': autos[:DETAIL_AANTAL - 5],  # alleen auto's die de detailcontrole hebben gehad
    }, ensure_ascii=False, indent=1), 'utf-8')
    GEZIEN.write_text(json.dumps(gezien, indent=0, sort_keys=True), 'utf-8')

    print(f'{len(ruw)} bekeken, {len(autos)} passen. Top 5:')
    for a in autos[:5]:
        print(f"  {a['score']:5}  {a['titel'][:55]:55} {a['jaar']} {a['km']:>7} km  EUR {a['prijs']}  {a['bron']}")


if __name__ == '__main__':
    main()
