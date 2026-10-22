# Backlog — Auto voor Annemarie

*Bijgewerkt 22-10-2026*

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
| B2 | **Nieuwe modellen in de modellenlijst.** `MODELLEN` is ook de toelatingslijst: een model dat er niet in staat, krijgt een neutrale betrouwbaarheid van 5,5 en een standaard-accumaat van 24 kWh. Modellen die inmiddels onder de € 8.000 kunnen komen, staan er nog niet in (o.a. Citroën ë-C3, Opel Corsa-e, Peugeot e-2008, Mini Cooper SE, MG ZS EV, VW ID.3, Renault Captur plug-in). Per model ook de accumaat en het verbruik invullen. | Elk model dat in de uitslag voorkomt heeft een eigen betrouwbaarheidscijfer, accumaat en verbruik; geen auto in de top 20 draait meer op de standaardwaarden |

## Volgende (op volgorde)

| # | Item | Af als… |
|---|---|---|
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

**Modellen die bewust niet op de toelatingslijst komen:** Renault, Fiat en Alfa Romeo met benzinemotor · de Opel 1.4 Turbo · de Ford 1.0 EcoBoost (koelvloeistof, distributieriem) · elke auto met een DSG- of CVT-automaat van vóór 2015. Goedkoop in aanschaf, duur in onderhoud.

Specificaties per advertentie scrapen (fragiel en langzaam; de modeltabel doet hetzelfde werk één keer) · prijs of taxatie voorspellen · onderhandelen of contact opnemen met verkopers · accounts bij de marktplaatsen · auto's boven € 8.000 · gewone hybrides zonder stekker.

## Af

| # | Item | Datum |
|---|---|---|
| B9 | **Criteria zichtbaar op de site + bestelbussen eruit** (v1.4.1): uitklapbaar criteria-blok bovenaan, gevuld vanuit `data.json`; Partner, Berlingo, Caddy en andere bestelbussen toegevoegd aan `UITSLUITEN` | 22-10-2026 |
| B8 | **Minimumlengte: niet kleiner dan de Citroën C3 Pluriel** (v1.4.0): tabel `LENGTE` per model, grens `MIN_LENGTE = 3934` mm. up/e-up, Citigo, Mii, Spring, 500e, Twingo, Aygo, Swift, Picanto, i10, 108 en C1 vallen af (26 van de 63 auto's op de lijst van 18-10); lengte staat op de kaart en als criterium in de uitleg. Ook: "totale kosten" heet nu "totale kosten excl. onderhoud" | 22-10-2026 |
| B1 | **Accumaat begrensd op wat in dat bouwjaar leverbaar was** (v1.3.2): elke uitvoering in `ACCU` heeft een eerste bouwjaar; een kWh-maat uit de titel geldt alleen als die accu er toen al was, anders de grootste van dat jaar. De ZOE uit 2013 ging van 41 kWh / ± 210 km naar 22 kWh / ± 110 km | 18-10-2026 |
| B7 | **Benzine en gewone hybride erbij** (v1.3.0): 22 modellen met een bewezen reputatie, strengere eisen zonder stekker (2015 / 150.000 km / € 3.000), benzine per model opgehaald, "totale kosten bij 12.000 km per jaar" in plaats van vaste lasten, bereik vast 8 van 10, hoogstens 25 auto's per soort op de site | 18-10-2026 |
| — | **Halve-prijs-advertenties eruit** ("betaal nu 50%, de rest later": € 7.950 in de lijst, € 16.000 in het echt) (v1.2.2) | 18-10-2026 |
| — | **Bereik per auto** op de kaart en voor 20% in de score, met accumaat per uitvoering, verbruik per model en een geschatte accustaat (v1.2.0); i3 Range Extender eigen bereik (v1.2.1) | 18-10-2026 |
| — | **Opel Rocks uitgefilterd**, ook zonder "-e" in de naam (v1.1.0) | 18-10-2026 |
| — | Eerste versie: dagelijkse zoekactie, score met uitleg, site met top 5 en filters (v1.0.0) | 12-10-2026 |

---

**Google Sheet:** [Auto voor Annemarie — backlog en versies](https://docs.google.com/spreadsheets/d/1R0dGSir9Tyh0SPfiEnYhB8ycrnz9xlUN_C9h40wtCqY/edit) — tabs *Backlog* en *Versies*. Dit bestand en `VERSIES.md` zijn de bron; bij elke push naar GitHub zet de Action `sync-sheet.yml` ze automatisch in de sheet (service-account `youtube-commenter@yt-comment-bot-494117`, secret `GOOGLE_SA_JSON`). Wijzig dus hier, niet in de sheet.
