"""Auto voor Annemarie: elektrisch of plug-in hybride, max EUR 8.000, Nederland.

Haalt aanbod op van AutoScout24.nl en Marktplaats, filtert microcars, accuhuur,
schade, gewone (niet-plug-in) hybrides en auto's die korter zijn dan een Citroen C3 Pluriel
(3.934 mm) eruit, geeft elke auto een score op
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
# Zonder stekker gelden strengere grenzen: een benzinemotor met 200.000 km staat aan de vooravond
# van distributieriem, koppeling en ophanging, en onder EUR 3.000 is het een APK-gok. Een
# elektrische auto heeft die slijtagedelen niet, dus daar blijven de ruime grenzen staan.
MIN_JAAR_BRANDSTOF = 2015   # 2013 maakt er ook Auris, Civic, Jazz en i30 bij, maar wel oudere auto's
MAX_KM_BRANDSTOF = 150000
MIN_PRIJS_BRANDSTOF = 3000
# Niet kleiner dan de Citroen C3 Pluriel die Annemarie nu heeft: die is 3.934 mm lang (bron:
# Citroenet/angurten, 2004-2010). Alles wat korter is, valt af. Staat de lengte van een model niet
# in LENGTE, dan valt de auto niet af; dan weten we het simpelweg niet.
MIN_LENGTE = 3934
TZ = ZoneInfo('Europe/Amsterdam')
VERSIE = '1.4.0'       # ophogen bij elke release, zie docs/VERSIES.md

ROOT = Path(__file__).parent
DATA = ROOT / 'docs' / 'data.json'
GEZIEN = ROOT / 'docs' / 'gezien.json'

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                  '(KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36',
    'Accept-Language': 'nl-NL,nl;q=0.9',
}

# Microcars, brommobielen (ook Citroën Ami), quadricycles, Smarts en bestelbussen: nooit tonen.
UITSLUITEN = [
    'ami', 'smart', 'rocks', 'twizy', 'biro', 'estrima', 'aixam', 'ligier', 'microcar',
    'chatenet', 'microlino', 'tazzari', 'topolino', 'brommobiel', '45 km', '45km', 'bellier',
    'jdm', 'casalini', 'kewet', 'buddy', 'reva', 'think city', 'goupil', 'club car',
    'lpg', 'autogas', 'lpg-g3', 'g3',
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
# Advertenties waarin de genoemde prijs niet de hele prijs is: "ACTIE! BETAAL NU 50% 7950, DE REST
# LATER" staat voor 7.950 in de lijst terwijl de auto 16.000 kost. Altijd weg.
# Handelaren die meerdere auto's in een advertentie zetten ("4X TOYOTA AYGO"): de prijs en de
# kilometerstand horen dan bij geen enkele auto in het bijzonder.
PARTIJ = re.compile(r'^\s*\d{1,2}\s*x', re.I)

PRIJS_TRUC = re.compile(
    r'betaal\w*\s*(je\s*|u\s*)?(nu\s*)?(de\s*helft|\d{1,2}\s*%)|\d{1,2}\s*%\s*(aan|voor)?betal|'
    r'rest(erend)?\s*(bedrag|deel)|rest\s*(betaal|later|bij\s*aflevering|na\s*aflevering|in\s*termijnen)',
    re.I)

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
    # Benzine en gewone hybride. Alleen modellen met een bewezen reputatie; zie ZONDER_STEKKER.
    ('toyota', 'aygo', 9.0, None, 'Simpel en zuinig, er gaat vrijwel niets kapot'),
    ('toyota', 'yaris', 9.0, None, 'Toyota-betrouwbaarheid; de hybride is nog zuiniger'),
    ('toyota', 'auris', 8.5, None, 'Ruimer dan de Yaris, zelfde techniek'),
    ('honda', 'jazz', 8.5, None, 'Ruim, hoge instap, zeer betrouwbaar'),
    ('honda', 'civic', 8.0, None, ''),
    ('lexus', 'ct', 8.5, None, 'Prius-techniek in een nettere jas'),
    ('suzuki', 'swift', 8.0, None, 'Licht en eenvoudig'),
    ('kia', 'picanto', 8.0, None, 'Goedkoop in onderhoud, 7 jaar fabrieksgarantie'),
    ('kia', 'rio', 7.5, None, ''),
    ('kia', 'ceed', 7.5, None, ''),
    ('kia', "cee'd", 7.5, None, ''),
    ('hyundai', 'i10', 8.0, None, 'Zelfde techniek als de Kia Picanto'),
    ('hyundai', 'i20', 7.5, None, ''),
    ('hyundai', 'i30', 7.5, None, ''),
    ('mazda', '3', 8.0, None, 'Geen turbo, geen distributieriem: weinig dure verrassingen'),
    ('mazda', '2', 8.0, None, 'Geen turbo, geen distributieriem: weinig dure verrassingen'),
    ('skoda', 'fabia', 7.5, None, ''),
    ('volkswagen', 'polo', 7.5, None, ''),
    ('seat', 'ibiza', 7.0, None, 'Zelfde techniek als de VW Polo'),
    ('peugeot', '108', 8.0, None, 'Zelfde auto als de Toyota Aygo'),
    ('citroen', 'c1', 8.0, None, 'Zelfde auto als de Toyota Aygo'),
    ('citroën', 'c1', 8.0, None, 'Zelfde auto als de Toyota Aygo'),
]

# Modellen die ook zonder stekker mogen meedoen: modelwoord -> (pad op AutoScout24, liter per 100 km).
# Alleen wat hier staat, komt als benzine of gewone hybride op de site. Bewust niet: Renault, Fiat
# en Alfa met benzinemotor, de Opel 1.4 Turbo, de Ford 1.0 EcoBoost (koelvloeistof, distributieriem)
# en alles met een DSG- of CVT-automaat van voor 2015.
ZONDER_STEKKER = {
    'aygo': ('toyota/aygo', 4.8), 'yaris': ('toyota/yaris', 5.3), 'auris': ('toyota/auris', 6.0),
    'prius': ('toyota/prius', 4.5), 'jazz': ('honda/jazz', 5.6), 'civic': ('honda/civic', 6.2),
    'ct': ('lexus/ct', 4.6), 'swift': ('suzuki/swift', 5.2), 'picanto': ('kia/picanto', 5.0),
    'rio': ('kia/rio', 5.5), 'ceed': ('kia/ceed', 6.0), "cee'd": (None, 6.0),
    'i10': ('hyundai/i10', 5.0), 'i20': ('hyundai/i20', 5.5), 'i30': ('hyundai/i30', 6.2),
    '3': ('mazda/3', 6.0), '2': ('mazda/2', 5.2), 'fabia': ('skoda/fabia', 5.3),
    'polo': ('volkswagen/polo', 5.4), 'ibiza': ('seat/ibiza', 5.5), '108': ('peugeot/108', 4.8),
    'c1': ('citroen/c1', 4.8),
}
# Zuiniger als het een hybride is (dezelfde auto, andere aandrijving).
HYBRIDE_VERBRUIK = {'yaris': 4.2, 'auris': 4.5, 'jazz': 4.8, 'prius': 4.5, 'ct': 4.6}

# (merk, modelwoord) voor de zoekopdrachten per model op Marktplaats.
BENZINE_PAREN = []
for _merk, _model, *_rest in MODELLEN:
    if _model in ZONDER_STEKKER and _model not in {x[1] for x in BENZINE_PAREN}:
        BENZINE_PAREN.append((_merk, _model))

# Echte automerken. Model onbekend maar merk hier = neutrale score; merk niet hier = weg
# (vangt de vele Chinese microcars en brommobielen af).
GANGBARE_MERKEN = {
    'alfa romeo', 'audi', 'bmw', 'byd', 'chevrolet', 'citroen', 'citroën', 'cupra', 'dacia', 'ds',
    'fiat', 'ford', 'honda', 'hyundai', 'jaguar', 'jeep', 'kia', 'land rover', 'lexus', 'lynk & co',
    'mazda', 'mercedes', 'mercedes-benz', 'mg', 'mini', 'mitsubishi', 'nissan', 'opel', 'peugeot',
    'polestar', 'porsche', 'renault', 'seat', 'skoda', 'subaru', 'suzuki', 'tesla',
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
            return score, soort, uitleg, GEWICHT.get(model), model
    if merk in GANGBARE_MERKEN:
        return 5.5, None, 'Model niet in de lijst: neutrale betrouwbaarheid', None, None
    return None  # onbekend merk: bijna altijd een microcar of brommobiel


# ---------------------------------------------------------------- vaste lasten

# Gewicht leeg voertuig (kg, kentekenbewijs) per model, typische uitvoering. Bepaalt de wegenbelasting.
GEWICHT = {
    'ioniq': 1420, 'niro': 1600, 'kona': 1610, 'e-golf': 1510, 'golf': 1540, 'e-up': 1140, 'up': 1140,
    'citigo': 1160, 'mii': 1160, 'soul': 1490, 'ampera-e': 1625, 'leaf': 1450, 'i3': 1250, 'zoe': 1450,
    'spring': 970, '500e': 1265, 'e-208': 1455, 'b 250e': 1650, 'focus': 1645, 'model s': 2100,
    'twingo': 1110, 'mx-30': 1645, 'prius': 1450, 'outlander': 1810, 'volt': 1715,
    'ampera': 1715, 'c-max': 1720, 'optima': 1720, 'sonata': 1700, 'passat': 1700, 'a3': 1540,
    '225xe': 1660, '330e': 1660, '2-serie': 1660, '3-serie': 1660, 'x5': 2230, 'countryman': 1735,
    'v60': 1980, 'xc90': 2300, 'v90': 2000, 's90': 2000, 'c 350': 1780, 'cayenne': 2350,
    'panamera': 2170, '3008': 1900, '508': 1800,
}
GEWICHT.update({
    'aygo': 900, 'yaris': 1050, 'auris': 1250, 'jazz': 1100, 'civic': 1300, 'ct': 1400,
    'swift': 950, 'picanto': 900, 'rio': 1100, 'ceed': 1250, "cee'd": 1250, 'i10': 950,
    'i20': 1050, 'i30': 1250, '3': 1250, '2': 1050, 'fabia': 1050, 'polo': 1100, 'ibiza': 1100,
    '108': 900, 'c1': 900,
})
GEWICHT_ONBEKEND = {'Elektrisch': 1500, 'Plug-in hybride': 1700, 'Hybride': 1300, 'Benzine': 1200}

# Lengte in mm per model, typische uitvoering (5-deurs hatchback of sedan waar dat de gangbare is).
# Annemarie wil geen auto die kleiner is dan haar Citroen C3 Pluriel (3.934 mm), dus alles onder
# MIN_LENGTE valt af. Daardoor doen deze modellen niet meer mee: VW up/e-up, Skoda Citigo,
# Seat Mii, Dacia Spring, Fiat 500e, Renault Twingo, Toyota Aygo, Suzuki Swift, Kia Picanto,
# Hyundai i10, Peugeot 108 en Citroen C1. Ze staan er bewust nog in: zet MIN_LENGTE lager en ze
# komen terug.
LENGTE = {
    'ioniq': 4470, 'niro': 4355, 'kona': 4180, 'e-golf': 4270, 'golf': 4258, 'e-up': 3600,
    'up': 3540, 'citigo': 3597, 'mii': 3557, 'soul': 4140, 'ampera-e': 4166, 'leaf': 4445,
    'i3': 3999, 'zoe': 4084, 'spring': 3734, '500e': 3571, 'e-208': 4055, 'b 250e': 4359,
    'focus': 4358, 'model s': 4979, 'twingo': 3615, 'mx-30': 4395, 'prius': 4460,
    'outlander': 4695, 'volt': 4498, 'ampera': 4498, 'c-max': 4380, 'optima': 4855,
    'sonata': 4855, 'passat': 4767, 'a3': 4313, '225xe': 4342, '330e': 4633, '2-serie': 4342,
    '3-serie': 4633, 'x5': 4886, 'countryman': 4299, 'v60': 4628, 'xc90': 4950, 'v90': 4936,
    's90': 4963, 'c 350': 4686, 'cayenne': 4918, 'panamera': 5049, '3008': 4447, '508': 4750,
}
LENGTE.update({
    'aygo': 3465, 'yaris': 3945, 'auris': 4330, 'jazz': 3955, 'civic': 4300, 'ct': 4350,
    'swift': 3850, 'picanto': 3595, 'rio': 4045, 'ceed': 4310, "cee'd": 4310, 'i10': 3665,
    'i20': 4035, 'i30': 4300, '3': 4580, '2': 4060, 'fabia': 3992, 'polo': 3972, 'ibiza': 4061,
    '108': 3475, 'c1': 3466,
})


def te_klein(model):
    """Waar als we van dit model weten dat het korter is dan de C3 Pluriel."""
    lengte = LENGTE.get(model)
    return lengte is not None and lengte < MIN_LENGTE

# Wegenbelasting per kwartaal, provincie Utrecht, 2026, uit de rekenhulp van de Belastingdienst
# (opgehaald 12-10-2026). Klasse vanaf gewicht -> (benzine, diesel). Elektrisch = 70% van benzine
# (2026-2028); plug-in hybride betaalt sinds 2026 het volle tarief van zijn brandstof.
# Woont Annemarie in een andere provincie, dan scheelt dat tot ca. 10%.
MRB_UTRECHT = [
    (1, 33, 117), (651, 44, 143), (751, 54, 169), (851, 71, 202), (951, 93, 246),
    (1051, 121, 290), (1151, 148, 334), (1251, 175, 378), (1351, 203, 422), (1451, 230, 466),
    (1551, 257, 510), (1651, 285, 554), (1751, 312, 598), (1851, 339, 642), (1951, 367, 686),
    (2051, 394, 729), (2151, 422, 773), (2251, 449, 817), (2351, 476, 861), (2451, 504, 905),
]
PREMIUM_MERKEN = {'bmw', 'mercedes', 'mercedes-benz', 'audi', 'volvo', 'mini', 'lexus', 'jaguar', 'land rover'}
DURE_MERKEN = {'tesla', 'porsche'}


def wegenbelasting(gewicht, soort, diesel):
    """Wegenbelasting per maand in euro."""
    benzine, dieseltarief = next(t[1:] for t in reversed(MRB_UTRECHT) if gewicht >= t[0])
    if soort == 'Elektrisch':
        kwartaal = benzine * 0.7
    else:
        kwartaal = dieseltarief if diesel else benzine
    return round(kwartaal / 3)


BENZINEPRIJS = 2.10          # euro per liter aan de pomp
STROOMPRIJS = 0.28           # euro per kWh, thuis laden
KM_PER_JAAR = 12000
PHEV_BENZINEVERBRUIK = 7.0   # liter per 100 km zodra de accu leeg is
PHEV_DEEL_ELEKTRISCH = 0.5   # een plug-in rijdt ongeveer de helft van de kilometers op stroom


def brandstofkosten(a, model):
    """Benzine en stroom per maand, gerekend op KM_PER_JAAR kilometer per jaar."""
    km = KM_PER_JAAR / 12
    if a['soort'] == 'Elektrisch':
        return round(km * VERBRUIK.get(model, VERBRUIK_ONBEKEND) / 1000 * STROOMPRIJS)
    if a['soort'] == 'Plug-in hybride':
        stroom = km * PHEV_DEEL_ELEKTRISCH * VERBRUIK.get(model, VERBRUIK_ONBEKEND) / 1000 * STROOMPRIJS
        return round(stroom + km * (1 - PHEV_DEEL_ELEKTRISCH) * PHEV_BENZINEVERBRUIK / 100 * BENZINEPRIJS)
    liter = HYBRIDE_VERBRUIK.get(model) if a['soort'] == 'Hybride' else None
    if liter is None:
        liter = (ZONDER_STEKKER.get(model) or (None, 6.0))[1]
    return round(km * liter / 100 * BENZINEPRIJS)


def verzekering(gewicht, prijs, merk):
    """Grove inschatting WA + beperkt casco per maand, 10 schadevrije jaren, bestuurder 30+.
    Zwaardere auto = hogere WA-premie; beperkt casco groeit met de waarde; premiummerken zijn duurder
    om te repareren."""
    wa = 14 + 6 * max(0, gewicht - 1000) / 500
    bc = 5 + prijs / 1000
    factor = 1.5 if norm(merk) in DURE_MERKEN else 1.25 if norm(merk) in PREMIUM_MERKEN else 1.0
    return round((wa + bc) * factor)


# ---------------------------------------------------------------- AutoScout24

MAX_PAGINAS = 20        # brede zoekopdracht op brandstof (elektrisch, plug-in)
MAX_PAGINAS_MODEL = 4   # per model (benzine); gesorteerd op nieuwste, dus dit houdt de beste over


def as24_auto(L):
    v, t = L.get('vehicle', {}), L.get('tracking', {})
    jaar = re.search(r'(\d{4})', t.get('firstRegistration') or '')
    imgs = L.get('images') or []
    return {
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
    }


def as24_pagina(url):
    """Een zoekpagina: geeft de advertenties en het totale aantal pagina's."""
    r = requests.get(url, headers=HEADERS, timeout=30)
    r.raise_for_status()
    tag = BeautifulSoup(r.text, 'html.parser').find('script', id='__NEXT_DATA__')
    pp = json.loads(tag.string)['props']['pageProps']
    return [as24_auto(L) for L in pp.get('listings', [])], (pp.get('numberOfPages') or 1)


