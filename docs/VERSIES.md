# Versies — Auto voor Annemarie

Versienummer: `groot.klein.fix`. Bij elke release ophogen op **twee plekken**: `VERSIE` in `zoek.py` en hier. Het nummer gaat mee in `docs/data.json` en staat onderaan de site. Code-geschiedenis staat in git.

## 1.16.1 — 14-11-2026

- **Handleiding bladwijzer voor Brave in plaats van Safari** (wens Durk). `bladwijzer.html` heeft nu de stappen voor Brave op de iPhone en Brave op Android. Op Android werkt een bladwijzer met code alleen via de adresbalk (typ "Vul in" en kies hem uit de suggesties), niet vanuit de bladwijzerlijst.

## 1.16.0 — 14-11-2026

- **Bladwijzer "Vul in ANWB": kenteken en km automatisch invullen** (keuze Durk: optie A). De ANWB-knop zet kenteken en km achter # in de link (`koerslijst#kenteken=X667TS&km=162188`); de ANWB doet daar zelf niets mee. De bladwijzer leest ze uit, vult het formulier (velden `licensePlate` en `currentMileage`) en klikt op "Volgende stap"; Annemarie kiest dan alleen nog de uitvoering. Toont de ANWB nog de vorige auto (dat onthoudt hij), dan gaat de bladwijzer eerst een stap terug.
- **Uitlegpagina `bladwijzer.html`** met knop "Kopieer code" en de stappen voor Safari op de iPhone, plus een sleepknop voor de computer. Link bovenaan de site en in de uitleg.
- Getest op anwb.nl op 14-11-2026 met drie echte kentekens, ook vanaf de "vorige auto"-stand. Breekbaar als de ANWB het formulier verandert; dan blijven plakken en "Kopieer km" werken.

## 1.15.0 — 14-11-2026

- **Knop "Kopieer km" naast de ANWB-knop** (wens Durk: het kenteken plakken werkte goed, nu ook de kilometerstand). Een tik zet de kilometerstand als kale cijfers op het klembord (bijv. `128000`) en opent verder niets; plak hem bij de ANWB in het veld "Huidige kilometerstand". Volgorde: eerst de ANWB-knop (kenteken plakken), dan terug naar de site, "Kopieer km", en plakken.

## 1.14.0 — 14-11-2026

- **Kenteken bij de ANWB-knop** (wens Durk). De scraper leest het kenteken uit de advertentiepagina die hij voor de schadecontrole al ophaalt (veld `licensePlate` bij Marktplaats en AutoScout24; niet elke verkoper vult het in). Nieuw veld `kenteken` in `data.json`. De knop toont het kenteken op een geel plaatje; een klik zet het op het klembord en opent de ANWB Koerslijst. Zelf invullen via de link kan niet: de ANWB-pagina leest geen kenteken uit de link (getest 14-11-2026), dus plakken in het kentekenveld.
- **Resterende levensduur beter zichtbaar.** Stond als vierde grijze regel ("Gaat nog ± X jaar mee") en viel weg. Nu: "⏳ **Resterende levensduur: nog ± X jaar**" in vet en gewone tekstkleur. Berekening ongewijzigd.

## 1.13.0 — 12-11-2026

- **Wekker op Cloudflare: de update start nu echt om 08:00** (besluit Durk). GitHub startte de geplande run op het gratis plan uren te laat: de afgelopen week tussen 12:54 en 15:16 Nederlandse tijd in plaats van 08:00. De Worker `auto-annemarie-wekker` (map `wekker/`) draait om 06:00 en 07:00 UTC, kijkt of het in Amsterdam 8 uur is en start dan de workflow "Dagelijkse update" via `workflow_dispatch`. Geheim `GITHUB_TOKEN`: fine-grained token, alleen deze repo, Actions read/write.
- De GitHub-cron blijft als reserve. Komt die later alsnog, dan ziet hij "Vandaag al bijgewerkt" en doet niets.
- Online zetten: `tools\wekker-deploy.ps1`; token zetten of vernieuwen: `tools\wekker-token.ps1` (zie `tools/LEESMIJ.md`).

