from experta import KnowledgeEngine, Fact, Field, Rule, MATCH, TEST

# =========================================================
# 1. BASISFEITEN (direct ingevoerde feiten)
# =========================================================

class Persoon(Fact):
    """
    Persoon-fact:
    Stelt een individu voor met een naam en optioneel geslacht.

    Voorbeeld:
        Persoon(naam="Jan", geslacht="M")
    """
    naam = Field(str, mandatory=True)
    geslacht = Field(str, mandatory=False)


class OuderRelatie(Fact):
    """
    OuderRelatie-fact:
    Beschrijft een ouder-kind relatie.

    LET OP:
    structuur = (kind, ouder)

    Voorbeeld:
        OuderRelatie(kind="Jan", ouder="Piet")
        → Piet is ouder van Jan
    """
    kind = Field(str, mandatory=True)
    ouder = Field(str, mandatory=True)


# =========================================================
# 2. AFGELEIDE FEITEN (automatisch door regels)
# =========================================================

class Vader(Fact):
    """Afgeleid feit: vader-kind relatie"""
    pass


class Moeder(Fact):
    """Afgeleid feit: moeder-kind relatie"""
    pass


class NeutraleOuder(Fact):
    """Afgeleid feit: ouder met onbekend/neutral geslacht"""
    pass


class BroerZus(Fact):
    """Afgeleid feit: sibling-relatie"""
    pass


class OomTante(Fact):
    """Afgeleid feit: oom/tante relatie"""
    pass


class NeefNicht(Fact):
    """Afgeleid feit: neef/nicht relatie"""
    pass


class CousinRelatie(Fact):
    """Afgeleid feit: cousin (kinderen van siblings)"""
    pass


class Kleinkind(Fact):
    """Afgeleid feit: grootouder-kleinkind relatie"""
    pass


# =========================================================
# 3. RELATIE / HUWELIJK
# =========================================================

class RelatieGroep(Fact):
    """
    RelatieGroep-fact:
    Stelt een huwelijk of relatie voor.

    - Gebruikt een set (volgorde maakt niet uit)
    - Ondersteunt meer dan twee personen
    """
    leden = Field(set, mandatory=True)


# =========================================================
# 4. INFERENTIE-ENGINE
# =========================================================

class FamilieRedeneerder(KnowledgeEngine):
    """
    Deze engine leidt familiebanden af
    op basis van ingevoerde feiten.
    """

    # -----------------------------
    # Vader-afleiding
    #Als X is kind van Y en Y is man, dan is Y de vader van X.
    @Rule(
        OuderRelatie(kind=MATCH.k, ouder=MATCH.o),
        Persoon(naam=MATCH.o, geslacht="M")
    )
    def bepaal_vader(self, k, o):
        self.declare(Vader(ouder=o, kind=k))
        print(f"AFGELEID: {o} is vader van {k}")

    # -----------------------------
    # Moeder-afleiding

    # Als X is kind van Y en Y is vrouw, dan is Y de moeder van X.
    # -----------------------------
    @Rule(
        OuderRelatie(kind=MATCH.k, ouder=MATCH.o),
        Persoon(naam=MATCH.o, geslacht="F")
    )
    def bepaal_moeder(self, k, o):
        self.declare(Moeder(ouder=o, kind=k))
        print(f"AFGELEID: {o} is moeder van {k}")

    # -----------------------------
    # Neutrale ouder

    # Als X is kind van Y en het geslacht van Y is onbekend of neutraal, dan is Y een neutrale ouder van X.
    # -----------------------------
    @Rule(
        OuderRelatie(kind=MATCH.k, ouder=MATCH.o),
        Persoon(naam=MATCH.o, geslacht="X")
    )
    def bepaal_neutrale_ouder(self, k, o):
        self.declare(NeutraleOuder(ouder=o, kind=k))
        print(f"AFGELEID: {o} is ouder van {k}")

    # -----------------------------
    # Broer / Zus
    # Als X en Y kinderen zijn van dezelfde ouder O, en X is niet gelijk aan Y, dan zijn X en Y siblings.
    # -----------------------------
    @Rule(
        OuderRelatie(kind=MATCH.k1, ouder=MATCH.o),
        OuderRelatie(kind=MATCH.k2, ouder=MATCH.o),
        TEST(lambda k1, k2: k1 != k2)
    )
    def bepaal_broer_zus(self, k1, k2, o):
        self.declare(BroerZus(persoon=k1, sibling=k2))
        self.declare(BroerZus(persoon=k2, sibling=k1))
        print(f"AFGELEID: {k1} en {k2} zijn siblings")

    # -----------------------------
    # Oom / Tante
    # Als K is kind van O, en O is sibling van OT, dan is OT oom/tante van K.
    # -----------------------------
    @Rule(
        OuderRelatie(kind=MATCH.k, ouder=MATCH.o),
        BroerZus(persoon=MATCH.o, sibling=MATCH.ot)
    )
    def bepaal_oom_tante(self, k, o, ot):
        self.declare(OomTante(oom_tante=ot, kind=k))
        print(f"AFGELEID: {ot} is oom/tante van {k}")

    # -----------------------------
    # Neef / Nicht
    # Als OT is oom/tante van K, dan is K neef/nicht van OT.

    # -----------------------------
    @Rule(
        OomTante(oom_tante=MATCH.ot, kind=MATCH.k)
    )
    def bepaal_neef_nicht(self, ot, k):
        self.declare(NeefNicht(persoon=k, oom_tante=ot))
        print(f"AFGELEID: {k} is neef/nicht van {ot}")

    # -----------------------------
    # Cousins
    # Als O1 en O2 siblings zijn, en K1 is kind van O1, en K2 is kind van O2, dan zijn K1 en K2 cousins.
    # -----------------------------
    @Rule(
        OuderRelatie(kind=MATCH.k1, ouder=MATCH.o1),
        OuderRelatie(kind=MATCH.k2, ouder=MATCH.o2),
        BroerZus(persoon=MATCH.o1, sibling=MATCH.o2),
        TEST(lambda k1, k2: k1 != k2)
    )
    def bepaal_cousins(self, k1, k2, o1, o2):
        self.declare(CousinRelatie(persoon=k1, cousin=k2))
        self.declare(CousinRelatie(persoon=k2, cousin=k1))
        print(f"AFGELEID: {k1} en {k2} zijn cousins")

    # -----------------------------
    # Kleinkind
    # Als K is kind van O, en O is kind van GO, dan is K kleinkind van GO.
    # -----------------------------
    @Rule(
        OuderRelatie(kind=MATCH.k, ouder=MATCH.o),
        OuderRelatie(kind=MATCH.o, ouder=MATCH.go)
    )
    def bepaal_kleinkind(self, k, o, go):
        self.declare(Kleinkind(grootouder=go, kleinkind=k))
        print(f"AFGELEID: {k} is kleinkind van {go}")