def as24_zoek(naam, basis, maxpaginas):
    uit = []
    for pagina in range(1, maxpaginas + 1):
        try:
            autos, paginas = as24_pagina(f'{basis}&page={pagina}')
        except Exception as e:
            print(f'  AS24 {naam} p{pagina}: {e}')
            break
        uit += autos
        if pagina >= paginas:
            break
        time.sleep(1)
    return uit


def autoscout24():
    """Elektrisch en plug-in: in een keer op brandstof. E = elektrisch, 2 = elektro/benzine,
    3 = elektro/diesel. Dat zijn kleine markten, dus de hele lijst past in een paar pagina's."""
    uit = []
    for fuel in ['E', '2', '3']:
        basis = (f'https://www.autoscout24.nl/lst?atype=C&cy=NL&fuel={fuel}&priceto={MAX_PRIJS}'
                 f'&pricefrom={MIN_PRIJS}&fregfrom={MIN_JAAR}&kmto={MAX_KM}'
                 f'&damaged_listing=exclude&sort=age&desc=1')
        uit += as24_zoek(f'fuel={fuel}', basis, MAX_PAGINAS)
    print(f'AutoScout24 stekker: {len(uit)} advertenties')
    return uit


def autoscout24_benzine():
    """Benzine per model. De hele benzinemarkt tot EUR 8.000 is te groot om te doorzoeken, maar
    alleen de modellen uit ZONDER_STEKKER komen er toch doorheen. Dus vragen we er meteen om."""
    uit = []
    for pad in sorted({pad for m, (pad, _) in ZONDER_STEKKER.items()
                       if pad and not te_klein(m)}):
        basis = (f'https://www.autoscout24.nl/lst/{pad}?atype=C&cy=NL&fuel=B&priceto={MAX_PRIJS}'
                 f'&pricefrom={MIN_PRIJS_BRANDSTOF}&fregfrom={MIN_JAAR_BRANDSTOF}'
                 f'&kmto={MAX_KM_BRANDSTOF}&damaged_listing=exclude&sort=age&desc=1')
        gevonden = as24_zoek(pad, basis, MAX_PAGINAS_MODEL)
        if not gevonden:
            print(f'  let op: {pad} gaf niets terug')
        uit += gevonden
        time.sleep(1)
    print(f'AutoScout24 benzine: {len(uit)} advertenties')
    return uit