## 1.12.0 — 12-11-2026

- **Resterende levensduur per auto** (ANWB-tip uit de Kampioen, besluit Durk: alleen als extra regel, telt niet mee in de score). Elke kaart toont "Gaat nog ± X jaar mee". Grove schatting op de betrouwbaarheid van het model: 150.000 km + 20.000 km per punt en 12 jaar + 1 jaar per punt (betrouwbaarheid 8 = ± 310.000 km of 20 jaar). Wat het eerst op is telt, bij 12.000 km per jaar. Nieuwe velden `rest_jaar` en `levensduur_km` in `data.json`.
- **Knop "Check richtprijs bij ANWB" per auto** (besluit Durk: alleen een knop, niet automatisch ophalen; dat blijft op de Nee-lijst). De knop opent de ANWB Koerslijst; daar vul je zelf het kenteken uit de advertentie in. De link staat als `ANWB_KOERSLIJST` in `zoek.py` en gaat mee in `data.json`.
- Uitleg van beide onder "Hoe wordt de top 5 bepaald?". De score zelf is niet veranderd.

## 1.11.0 — 01-11-2026

- **Hoogstens 4 van hetzelfde model per soort** (besluit Durk), nieuwe grens `PER_MODEL` naast `PER_SOORT`. Zonder die grens vulde één model met veel aanbod de hele categorie: 18 van de 24 benzineplekken was een Kia Ceed, waardoor nieuwe modellen er nooit doorheen kwamen. `cee'd` en `ceed` tellen als één model (`MODEL_ALIAS`); auto's waarvan het model niet op de lijst staat worden niet op één hoop gegooid. Een model dat in twee soorten voorkomt mag in allebei vier (de Auris staat er nu 4× als hybride en 3× als benzine).
- **Drie modellen erbij** (besluit Durk): Kia Sportage en Hyundai Tucson (beide 1.6 GDI zonder turbo, betrouwbaarheid 7,5, segment C) en Toyota Avensis (1.8 Valvematic, betrouwbaarheid 8,5, segment D).
- **Ioniq en Niro mogen nu ook zonder stekker.** Ze stonden wel in `MODELLEN` maar niet in `ZONDER_STEKKER`, waardoor de gewone hybride eruit viel terwijl de stekkerversie wel mocht. Dat was geen keuze maar een gat in de regel. Ze komen binnen via de brede zoekopdracht op brandstof, dus zonder eigen benzinezoekactie (pad `None`).
- **Lijst opnieuw opgehaald**: 2.537 bekeken, 669 geschikt, 80 op de site (23 benzine, 22 plug-in, 19 elektrisch, 10 hybride, 6 waterstof). Korter dan de 95 van gisteren, en dat is de bedoeling: de dubbele Ceed's zijn eruit en er staan nu 12 verschillende modellen in plaats van 5 bij benzine.
- Nieuw in de top 10: Hyundai Ioniq Hybrid op plek 2 (73,8) en Kia Niro Hybrid op plek 8 (69,6). De ASX staat op 31, 34, 39 en 41; de Sportage op 43, 48, 52 en 54; de Avensis op 25. De Tucson haalt het nog niet.

## 1.10.0 — 01-11-2026

- **Mitsubishi ASX erbij** (besluit Durk). Betrouwbaarheid 7,5: de 1.6 MIVEC is atmosferisch, heeft een distributieketting en is handgeschakeld. 1.310 kg, 4.365 mm, segment C, 7,0 l/100 km. Benzine wordt nu voor zeven modellen per model opgehaald.
- **Maar hij haalt de site nog niet.** Acht ASX'en komen door alle filters, met scores van 60,7 tot 65,5. De grens van 25 auto's per soort ligt bij benzine op 68,6, dus ze vallen er net buiten. Oorzaak: van de 24 benzineplekken zijn er **18 bezet door een Kia Ceed**.
- **Lijst opnieuw opgehaald**: 2.486 bekeken, 621 geschikt, 95 op de site (24 benzine, 23 plug-in, 22 elektrisch, 19 hybride, 7 waterstof).

