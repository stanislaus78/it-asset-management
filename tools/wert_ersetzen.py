import sqlite3

# Hier anpassen:
# TABELLE = "assets"
# SPALTE = "assettyp"
# ALT = "Microfon"
# NEU = "Mikrofon"
#
# con = sqlite3.connect("asset_management.db")
# cur = con.execute(f"UPDATE {TABELLE} SET {SPALTE} = ? WHERE {SPALTE} = ?", (NEU, ALT))
# con.commit()
# print(f"{cur.rowcount} Zeile(n) geändert")
# con.close()




# con = sqlite3.connect("asset_management.db")
# for zeile in con.execute("SELECT id, inventarnummer, assettyp FROM assets"):
#     print(zeile)
#
# cur = con.execute("UPDATE assets SET assettyp = 'Mikrofon' WHERE LOWER(assettyp) = 'microfon'")
# con.commit()
# print(cur.rowcount, "Zeile(n) geändert")
# con.close()