# ---------------------------------------------------------------- Marktplaats

MERK_SLUG = {'volkswagen': 'Volkswagen', 'mercedes-benz': 'Mercedes-Benz', 'bmw': 'BMW',
             'mini': 'MINI', 'kia': 'Kia', 'ds': 'DS'}
NIET_PERSONENAUTO = ('bestelauto-s', 'vrachtwagens', 'campers', 'oldtimers', 'aanhangers')


def mp_auto(x, brandstof):
    attr = {a['key']: a.get('value') for a in x.get('attributes', [])}
    if (x.get('priceInfo') or {}).get('priceType') not in ('FIXED', 'MIN_BID', 'NEGOTIABLE', None):
        return None
    vip = x.get('vipUrl') or ''
    delen = vip.split('/')              # /v/auto-s/<merk>/m123-titel
    slug = delen[3] if len(delen) > 3 else ''
    if slug in NIET_PERSONENAUTO:
        return None
    imgs = x.get('imageUrls') or []
    return {
        'id': 'mp_' + x['itemId'],
        'bron': 'Marktplaats',
        'merk': MERK_SLUG.get(slug, slug.replace('-', ' ').title()),
        'model': attr.get('model') or '',
        'titel': x.get('title', ''),
        'beschrijving': x.get('categorySpecificDescription', ''),
        'prijs': ((x.get('priceInfo') or {}).get('priceCents') or 0) // 100,
        'km': int(attr['mileage']) if str(attr.get('mileage', '')).isdigit() else None,
        'jaar': int(attr['constructionYear']) if str(attr.get('constructionYear', '')).isdigit() else None,
        'brandstof': brandstof,
        'plaats': (x.get('location') or {}).get('cityName', ''),
        'verkoper': (x.get('sellerInformation') or {}).get('sellerName', ''),
        'url': 'https://www.marktplaats.nl' + vip if vip.startswith('/') else vip,
        'foto': ('https:' + imgs[0].replace('$_82', '$_84')) if imgs else '',
    }