## 1.9.0 — 30-10-2026

- **Mazda eruit** (verzoek Durk). De Mazda 2, Mazda 3 en MX-30 zijn van de toelatingslijst gehaald en het merk zelf is uit `GANGBARE_MERKEN`, zodat ook een Mazda-model dat niet op de lijst staat niet meer met een neutrale betrouwbaarheid binnenkomt. De maten blijven in `GEWICHT`, `LENGTE` en `SEGMENT` staan: terugzetten kost alleen die paar regels in `MODELLEN` en `ZONDER_STEKKER`.
- Benzine wordt daardoor nog voor zes modellen per model opgehaald (Auris, Prius, Civic, CT, Ceed, i30).
- **Lijst opnieuw opgehaald**: 2.521 bekeken, 614 geschikt, 101 op de site (24 benzine, 24 elektrisch, 24 plug-in, 20 hybride, 9 waterstof). De Mazda 3 die op plek 2 stond is weg; hoogste blijft de Toyota Auris 1.8 Hybrid uit 2018 (100.870 km, € 9.750, score 76,5).

## 1.8.0 — 28-10-2026

- **BMW i3 doet weer mee, ondanks segment B** (besluit Durk). Nieuwe tabel `SEGMENT_UITZONDERING`: modellen die onder segment C zitten maar toch mogen. Voorlopig alleen de i3 (3.999 mm). Er staan er nu vier op de site, de hoogste op plek 23 met score 68,6 (2016, 114.100 km, € 9.999).
- **Dieper zoeken: `MAX_PAGINAS` van 20 naar 50.** AutoScout24 meldt zelf hoeveel pagina's er zijn en de zoekactie stopt daar; voor plug-ins waren dat er 22, dus die laatste twee pagina's (± 40 advertenties) werden niet meer opgehaald. Nu wel: 822 in plaats van 798 advertenties bij AutoScout24. Elektrisch (18 pagina's) en diesel-hybride (3) zaten al onder de grens.
- **Waarom er toch geen BMW 225xe of 330e op de site staat:** niet omdat ze gemist worden — ze zitten wel degelijk in de zoekopdracht (27 BMW's), maar hun score komt niet hoog genoeg. De beste 225xe haalt 54,0 en de laagste plug-in op de site staat op 59,4. Ze vallen dus af op de grens van 25 auto's per soort, niet op dekking.
- **Lijst opnieuw opgehaald**: 2.522 bekeken, 636 geschikt, 100 op de site (24 benzine, 24 elektrisch, 24 plug-in, 20 hybride, 8 waterstof).

## 1.7.0 — 27-10-2026

- **Grootte-eis vervangen: minstens segment C** (besluit Durk). De eis "niet korter dan de Citroën C3 Pluriel (3.934 mm)" is eruit; in de plaats komt het Europese segment: **C – compacte middenklasse** (de Golf-klasse) of groter. Segment D, E en F mogen ook, A (stadsauto) en B (klein) niet. Nieuwe tabel `SEGMENT` per model en de functie `onder_segment()`; `MIN_LENGTE` en `te_klein()` zijn weg. Een SUV krijgt het segment van de auto waarop hij gebouwd is (Countryman en 3008 C, Outlander D, X5 en XC90 E). Grensgevallen die bewust B zijn en dus afvallen: Yaris, Jazz, Polo, Fabia, Ibiza, i20, Rio, Mazda 2, ZOE, i3 (3.999 mm), Kona, Soul, Ampera-e en e-208. Bewust C: Mercedes B-klasse (C-MPV) en Mazda MX-30. De lengte staat nog wel op de kaart, nu met het segment erachter.
- **Prijsgrens naar € 10.000** (besluit Durk), voor alle brandstoffen. Nodig ook: de compacte middenklasse begint boven de € 8.000 pas echt (82 van de 97 auto's op de lijst kosten meer dan € 8.000).
- **Benzine wordt per model nog maar voor zeven modellen opgehaald** (Auris, Prius, Civic, CT, Ceed, i30, Mazda 3); Aygo, Yaris, Jazz, Swift, Picanto, Rio, i10, i20, Mazda 2, Fabia, Polo, Ibiza, 108 en C1 zitten onder segment C en worden niet meer gezocht.
- **Lijst opnieuw opgehaald**: 2.502 bekeken, 632 geschikt, 97 op de site (24 benzine, 24 elektrisch, 22 plug-in, 19 hybride, 8 waterstof). Hoogste score: Mazda 3 2015 / 315 km / € 5.200 (74,9), daarna vier Kia Ceed's.

## 1.6.0 — 27-10-2026

- **Waterstofauto's doen mee** (besluit Durk). Nieuwe soort **Waterstof** met de Toyota Mirai, Hyundai Nexo en Hyundai ix35 FCEV. Een auto telt alleen als waterstof als de advertentie dat zelf zegt (brandstofveld of woorden als "waterstof", "FCEV", "Mirai"); een gewone benzine-ix35 valt dus gewoon af.
- **Rode H2 naast de score** op elke kaart, zodat in één oogopslag duidelijk is dat het waterstof is. Ook een filterknop "Waterstof" en een eigen alinea in de uitleg.
- **Rekenwerk**: € 15,00 per kilo (de pompprijs liep in 2026 uiteen van ± € 10 tot € 25) en ongeveer 1 kilo per 100 km, dus ± € 150 per maand bij 12.000 km per jaar. Wegenbelasting is 70% van het benzinetarief, net als bij elektrisch. Bereik per tank: Mirai 420 km, Nexo 550 km, ix35 380 km (zomer), met dezelfde winterkorting en dezelfde bereikschaal als elektrisch. Elke waterstofauto krijgt twee waarschuwingen op de kaart: "tanken kan op ± 20 plaatsen in Nederland" en de prijs per kilo.
- **Ophalen**: AutoScout24 per model (Mirai, Nexo, ix35), Marktplaats in één keer op brandstof `Waterstof`.
- **Lijst opnieuw opgehaald**: 2.131 bekeken, 965 geschikt, 70 op de site. Drie waterstofauto's: Toyota Mirai 2019 / 155.424 km / € 7.450 (score 62,1, plek 30), Hyundai ix35 FCEV 2016 / 81.694 km / € 5.950 (59,7) en Toyota Mirai 2019 / 202.114 km / € 5.445 (59,1).

## 1.5.0 — 22-10-2026

- **Ondergrens prijs van € 1.500 naar € 1.200**, voor elk soort auto (besluit Durk).
- **Benzine en gewone hybride mogen ook tot 260.000 km** en vanaf € 1.200, gelijk aan elektrisch (besluit Durk). De enige strengere eis die blijft, is bouwjaar 2015 of nieuwer. De uitleg op de site is aangepast: niet meer "strengere eisen", maar één strengere eis, met de waarschuwing dat distributieriem, koppeling en uitlaat bij een hoge stand dure posten zijn die een elektrische auto niet heeft.
- **Meer aanbod bekeken**: 2.102 advertenties in plaats van 1.297, waarvan er 940 door de filters komen (was 377). Op de site staan er 66: 25 benzine (de limiet per soort), 21 plug-in, 19 elektrisch en 1 gewone hybride. De benzinelijst is nu Yaris (12), Fabia (9), Ibiza (2), Mazda 3, i20 (2), met standen tot 243.000 km.

## 1.4.1 — 22-10-2026

- **Criteria staan nu op de site** (wens Durk). Uitklapbaar blok bovenaan met alle harde eisen: prijs € 1.500–€ 8.000, lengte minstens 3.934 mm, elektrisch en plug-in vanaf 2010 met hoogstens 260.000 km, benzine en gewone hybride vanaf 2015 met hoogstens 150.000 km en minstens € 3.000, geen diesel of LPG, alleen Nederland, alleen modellen van de toelatingslijst, en hoogstens 25 auto's per soort. De getallen komen uit `data.json` (nieuw veld `criteria`), dus site en `zoek.py` kunnen niet uit elkaar gaan lopen.
- **Bestelbussen die er nog doorheen kwamen eruit**: een Peugeot Partner Electric stond gewoon in de lijst. `UITSLUITEN` kent nu ook Partner, Berlingo, Caddy, Combo, Doblo, NV200, Proace, Vivaro, Transporter, Boxer, Jumper, Jumpy, Expert, Scudo, Bipper en Nemo.
- **Lijst opnieuw opgehaald** met de nieuwe regels: 1.297 advertenties bekeken, 63 op de site (24 benzine, 21 plug-in, 19 elektrisch, één bestelbus eruit). De benzinelijst is nu Yaris, Fabia, Polo, i20, Rio, Mazda 3 en Ibiza in plaats van alleen Aygo's, 108's en C1's: die vulden met 24 stuks de hele limiet van 25 per soort, waardoor grotere auto's er niet eens in kwamen.

## 1.4.0 — 22-10-2026

- **Niet kleiner dan de Citroën C3 Pluriel** (wens Durk). De C3 Pluriel die Annemarie nu rijdt is 3.934 mm (393 cm) lang; alles wat korter is, komt niet meer op de site. Nieuwe tabel `LENGTE` met de lengte per model en grens `MIN_LENGTE = 3934` in `zoek.py`. Daardoor vallen af: VW up en e-up, Škoda Citigo, Seat Mii, Dacia Spring, Fiat 500e, Renault Twingo, Toyota Aygo, Suzuki Swift, Kia Picanto, Hyundai i10, Peugeot 108 en Citroën C1. Op de lijst van 18-10 ging het om 26 van de 63 auto's (12 Aygo's, 4 Peugeot 108, 3 C1, 3 Fiat 500e, Twingo, e-up, i10, Picanto); 37 blijven over. Modellen die het niet halen worden ook niet meer opgehaald bij AutoScout24 en Marktplaats, dus de dagelijkse ronde is korter. Staat de lengte van een model niet in de tabel, dan valt de auto niet af: dan weten we het niet.
- **Lengte op de kaart en als criterium op de site.** Elke auto toont "± xxx cm lang", de kopregel noemt de eis en de uitleg legt uit waarom en welke modellen daardoor afvallen.
- **"Totale kosten" heet nu "Totale kosten excl. onderhoud"** (besluit Durk), op de kaart, in de score-uitleg en in de toelichting. Onderhoud, APK en reparaties zitten niet in dat bedrag.

## 1.3.2 — 18-10-2026

- **Een accu die in dat bouwjaar nog niet bestond, wordt niet meer gebruikt** (B1). Een ZOE uit 2013 met "41 kWh" in de titel kreeg 41 kWh en daarmee ± 210 km bereik, bijna het dubbele van wat hij haalt; de 41 kWh-accu zit er pas in vanaf 2017. Elke uitvoering in de tabel `ACCU` heeft nu een eerste bouwjaar. Een maat uit de titel wordt alleen gebruikt als die uitvoering er toen al was; zo niet, dan de grootste accu die er in dat bouwjaar wel in zat. Die ZOE staat nu op 22 kWh en ± 110 km, en zakt in de score van 57,7 naar 48,3. Verder veranderde er geen enkele auto in de lijst.

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
