

import sqlite3

verbindung = sqlite3.connect("asset_management.db")

cursor = verbindung.cursor()
#Create
# cursor.execute("""
# CREATE TABLE IF NOT EXISTS assets (
#     inventarnummer TEXT,
#     hersteller TEXT,
#     status TEXT,
#     geraetetyp TEXT,
#     standort TEXT,
#     zimmer TEXT,
#     organisationseinheit TEXT
# )
# """)

#Instert Into
# cursor.execute("""
# INSERT INTO assets
# VALUES (
#     'LT001',
#     'Dell',
#     'Ausgegeben',
#     'Laptop',
#     'Zlb',
#     '308',
#     '602'
# )
# """)

#erbindung.commit()


#------------------------------------------------------
# Read
cursor.execute("SELECT * FROM assets")
for asset in cursor.fetchall():
    print(asset)
verbindung.commit()
#--------------------------------------------------------



#cursor.execute("SELECT * FROM assets WHERE inventarnummer = 'LT001';")

#----------------------------------------------------------------------
#Update
# cursor.execute("""
# UPDATE assets
# SET status = 'Lager'
# WHERE inventarnummer = 'LT001';
# """)

# for asset in cursor.fetchall():
#     print(asset)
# verbindung.commit()
# print("Datensatz hinzugefügt")
#verbindung.commit()
#------------------------------------------------------------------------




#----------------------------------------------------------------------------
#Delete
# cursor.execute("""
# DELETE FROM assets
# WHERE inventarnummer = 'LT001';
# """)
# cursor.execute("SELECT * FROM assets")
# for asset in cursor.fetchall():
#     print(asset)
# #verbindung.commit()
#------------------------------------------------------------------------------


#cursor.execute("SELECT * FROM assets")

#daten = cursor.fetchall()

#print(daten)


verbindung.close()
