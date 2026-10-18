"""Zet docs/BACKLOG.md en docs/VERSIES.md in de Google Sheet (tabs Backlog en Versies).

De md-bestanden zijn de bron; de sheet wordt elke keer volledig overschreven. Draait vanzelf
via GitHub Actions bij een push die docs/ wijzigt (.github/workflows/sync-sheet.yml).

Inloggen met een service-account (moet editor zijn op de sheet):
  GOOGLE_SA_JSON  = de key als JSON-tekst (GitHub-secret), of
  GOOGLE_SA_FILE  = pad naar het key-bestand (lokaal).
Lokaal: GOOGLE_SA_FILE=C:/Users/dell/Downloads/yt-comment-bot-494117-20ed92f4f3dd.json python tools/sync_sheet.py
"""
import json
import os
import re
from datetime import datetime, timezone
from pathlib import Path

from google.oauth2 import service_account
from googleapiclient.discovery import build

SHEET_ID = '1R0dGSir9Tyh0SPfiEnYhB8ycrnz9xlUN_C9h40wtCqY'
MAP = Path(__file__).resolve().parent.parent
BACKLOG = MAP / 'docs' / 'BACKLOG.md'
VERSIES = MAP / 'docs' / 'VERSIES.md'

# Kopje in BACKLOG.md -> status in de sheet
STATUS = {'Nu': 'Nu', 'In test': 'Test', 'Volgende': 'Volgende', 'Later': 'Later', 'Nee-lijst': 'Nee', 'Af': 'Af'}


def kaal(t):
    """Markdown-opmaak weghalen: **vet**, *schuin*, `code`, [tekst](link)."""
    t = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', t)
    t = re.sub(r'\*\*(.+?)\*\*', r'\1', t)
    t = re.sub(r'(?<!\w)\*(.+?)\*(?!\w)', r'\1', t)
    return t.replace('`', '').strip()


def cellen(regel):
    return [kaal(c) for c in regel.strip().strip('|').split('|')]


def lees_backlog():
    rijen = [['Status', '#', 'Item', 'Af als… / datum']]
    status = None
    for regel in BACKLOG.read_text(encoding='utf-8').splitlines():
        if regel.startswith('## '):
            kop = regel[3:].split('(')[0].strip()
            status = STATUS.get(kop)
            continue
        if not status:
            continue
        if regel.startswith('|'):
            c = cellen(regel)
            if c[0] in ('#', '') or set(c[0]) <= set('-: '):
                continue  # kopregel of scheidingsregel van de tabel
            nummer = '' if c[0] in ('—', '-') else c[0]
            rijen.append([status, nummer, c[1] if len(c) > 1 else '', c[2] if len(c) > 2 else ''])
        elif regel.startswith('- '):
            rijen.append([status, '', kaal(regel[2:]), ''])
        elif status == 'Nee' and regel.strip():
            for punt in regel.split('·'):
                rijen.append([status, '', kaal(punt), ''])
    return rijen


def lees_versies():
    rijen = [['Versie', 'Datum', 'Wijziging']]
    versie = datum = None
    for regel in VERSIES.read_text(encoding='utf-8').splitlines():
        m = re.match(r'## (\d+\.\d+\.\d+) — (.+)', regel)
        if m:
            versie, datum = m.group(1), m.group(2).strip()
            continue
        if regel.startswith('## '):
            versie = None  # andere sectie, bv. Plannen
            continue
        if versie and (regel.startswith('- ') or (regel.strip() and not regel.startswith('#'))):
            rijen.append([versie, datum, kaal(regel[2:] if regel.startswith('- ') else regel)])
    return rijen


def diensten():
    ruw = os.environ.get('GOOGLE_SA_JSON')
    info = json.loads(ruw) if ruw else json.loads(Path(os.environ['GOOGLE_SA_FILE']).read_text(encoding='utf-8'))
    creds = service_account.Credentials.from_service_account_info(
        info, scopes=['https://www.googleapis.com/auth/spreadsheets'])
    return build('sheets', 'v4', credentials=creds, cache_discovery=False).spreadsheets()


def zorg_voor_tabs(sheets, namen):
    meta = sheets.get(spreadsheetId=SHEET_ID).execute()
    bestaand = {s['properties']['title']: s['properties']['sheetId'] for s in meta['sheets']}
    verzoeken = [{'addSheet': {'properties': {'title': n, 'gridProperties': {'frozenRowCount': 1}}}}
                 for n in namen if n not in bestaand]
    if verzoeken:
        sheets.batchUpdate(spreadsheetId=SHEET_ID, body={'requests': verzoeken}).execute()
        meta = sheets.get(spreadsheetId=SHEET_ID).execute()
        bestaand = {s['properties']['title']: s['properties']['sheetId'] for s in meta['sheets']}
    # Standaardtab (Blad1/Sheet1) weg zodra onze tabs er zijn.
    weg = [{'deleteSheet': {'sheetId': i}} for t, i in bestaand.items() if t not in namen]
    if weg:
        sheets.batchUpdate(spreadsheetId=SHEET_ID, body={'requests': weg}).execute()
    return {n: bestaand[n] for n in namen}