# =========================================================
# 5. QUERY FUNCTIES
# Dit zijn hulpfuncties om specifieke relaties op te vragen

def check_kleinkind(engine, grootouder, kleinkind):
    return any(
        isinstance(f, Kleinkind)
        and f["grootouder"] == grootouder
        and f["kleinkind"] == kleinkind
        for f in engine.facts.values()
    )


def relaties_van(engine, persoon):
    return [
        f["leden"]
        for f in engine.facts.values()
        if isinstance(f, RelatieGroep) and persoon in f["leden"]
    ]



# =========================================================
# 6. HOOFDPROGRAMMA
# =========================================================

if __name__ == "__main__":

    # ----------------------------------
    # Engine initialiseren
    # ----------------------------------
    engine = FamilieRedeneerder()
    engine.reset()

    # ----------------------------------
    # Personen invoeren
    # ----------------------------------
    personen_data = [
        ("Ayham", "M"),
        ("Amal", "F"),
        ("Lama", "F"),
        ("Ahmad", "M"),
        ("Moh", "M"),
        ("Mosti", "M"),
        ("Haiat", "F"),
        ("Basel", "M"),
        ("Ali", "M"),
        ("Lmiaa", "F"),
        ("Khadiga", "F"),
        ("Tarek", "M"),
        ("Wafaa", "F"),
    ]

    for naam, geslacht in personen_data:
        engine.declare(Persoon(naam=naam, geslacht=geslacht))

    # ----------------------------------
    # Ouder-kind relaties invoeren
    # ----------------------------------
    ouder_relaties = [
        ("Ayham", "Ahmad"),
        ("Lama", "Ahmad"),
        ("Moh", "Ahmad"),
        ("Ahmad", "Khadiga"),
        ("Lama", "Amal"),
        ("Haiat", "Lmiaa"),
        ("Basel", "Lmiaa"),
        ("Amal", "Lmiaa"),
        ("Amal", "Ali"),
        ("Wafaa", "Khadiga"),
        ("Tarek", "Khadiga"),
        ("Tarek", "Mosti"),
        ("Ahmad", "Mosti"),
    ]

    for kind, ouder in ouder_relaties:
        engine.declare(OuderRelatie(kind=kind, ouder=ouder))

    # ----------------------------------
    # Relatie / huwelijk-groepen
    # ----------------------------------
    engine.declare(RelatieGroep(leden={"Ahmad", "Amal"}))
    engine.declare(RelatieGroep(leden={"Ali", "Lmiaa"}))
    engine.declare(RelatieGroep(leden={"Mosti", "Khadiga"}))

    # ----------------------------------
    # Inferentie uitvoeren
    # ----------------------------------
    engine.run()

    # ----------------------------------
    # Alle feiten tonen
    # ----------------------------------
    print("\n--- FEITEN IN HET WERKGEHEUGEN ---")
    for fact_id, fact in engine.facts.items():
        print(fact_id, fact)

    # ----------------------------------
    # Queries uitvoeren
    # ----------------------------------
    print("\n--- QUERIES ---")
    print(
        "Is Ayham een kleinkind van Mosti?",
        check_kleinkind(engine, "Mosti", "Ayham")
    )

    print(
        "Relatiegroepen van Amal:",
        relaties_van(engine, "Amal")
    )

    print(
        "Relatiegroepen van Khadiga:",
        relaties_van(engine, "Khadiga")
    )

    print(
        "Relatiegroepen van Ahmad:",
        relaties_van(engine, "Ahmad")
    )
