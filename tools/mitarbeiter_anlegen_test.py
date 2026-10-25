from funktionen_mitarbeiter import mitarbeiter_anlegen_sqlite, alle_mitarbeiter_sqlite

print(mitarbeiter_anlegen_sqlite("Max", "Muster", "musterm", "ZLB", "AECC",
                                 "207", "A603-D005", "360300", "Aktiv", "Test"))
print(alle_mitarbeiter_sqlite())