def kleur(hexkleur):
    h = hexkleur.lstrip('#')
    return {k: int(h[i:i + 2], 16) / 255 for k, i in (('red', 0), ('green', 2), ('blue', 4))}


# Zelfde groen als de app; per status een eigen tint (cel) en een lichte rijkleur.
GROEN = '#0f766e'
STATUSKLEUR = {          # (statuscel, tekst, hele rij)
    'Nu':       ('#fcd34d', '#78350f', '#fffbeb'),
    'Test':     ('#ddd6fe', '#4c1d95', None),
    'Volgende': ('#bfdbfe', '#1e3a8a', None),
    'Later':    ('#e2e8f0', '#334155', None),
    'Nee':      ('#fecaca', '#7f1d1d', None),
    'Af':       ('#bbf7d0', '#14532d', None),
}
LIJN = {'style': 'SOLID', 'width': 1, 'colorStyle': {'rgbColor': kleur('#e2e8f0')}}


def bereik(tab_id, r0, r1, c0=None, c1=None):
    b = {'sheetId': tab_id, 'startRowIndex': r0, 'endRowIndex': r1}
    if c0 is not None:
        b.update(startColumnIndex=c0, endColumnIndex=c1)
    return b


def cel(tab_id, r0, r1, c0, c1, fmt, velden):
    return {'repeatCell': {'range': bereik(tab_id, r0, r1, c0, c1),
                           'cell': {'userEnteredFormat': fmt}, 'fields': f'userEnteredFormat({velden})'}}


def schrijf(sheets, tab, rijen, tab_id, breedtes, extra, tabkleur):
    """Schrijf de rijen en maak de tab op. `extra` = opmaakverzoeken voor de datarijen."""
    n_kol = len(breedtes)
    n_data = len(rijen) - 2           # zonder lege regel + stempel
    stempelrij = len(rijen) - 1
    # Alles leeg: oude opmaak, randen en samenvoegingen (de stempel verschuift steeds).
    sheets.batchUpdate(spreadsheetId=SHEET_ID, body={'requests': [
        {'unmergeCells': {'range': {'sheetId': tab_id}}},
        {'repeatCell': {'range': {'sheetId': tab_id}, 'cell': {}, 'fields': 'userEnteredFormat'}},
    ]}).execute()
    sheets.values().clear(spreadsheetId=SHEET_ID, range=tab).execute()
    sheets.values().update(spreadsheetId=SHEET_ID, range=f'{tab}!A1',
                           valueInputOption='RAW', body={'values': rijen}).execute()
    basis = {'wrapStrategy': 'WRAP', 'verticalAlignment': 'TOP',
             'padding': {'top': 6, 'bottom': 6, 'left': 8, 'right': 8},
             'textFormat': {'fontFamily': 'Roboto', 'fontSize': 10,
                            'foregroundColorStyle': {'rgbColor': kleur('#1c2421')}}}
    opmaak = [
        {'updateSheetProperties': {'properties': {'sheetId': tab_id, 'tabColorStyle': {'rgbColor': kleur(tabkleur)},
                                                  'gridProperties': {'hideGridlines': True, 'frozenRowCount': 1}},
                                   'fields': 'tabColorStyle,gridProperties(hideGridlines,frozenRowCount)'}},
        cel(tab_id, 0, n_data, 0, n_kol, basis, 'wrapStrategy,verticalAlignment,padding,textFormat'),
        # Kopregel: groen met witte vette tekst.
        cel(tab_id, 0, 1, 0, n_kol, {
            'backgroundColorStyle': {'rgbColor': kleur(GROEN)}, 'verticalAlignment': 'MIDDLE',
            'padding': {'top': 8, 'bottom': 8, 'left': 8, 'right': 8},
            'textFormat': {'fontFamily': 'Roboto', 'fontSize': 11, 'bold': True,
                           'foregroundColorStyle': {'rgbColor': kleur('#ffffff')}}},
            'backgroundColorStyle,verticalAlignment,padding,textFormat'),
        # Dunne scheidingslijnen tussen de datarijen.
        {'updateBorders': {'range': bereik(tab_id, 1, n_data, 0, n_kol), 'innerHorizontal': LIJN, 'bottom': LIJN}},
    ] + extra + [
        # Stempelregel: klein, grijs, schuin, over A-C.
        {'mergeCells': {'range': bereik(tab_id, stempelrij, stempelrij + 1, 0, 3), 'mergeType': 'MERGE_ALL'}},
        cel(tab_id, stempelrij, stempelrij + 1, 0, 3, {
            'padding': {'top': 4, 'bottom': 4, 'left': 8, 'right': 8},
            'textFormat': {'fontFamily': 'Roboto', 'fontSize': 9, 'italic': True,
                           'foregroundColorStyle': {'rgbColor': kleur('#64748b')}}}, 'padding,textFormat'),
    ] + [
        {'updateDimensionProperties': {'range': {'sheetId': tab_id, 'dimension': 'COLUMNS',
                                                 'startIndex': i, 'endIndex': i + 1},
                                       'properties': {'pixelSize': b}, 'fields': 'pixelSize'}}
        for i, b in enumerate(breedtes)
    ] + [{'autoResizeDimensions': {'dimensions': {'sheetId': tab_id, 'dimension': 'ROWS',
                                                   'startIndex': 0, 'endIndex': len(rijen)}}}]
    sheets.batchUpdate(spreadsheetId=SHEET_ID, body={'requests': opmaak}).execute()


