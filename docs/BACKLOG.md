# Backlog — Auto voor Annemarie

*Bijgewerkt 18-10-2026*

> **Nog door Durk te bevestigen:** de verdeling over Nu / Volgende / Later hieronder is een voorstel.
> Wat er op "Nu" staat, bepaalt Durk.

## Werkwijze (geldt voor elk item)

1. **Eén ding tegelijk.** Hooguit 1 item staat op "Nu". Pas als het af is, komt het volgende.
2. **Volgorde = het knelpunt.** Het knelpunt is of de lijst klopt: een auto die er niet in hoort of
   een getal dat niet klopt, kost meer dan een ontbrekende functie. Daarna pas: kijkt Annemarie er
   ook echt naar?
3. **"Af" vooraf vastleggen.** Elk item heeft een regel "Af als…". Daar stoppen we, er komt niets
   extra's bij.
4. **Simpel eerst.** Is er een manier met minder stappen, dan nemen we die. Liever iets schrappen
   dan versimpelen.
5. **Eén tabel per model, geen scraper per advertentie.** Wat uit een tabel kan, komt uit een tabel:
   dat breekt niet als een site verandert.

## Nu (max 1)

| # | Item | Af als… |
|---|---|---|
| B1 | **Accumaat begrenzen op wat in dat bouwjaar leverbaar was.** Er staat een Renault Zoe uit 2013 in de lijst met "41 kWh" in de titel; die accu bestond pas vanaf 2017. De app rekent nu met 41 kWh en geeft hem ± 210 km, bijna het dubbele van wat hij echt haalt. Per uitvoering in `ACCU` een eerste bouwjaar meegeven, en een kWh uit de titel alleen gebruiken als die uitvoering in dat jaar bestond. | De Zoe uit 2013 krijgt 22 kWh en ± 110 km; een Leaf uit 2018 met "40 kWh" in de titel houdt zijn 39 kWh; geen enkele auto in de lijst heeft een accu die in zijn bouwjaar niet bestond |

## Volgende (op volgorde)

| # | Item | Af als… |
|---|---|---|
| B2 | **Nieuwe modellen in de modellenlijst.** `MODELLEN` is ook de toelatingslijst: een model dat er niet in staat, krijgt een neutrale betrouwbaarheid van 5,5 en een standaard-accumaat van 24 kWh. Modellen die inmiddels onder de € 8.000 kunnen komen, staan er nog niet in (o.a. Citroën ë-C3, Opel Corsa-e, Peugeot e-2008, Mini Cooper SE, MG ZS EV, VW ID.3, Renault Captur plug-in). Per model ook de accumaat en het verbruik invullen. | Elk model dat in de uitslag voorkomt heeft een eigen betrouwbaarheidscijfer, accumaat en verbruik; geen auto in de top 20 draait meer op de standaardwaarden |
| B3 | **Ondergrens voor plug-in hybrides heroverwegen.** Een plug-in krijgt nu minimaal 5 van 10 op bereik, omdat je met benzine erbij nooit strandt. Daardoor klimmen plug-ins ten opzichte van de kleine elektrische auto's. Kijken of dat klopt met wat Annemarie wil: een goedkope stadsauto of een auto die ook de lange rit doet. | Durk heeft gekozen; de ondergrens staat op de gekozen waarde en de top 5 is één keer met beide instellingen vergeleken |
| B4 | **Accustaat ruimer herkennen.** Nu wordt alleen "SoH 82%" gevonden. Verkopers schrijven ook "accu 85%", "batterij nog 90%", "SOH: 78". Alles wat daar niet op lijkt, valt terug op de schatting op leeftijd. | Op de huidige lijst wordt minstens de helft meer accustaten uit de advertenties gehaald, zonder valse treffers (een percentage dat over iets anders gaat) |
| B5 | **Merkvoorkeur van Annemarie invullen.** `MERK_VOORKEUR` staat leeg; de bonus van 5 punten doet dus niets. Eerst aan Annemarie vragen welke merken ze wel en niet wil. | De merken die Annemarie noemt staan in de lijst, en die auto's staan zichtbaar hoger |
| B6 | **Bericht als er een nieuwe auto in de top 5 staat.** Nu moet je de site zelf openen. De dagelijkse Action weet precies wat er nieuw is ("nieuw"-label bestaat al); een mailtje aan Durk en Annemarie als de top 5 verandert, scheelt elke dag kijken. | Bij een wijziging in de top 5 komt er een mail met de nieuwe auto's en de link; geen mail als er niets verandert |

## Later

- **Wegenbelasting per provincie.** Nu staat alles op Utrecht; dat scheelt tot ongeveer 10%.
- **Verzekering uit een echte offerte** in plaats van de huidige grove schatting.
- **Meer bronnen** naast AutoScout24 en Marktplaats (Gaspedaal, AutoTrack).
- **Auto's afvinken** ("deze niet"), zodat ze niet elke dag terugkomen.
- **Laadmogelijkheid thuis** meewegen zodra bekend is of Annemarie een laadpunt heeft.

## Nee-lijst (bewust niet)

Specificaties per advertentie scrapen (fragiel en langzaam; de modeltabel doet hetzelfde werk één
keer) · prijs of taxatie voorspellen · onderhandelen of contact opnemen met verkopers · accounts bij
de marktplaatsen · auto's boven € 8.000 · gewone hybrides zonder stekker.

## Af

| # | Item | Datum |
|---|---|---|
| — | **Bereik per auto** op de kaart en voor 20% in de score, met accumaat per uitvoering, verbruik per model en een geschatte accustaat (v1.2.0); i3 Range Extender eigen bereik (v1.2.1) | 18-10-2026 |
| — | **Opel Rocks uitgefilterd**, ook zonder "-e" in de naam (v1.1.0) | 18-10-2026 |
| — | Eerste versie: dagelijkse zoekactie, score met uitleg, site met top 5 en filters (v1.0.0) | 12-10-2026 |

---

**Google Sheet:** [Auto voor Annemarie — backlog en versies](https://docs.google.com/spreadsheets/d/1R0dGSir9Tyh0SPfiEnYhB8ycrnz9xlUN_C9h40wtCqY/edit) — tabs *Backlog* en *Versies*. Dit bestand en `VERSIES.md` zijn de bron; bij elke push naar GitHub zet de Action `sync-sheet.yml` ze automatisch in de sheet (service-account `youtube-commenter@yt-comment-bot-494117`, secret `GOOGLE_SA_JSON`). Wijzig dus hier, niet in de sheet.