def mp_zoek(naam, basis, brandstof, maxoffset):
    uit, offset = [], 0
    while offset < maxoffset:
        try:
            r = requests.get(f'{basis}&offset={offset}', headers=HEADERS, timeout=30)
            r.raise_for_status()
            lijst = r.json().get('listings') or []
        except Exception as e:
            print(f'  Marktplaats {naam} offset {offset}: {e}')
            break
        uit += [a for a in (mp_auto(x, brandstof) for x in lijst) if a]
        if len(lijst) < 100:
            break
        offset += 100
        time.sleep(1)
    return uit


def marktplaats():
    """Elektrisch en plug-in: in een keer op brandstof."""
    uit = []
    for soort in ['Elektrisch', 'Hybride ElektrischBenzine', 'Hybride ElektrischDiesel']:
        basis = ('https://www.marktplaats.nl/lrp/api/search?l1CategoryId=91&limit=100'
                 f'&attributeRanges[]=PriceCents:{MIN_PRIJS * 100}:{MAX_PRIJS * 100}'
                 f'&attributeRanges[]=constructionYear:{MIN_JAAR}:null'
                 f'&attributesByKey[]=fuel:{soort}&viewOptions=list-view'
                 '&sortBy=SORT_INDEX&sortOrder=DECREASING')
        uit += mp_zoek(soort, basis, 'Elektrisch' if soort == 'Elektrisch' else 'Hybride', 1000)
    print(f'Marktplaats stekker: {len(uit)} advertenties')
    return uit


