# Versies — Auto voor Annemarie

Versienummer: `groot.klein.fix`. Bij elke release ophogen op **twee plekken**: `VERSIE` in `zoek.py` en hier. Het nummer gaat mee in `docs/data.json` en staat onderaan de site. Code-geschiedenis staat in git.

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
