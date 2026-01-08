
## 1. Aanpak

Dit project is gemaakt als een **rule-based expert system** met de Python-bibliotheek **Experta**.
Het idee is om het systeem zo simpel mogelijk te houden aan het begin, en daarna slimme regels te gebruiken om automatisch nieuwe kennis af te leiden.

De belangrijkste keuzes zijn:

* we slaan **alleen minimale basisfeiten** op
  (personen, ouder-kind relaties en huwelijken/relaties)
* we voeren **geen familiebanden handmatig** in zoals vader, moeder of neef
* alle complexe relaties worden **automatisch afgeleid door regels**

Dit volgt het klassieke AI-model van een **knowledge base + inference engine**.

### Initiële kennisbank (bewust klein)

De gebruiker voert alleen deze feiten in:

* `Persoon(naam, geslacht)`
* `OuderRelatie(kind, ouder)`
* `RelatieGroep(leden={...})`

Alle andere relaties zoals vader, moeder, siblings, cousins en kleinkinderen worden **door het systeem zelf afgeleid**.

---

## 2. Code-architectuur

De code is opgebouwd in vijf duidelijke lagen:

1. **Basisfeiten**
   Dit zijn de ruwe gegevens, zoals personen en ouder-kind relaties.

2. **Afgeleide feiten**
   Deze feiten worden nooit handmatig ingevoerd
   (bijvoorbeeld `Vader`, `BroerZus`, `Kleinkind`).

3. **Regels (Rules)**
   De regels beschrijven wanneer een afgeleid feit geldig is.

4. **Inference Engine**
   De klasse `FamilieRedeneerder` voert de redenering uit.

5. **Query-functies**
   Deze functies lezen de afgeleide feiten uit het werkgeheugen.

Door deze scheiding is de code overzichtelijk en makkelijk uitbreidbaar.

---

## 3. Forward en Backward Chaining

### Forward chaining (gebruikt)

Experta werkt met **forward chaining**:

* het systeem start met bekende feiten
* zodra een regel klopt, wordt deze uitgevoerd
* nieuwe feiten worden toegevoegd aan het werkgeheugen

Dit is handig voor:

* simulaties
* automatisch afleiden van kennis
* familie-relaties die stap voor stap ontstaan

### Backward chaining (niet standaard)

Backward chaining (doelgericht redeneren) wordt **niet standaard ondersteund** door Experta.
In dit project wordt dit **gesimuleerd met query-functies**, die zoeken in het werkgeheugen of een bepaald feit bestaat.

---

## 4. Opslag van afgeleide feiten

Afgeleide feiten zijn:

* **permanent aanwezig** zolang de engine draait
* niet tijdelijk of context-afhankelijk
* opnieuw afgeleid na een `reset()` van de engine

Voordelen hiervan zijn:

* alle conclusies zijn zichtbaar en uitlegbaar
* geen “magische” beslissingen
* wel kans op dubbele feiten (dit kan later geoptimaliseerd worden)

---

## 5. Futureproof ontwerp

Het systeem is gemaakt met moderne en inclusieve familiestructuren in gedachten.

###  Eenoudergezinnen

* Geen enkele regel verwacht twee ouders
* Eén ouder-relatie is genoeg
   Volledig ondersteund

###  Genderneutraal (M / F / X)

* Geslacht is optioneel
* Ouders met `X` worden apart behandeld
   Volledig ondersteund

###  Geslachtswijziging

* Geslacht staat in één `Persoon`-fact
* Aanpassen + engine reset is voldoende
   Geen code-aanpassing nodig

###  Huwelijk tussen personen van hetzelfde geslacht

* Relaties gebruiken een `set`
* Geen aannames over man/vrouw
 Volledig ondersteund

###  Relatie of huwelijk met 3 of meer personen

* `RelatieGroep(leden: set)`
* Geen limiet op aantal personen
   Al ondersteund door het ontwerp

---