def marktplaats_benzine():
    """Benzine per model, om dezelfde reden als bij AutoScout24."""
    uit = []
    for merk, model in BENZINE_PAREN:
        if te_klein(model):
            continue
        zoekterm = requests.utils.quote(f'{merk} {model}')
        basis = ('https://www.marktplaats.nl/lrp/api/search?l1CategoryId=91&limit=100'
                 f'&query={zoekterm}'
                 f'&attributeRanges[]=PriceCents:{MIN_PRIJS_BRANDSTOF * 100}:{MAX_PRIJS * 100}'
                 f'&attributeRanges[]=constructionYear:{MIN_JAAR_BRANDSTOF}:null'
                 f'&attributeRanges[]=mileage:null:{MAX_KM_BRANDSTOF}'
                 '&attributesByKey[]=fuel:Benzine&viewOptions=list-view'
                 '&sortBy=SORT_INDEX&sortOrder=DECREASING')
        uit += mp_zoek(f'{merk} {model}', basis, 'Benzine', 200)
        time.sleep(1)
    print(f'Marktplaats benzine: {len(uit)} advertenties')
    return uit


# ---------------------------------------------------------------- bereik

# Netto bruikbare accucapaciteit (kWh) per model, per uitvoering van klein naar groot, met het
# eerste bouwjaar waarin die uitvoering te koop was. De uitvoering wordt gekozen op de kWh in de
# titel, maar alleen als die in het bouwjaar van de advertentie al bestond; staat er geen maat in
# de titel, dan de kleinste, want in dit prijssegment is dat bijna altijd de juiste.
ACCU = {
    'ioniq': [(28, 2016), (38, 2020)],
    'niro': [(39, 2019), (64, 2019)],
    'kona': [(39, 2018), (64, 2018)],
    'e-golf': [(21, 2014), (32, 2017)],
    'golf': [(21, 2014), (32, 2017)],
    'e-up': [(16, 2013), (32, 2020)],
    'up': [(16, 2013), (32, 2020)],
    'citigo': [(32, 2020)],
    'mii': [(32, 2020)],
    'soul': [(27, 2014), (30, 2018), (39, 2020), (64, 2020)],
    'ampera-e': [(60, 2017)],
    'leaf': [(22, 2011), (28, 2016), (39, 2018), (59, 2019)],
    'i3': [(19, 2013), (27, 2016), (38, 2019)],
    'zoe': [(22, 2012), (41, 2017), (52, 2020)],
    'spring': [(27, 2021)],
    '500e': [(24, 2013), (37, 2021)],
    'e-208': [(45, 2019)],
    'b 250e': [(28, 2014)],
    'focus': [(23, 2012), (33, 2017)],
    'model s': [(85, 2012)],
    'twingo': [(22, 2020)],
    'mx-30': [(30, 2020)],
}
ACCU_ONBEKEND = 24

