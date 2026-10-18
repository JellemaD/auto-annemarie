# Versies — Auto voor Annemarie

Versienummer: `groot.klein.fix`. Bij elke release ophogen op **twee plekken**: `VERSIE` in `zoek.py` en hier. Het nummer gaat mee in `docs/data.json` en staat onderaan de site. Code-geschiedenis staat in git.

## 1.3.1 — 18-10-2026

- **LPG eruit en handelaarsadvertenties met meerdere auto's eruit.** Bij de eerste benzineronde kwam "4X TOYOTA AYGO 1.0 BENZINE LPG BOUWJAAR 2018-2021" voor € 3.750 in de lijst: vier auto's in één advertentie, dus prijs en kilometerstand horen bij geen van allen.

## 1.3.0 — 18-10-2026

- **Benzine en gewone hybride doen mee** (wens Durk). Alleen modellen met een bewezen reputatie: Aygo, 108, C1, Yaris, Auris, Prius, Jazz, Civic, Lexus CT, Swift, Picanto, Rio, Cee'd, i10, i20, i30, Mazda 2 en 3, Fabia, Polo, Ibiza. Diesel en LPG doen niet mee.
- **Strengere eisen zonder stekker**: bouwjaar 2015 of nieuwer, hoogstens 150.000 km, minstens € 3.000. Een elektrische auto heeft geen distributieriem, koppeling of uitlaat, dus daar blijven 2010, 260.000 km en € 1.500 staan.
- **Benzine wordt per model opgehaald.** De hele benzinemarkt tot € 8.000 is te groot om te doorzoeken; elektrisch en plug-in blijven in één keer op brandstof opgehaald, want per model werkt daar averechts (de e-Golf en e-up bestaan niet als eigen model op AutoScout24).
- **"Vaste lasten" heet nu "totale kosten bij 12.000 km per jaar"** (besluit Durk) en telt ook brandstof of stroom mee: € 2,10 per liter benzine, € 0,28 per kWh thuis laden. De schaal in de score loopt nu van € 100 (maximum) tot € 300 (nul).
- **Bereik bij benzine en hybride**: vast 8 van 10, met "± 600 km per tank" op de kaart. Geen 10, want tanken is duurder dan thuis laden en dat verschil zit al in de kosten.
- **Per soort hoogstens 25 auto's op de site.** Zonder die grens verdringt het jonge benzineaanbod alle elektrische auto's en is er onder "Elektrisch" niets meer te zien.
- Filterknoppen **Hybride** en **Benzine** erbij, en de uitleg onderaan vertelt welke eisen per brandstof gelden.

## 1.2.3 — 18-10-2026

- **Op de site staat nu ook wat er bewust níét op de modellenlijst komt** (wens Durk): Renault, Fiat en Alfa Romeo met benzinemotor, de Opel 1.4 Turbo, de Ford 1.0 EcoBoost (koelvloeistof en distributieriem) en elke auto met een DSG- of CVT-automaat van vóór 2015. Goedkoop in aanschaf, duur in onderhoud.

## 1.2.2 — 18-10-2026

- **Advertenties waarin de genoemde prijs niet de hele prijs is, vallen af.** "ACTIE! BETAAL NU 50% 7950, DE REST LATER" stond voor € 7.950 in de lijst terwijl de auto € 16.000 kost. Herkend worden: betalen in procenten of "de helft", en een restbedrag dat later, bij aflevering of in termijnen komt. Een advertentie die alleen "aanbetaling mogelijk" of "100% onderhouden" zegt, blijft gewoon staan.

## 1.2.1 — 18-10-2026

- **BMW i3 Range Extender krijgt zijn eigen elektrische bereik** (90 km). Hij telt als plug-in hybride en kreeg daardoor de standaardwaarde van 30 km, terwijl hij de gewone i3-accu van ruim 20 kWh heeft.

## 1.2.0 — 18-10-2026

- **Bereik per auto**, op de kaart en in de score. Berekend uit de netto accumaat van die uitvoering, maal de accustaat, gedeeld door het werkelijke verbruik van dat model. In de winter gaat er een kwart af.
- De **kWh uit de titel** kiest de uitvoering, maar alleen als het getal in de buurt van een bestaande uitvoering ligt. Anders is het het vermogen ("Fiat 500e 83kwh" werd zo een 37 kWh-auto).
- **Accustaat geschat op leeftijd** als de advertentie geen SoH noemt. De Nissan Leaf en de 27 kWh-Kia Soul lopen sneller terug: die hebben geen accukoeling.
- Bij een **plug-in hybride** is het bereik het elektrische deel, met een ondergrens van 5 van 10 omdat de benzinemotor stranden onmogelijk maakt.
- **Nieuwe weging van de score**: betrouwbaarheid 35, bereik 20, bouwjaar 18, kilometerstand 17, vaste lasten 10 (was 35 / — / 28 / 22 / 15).
- Nieuwe waarschuwing **"Klein winterbereik"** onder de 80 km.
- De score-uitleg op de site toont de berekening van het bereik per auto.
- Backlog en versies vastgelegd in `docs/BACKLOG.md` en `docs/VERSIES.md`, met automatische sync naar de Google Sheet bij elke push.

## 1.1.0 — 18-10-2026

- **Opel Rocks wordt uitgefilterd.** De lijst kende alleen "rocks-e" en "rocks e", waardoor een advertentie met de naam "Opel Rocks Tekno" op de site kwam. Nu matcht "rocks" op woordgrens.

## 1.0.0 — 12-10-2026

- Eerste versie: dagelijkse zoekactie om 8:00 via GitHub Actions over AutoScout24 en Marktplaats, elektrisch en plug-in hybride tot € 8.000 in heel Nederland.
- Score op betrouwbaarheid van het model, bouwjaar, kilometerstand en vaste lasten, met uitleg per auto.
- Weggefilterd: brommobielen en microcars, Smarts, bestelbussen, schadeauto's, gewone hybrides zonder stekker en elektrische auto's met een huuraccu.
- Site op GitHub Pages met top 5, volledige lijst, filters op soort en merk, en "Nieuw"-labels.