def opmaak_backlog(tab_id, rijen):
    extra = []
    for i, rij in enumerate(rijen[1:], start=1):
        if not rij or rij[0] not in STATUSKLEUR:
            continue
        celkleur, tekst, rijkleur = STATUSKLEUR[rij[0]]
        if rijkleur:  # "Nu" valt op: hele rij licht amber, item vet
            extra.append(cel(tab_id, i, i + 1, 0, 4, {'backgroundColorStyle': {'rgbColor': kleur(rijkleur)}},
                             'backgroundColorStyle'))
            extra.append(cel(tab_id, i, i + 1, 2, 3, {'textFormat': {'bold': True}}, 'textFormat.bold'))
        extra.append(cel(tab_id, i, i + 1, 0, 1, {
            'backgroundColorStyle': {'rgbColor': kleur(celkleur)}, 'horizontalAlignment': 'CENTER',
            'textFormat': {'bold': True, 'foregroundColorStyle': {'rgbColor': kleur(tekst)}}},
            'backgroundColorStyle,horizontalAlignment,textFormat.bold,textFormat.foregroundColorStyle'))
        if rij[1]:  # nummer (B1, B2 ...) vet
            extra.append(cel(tab_id, i, i + 1, 1, 2, {'textFormat': {'bold': True}}, 'textFormat.bold'))
        if rij[0] in ('Af', 'Nee'):  # afgerond of bewust niet: rustiger grijs
            extra.append(cel(tab_id, i, i + 1, 2, 4,
                             {'textFormat': {'foregroundColorStyle': {'rgbColor': kleur('#64748b')}}},
                             'textFormat.foregroundColorStyle'))
    return extra


def groepeer_versies(rijen):
    """Versie en datum alleen op de eerste regel van elke versie."""
    uit, vorige = [rijen[0]], None
    for rij in rijen[1:]:
        if rij and rij[0] == vorige:
            uit.append(['', '', rij[2]])
        else:
            uit.append(rij)
            vorige = rij[0] if rij else None
    return uit


def opmaak_versies(tab_id, rijen):
    extra, eerste, wissel = [], True, False
    for i, rij in enumerate(rijen[1:], start=1):
        if not rij or len(rij) < 3:
            continue
        if rij[0]:  # nieuwe versie begint
            if not eerste:
                wissel = not wissel
                extra.append({'updateBorders': {'range': bereik(tab_id, i, i + 1, 0, 3),
                              'top': {'style': 'SOLID', 'width': 2, 'colorStyle': {'rgbColor': kleur('#94a3b8')}}}})
            eerste = False
            extra.append(cel(tab_id, i, i + 1, 0, 1, {'textFormat': {'bold': True, 'fontSize': 11,
                             'foregroundColorStyle': {'rgbColor': kleur(GROEN)}}},
                             'textFormat.bold,textFormat.fontSize,textFormat.foregroundColorStyle'))
            extra.append(cel(tab_id, i, i + 1, 1, 2,
                             {'textFormat': {'foregroundColorStyle': {'rgbColor': kleur('#64748b')}}},
                             'textFormat.foregroundColorStyle'))
        if wissel:
            extra.append(cel(tab_id, i, i + 1, 0, 3, {'backgroundColorStyle': {'rgbColor': kleur('#f8fafc')}},
                             'backgroundColorStyle'))
    return extra


def main():
    sheets = diensten()
    ids = zorg_voor_tabs(sheets, ['Backlog', 'Versies'])
    stempel = f"Bijgewerkt {datetime.now(timezone.utc):%d-%m-%Y %H:%M} UTC vanuit GitHub (docs/). Niet hier wijzigen: wordt overschreven."
    backlog = lees_backlog() + [[], [stempel]]
    versies = groepeer_versies(lees_versies()) + [[], [stempel]]
    schrijf(sheets, 'Backlog', backlog, ids['Backlog'], [100, 50, 520, 420],
            opmaak_backlog(ids['Backlog'], backlog), GROEN)
    schrijf(sheets, 'Versies', versies, ids['Versies'], [80, 100, 760],
            opmaak_versies(ids['Versies'], versies), '#f59e0b')
    print(f'Backlog: {len(backlog) - 3} regels, Versies: {len(versies) - 3} regels')


if __name__ == '__main__':
    main()