# Werkelijk verbruik in de zomer (Wh/km), gemengd stad en buitenweg.
VERBRUIK = {
    'ioniq': 135, 'niro': 165, 'kona': 160, 'e-golf': 155, 'golf': 155, 'e-up': 140, 'up': 140,
    'citigo': 140, 'mii': 140, 'soul': 175, 'ampera-e': 175, 'leaf': 165, 'i3': 145, 'zoe': 165,
    'spring': 145, '500e': 165, 'e-208': 160, 'b 250e': 200, 'focus': 180, 'model s': 200,
    'twingo': 150, 'mx-30': 170,
}
VERBRUIK_ONBEKEND = 170
WINTERFACTOR = 1.35   # kou plus verwarming kosten ruwweg een kwart van het bereik

# Accuslijtage per jaar in procenten, voor als de advertentie geen SoH noemt. De Leaf en de
# 27 kWh-Soul hebben geen accukoeling en lopen sneller terug.
SLIJTAGE = {'leaf': 1.9, 'soul': 1.7, '500e': 1.5}
SLIJTAGE_STANDAARD = 1.2
SOH_MINIMUM = 65

# Elektrisch bereik van een volle accu bij een plug-in hybride (km, zomer, accu met slijtage).
# De i3 REx staat hier ook in: die heeft de gewone i3-accu plus een kleine benzinemotor.
PHEV_BEREIK = {
    'prius': 20, 'outlander': 35, 'volt': 55, 'ampera': 55, 'i3': 90, 'c-max': 30, 'optima': 40,
    'sonata': 40, 'passat': 40, 'a3': 35, '225xe': 30, '330e': 30, '2-serie': 30, '3-serie': 30,
    'x5': 25, 'countryman': 30, 'v60': 30, 'xc90': 35, 'v90': 35, 's90': 35, 'c 350': 25,
    'cayenne': 25, 'panamera': 30, '3008': 40, '508': 40,
}
PHEV_BEREIK_ONBEKEND = 30

NU_JAAR = datetime.now(TZ).year


def accu_kwh(model, titel, jaar=0):
    """Netto accucapaciteit: de uitvoering die het dichtst bij de kWh in de titel ligt, en die in
    het bouwjaar al leverbaar was."""
    varianten = ACCU.get(model) or [(ACCU_ONBEKEND, 0)]
    leverbaar = [kwh for kwh, vanaf in varianten if not jaar or jaar >= vanaf]
    if not leverbaar:
        leverbaar = [varianten[0][0]]       # ouder dan het model zelf: de kleinste uitvoering
    uit_titel = re.search(r'(\d{2}(?:[.,]\d)?)\s*kwh', titel)
    if not uit_titel:
        return leverbaar[0]
    genoemd = float(uit_titel.group(1).replace(',', '.'))
    beste = min((kwh for kwh, _ in varianten), key=lambda k: abs(k - genoemd))
    # Advertenties schrijven ook het vermogen als "83kwh". Ligt het genoemde getal nergens in de
    # buurt van een bestaande uitvoering, dan is het geen accumaat.
    if abs(beste - genoemd) > 0.25 * beste:
        return leverbaar[0]
    # Een uitvoering die er in dat bouwjaar nog niet was ("ZOE uit 2013 met 41 kWh") kan niet
    # kloppen; dan de grootste accu die er toen wel in zat.
    return beste if beste in leverbaar else max(leverbaar)


def accustaat(model, jaar, soh):
    """SoH in procenten, en of dat een schatting is. Uit de advertentie als die het noemt."""
    if soh:
        return soh, False
    per_jaar = SLIJTAGE.get(model, SLIJTAGE_STANDAARD)
    return max(SOH_MINIMUM, round(100 - per_jaar * max(0, NU_JAAR - jaar))), True


def zet_bereik(a, model):
    """Zet de bereikvelden op de auto en geeft een cijfer 1-10 voor de score."""
    if a['soort'] in ('Benzine', 'Hybride'):
        # Een tank is genoeg voor een dag rijden en overal bij te vullen. Geen 10 van 10: tanken is
        # duurder dan thuis laden, en dat verschil zit in de kosten, niet hier.
        a['bereik_zomer'] = 800 if a['soort'] == 'Hybride' else 600
        a['bereik_winter'] = a['bereik_zomer']
        return 8.0
    if a['soort'] == 'Plug-in hybride':
        zomer = PHEV_BEREIK.get(model, PHEV_BEREIK_ONBEKEND)
        a['bereik_zomer'] = zomer
        a['bereik_winter'] = round(zomer / WINTERFACTOR / 5) * 5
        # Met de benzinemotor erbij kom je overal: bodem van 5, het elektrische deel doet de rest.
        return min(10.0, 5.0 + a['bereik_winter'] / 10)
    kwh = accu_kwh(model, norm(f"{a['merk']} {a['model']} {a['titel']}"), a['jaar'])
    soh, geschat = accustaat(model, a['jaar'], a.get('soh'))
    zomer = kwh * (soh / 100) * 1000 / VERBRUIK.get(model, VERBRUIK_ONBEKEND)
    a['accu_kwh'] = kwh
    a['soh_schatting'] = soh if geschat else None
    a['bereik_zomer'] = round(zomer / 5) * 5
    a['bereik_winter'] = round(zomer / WINTERFACTOR / 5) * 5
    # 50 km winterbereik telt als 0, 200 km als 10.
    return max(0.0, min(10.0, (a['bereik_winter'] - 50) / 15))


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
    if bevat(titel, ['verkocht', 'gereserveerd', 'sold', 'reserved']):
        return None
    if PARTIJ.search(a['titel']):
        return None  # meerdere auto's in een advertentie
    if PRIJS_TRUC.search(tekst):
        return None  # de genoemde prijs is maar een deel van de prijs
    if any(w in norm(a.get('verkoper')) for w in SCHADE_VERKOPERS):
        return None

    # Goedkope ZOE's hebben bijna altijd een huuraccu ("ex accu", "(ex)"): alleen met koopaccu.
    if re.search(r'\bzoe\b', titel) and not bevat(tekst, KOOPACCU):
        return None
    model = zoek_model(a['merk'], titel)
    if not model:
        return None
    betrouwbaar, soort, uitleg, gewicht, modelwoord = model
    if te_klein(modelwoord):
        return None  # kleiner dan de Citroen C3 Pluriel van Annemarie
    a['lengte'] = LENGTE.get(modelwoord)
    elektrisch = 'elektrisch' in norm(a['brandstof']) and '/' not in a['brandstof']
    if elektrisch:
        a['soort'] = 'Elektrisch'
    elif soort == 'PHEV' or PHEV_WOORDEN.search(titel):
        a['soort'] = 'Plug-in hybride'
    elif modelwoord in ZONDER_STEKKER:
        brandstof = norm(a['brandstof'])
        if 'hybride' in brandstof or 'elektro' in brandstof:
            a['soort'] = 'Hybride'
        elif 'benzine' in brandstof:
            a['soort'] = 'Benzine'
        else:
            return None  # diesel, lpg of onbekend
        if (a['jaar'] < MIN_JAAR_BRANDSTOF or a['km'] > MAX_KM_BRANDSTOF
                or a['prijs'] < MIN_PRIJS_BRANDSTOF):
            return None
    else:
        return None  # model doet niet mee zonder stekker

    # Totale kosten per maand: wegenbelasting, verzekering en brandstof of stroom.
    a['gewicht'] = gewicht or GEWICHT_ONBEKEND[a['soort']]
    diesel = 'diesel' in norm(a['brandstof']) or bool(re.search(r'\bd6\b', titel))
    a['mrb'] = wegenbelasting(a['gewicht'], a['soort'], diesel)
    a['verzekering'] = verzekering(a['gewicht'], a['prijs'], a['merk'])
    a['brandstofkosten'] = brandstofkosten(a, modelwoord)
    a['totale_kosten'] = a['mrb'] + a['verzekering'] + a['brandstofkosten']

    # Accustaat uit de advertentie: nodig voor het bereik en voor de score.
    gemeld = re.search(r'soh\D{0,3}(\d{2,3})\s*%', tekst)
    if gemeld:
        a['soh'] = int(gemeld.group(1))
    bereik_s = zet_bereik(a, modelwoord)

    # Score 0-100: betrouwbaarheid 35%, bereik 20%, bouwjaar 18%, kilometerstand 17%, lasten 10%.
    jaar_s = max(0.0, min(10.0, (a['jaar'] - 2010) / 1.0))       # 2010 = 0, 2020+ = 10
    km_s = max(0.0, 10.0 - a['km'] / 25000)                      # 0 km = 10, 250.000 km = 0
    kosten_s = max(0.0, min(10.0, (300 - a['totale_kosten']) / 20))   # <= 100/mnd = 10, >= 300/mnd = 0
    a['score'] = (3.5 * betrouwbaar + 2.0 * bereik_s + 1.8 * jaar_s + 1.7 * km_s + 1.0 * kosten_s)
    # Opbouw van de score, voor de uitleg bij de score op de website.
    a['punten'] = {'betrouwbaarheid': round(3.5 * betrouwbaar, 1), 'bereik': round(2.0 * bereik_s, 1),
                   'bouwjaar': round(1.8 * jaar_s, 1), 'km': round(1.7 * km_s, 1),
                   'kosten': round(1.0 * kosten_s, 1)}
    a['betrouwbaarheid'] = betrouwbaar
    a['toelichting'] = uitleg

    if norm(a['merk']) in {norm(m) for m in MERK_VOORKEUR}:
        a['score'] += MERK_BONUS
        a['punten']['merk'] = MERK_BONUS

    let_op = []
    if a.get('soh') and a['soh'] < 80:
        a['score'] -= (80 - a['soh']) * 0.5
        a['punten']['accu'] = -round((80 - a['soh']) * 0.5, 1)
        let_op.append(f"Accu versleten (SoH {a['soh']}%)")
    if a['soort'] == 'Elektrisch':
        if a['bereik_winter'] < 80:
            let_op.append(f"Klein winterbereik (± {a['bereik_winter']} km)")
        if not a.get('soh'):
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
DETAIL_AANTAL = 100
PER_SOORT = 25        # hoeveel kandidaten per soort de detailcontrole in gaan en op de site komen


def beste_per_soort(autos, per_soort=PER_SOORT):
    """Per soort de beste kandidaten. Zonder dit verdringt een soort met veel jong aanbod
    (benzine) alle andere, en is er op de site geen elektrische auto meer te zien."""
    geteld, uit = {}, []
    for a in autos:                       # al op score gesorteerd
        if geteld.get(a['soort'], 0) < per_soort:
            geteld[a['soort']] = geteld.get(a['soort'], 0) + 1
            uit.append(a)
    return uit


def detail_tekst(a):
    r = requests.get(a['url'], headers=HEADERS, timeout=30)
    r.raise_for_status()
    soup = BeautifulSoup(r.text, 'html.parser')
    if a['bron'] == 'AutoScout24':
        L = json.loads(soup.find('script', id='__NEXT_DATA__').string)['props']['pageProps']['listingDetails']
        if str(L.get('status', 'Active')).lower() != 'active':
            return 'verkocht'
        schade = (L.get('vehicle') or {}).get('condition', {}).get('damage') or {}
        if schade.get('isCurrentlyDamaged') or schade.get('hadAccident') or schade.get('accidentFree') is False:
            return 'schadeauto'
        return BeautifulSoup(L.get('description') or '', 'html.parser').get_text(' ')
    # Marktplaats: verkoper heeft de auto op gereserveerd/verkocht gezet.
    if re.search(r'"is(?:Reserved|Sold)":\s*true', r.text):
        return 'verkocht'
    blok = soup.find(attrs={'data-collapsable': 'description'})
    return blok.get_text(' ') if blok else ''


def controleer_details(autos):
    """Leest de volledige advertentie van de beste kandidaten en gooit schadeauto's eruit."""
    goed = []
    for a in autos[:DETAIL_AANTAL]:
        try:
            tekst = detail_tekst(a)
            woord = 'verkocht' if tekst == 'verkocht' else bevat(norm(tekst), DETAIL_SCHADE)
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
    ruw = autoscout24() + marktplaats() + autoscout24_benzine() + marktplaats_benzine()
    if not ruw:
        print('Geen enkele advertentie opgehaald, oude data blijft staan.')
        sys.exit(1)

    autos = ontdubbel([a for a in (beoordeel(a) for a in ruw) if a])
    autos.sort(key=lambda a: (-a['score'], a['prijs']))
    passen = len(autos)
    autos = controleer_details(beste_per_soort(autos))

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
        'versie': VERSIE,
        'min_lengte': MIN_LENGTE,
        'aantal_bekeken': len(ruw),
        'aantal': passen,
        'autos': autos,
    }, ensure_ascii=False, indent=1), 'utf-8')
    GEZIEN.write_text(json.dumps(gezien, indent=0, sort_keys=True), 'utf-8')

    per = {}
    for a in autos:
        per[a['soort']] = per.get(a['soort'], 0) + 1
    print(f'{len(ruw)} bekeken, {passen} passen, {len(autos)} op de site: {per}. Top 5:')
    for a in autos[:5]:
        print(f"  {a['score']:5}  {a['titel'][:55]:55} {a['jaar']} {a['km']:>7} km  EUR {a['prijs']}  {a['bron']}")


if __name__ == '__main__':
    main()
