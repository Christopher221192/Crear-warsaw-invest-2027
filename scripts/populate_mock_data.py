import duckdb
import os

def populate():
    # Asegurarse de que el directorio data existe
    if not os.path.exists("data"):
        os.makedirs("data")

    db_path = "data/poland_real_estate.duckdb"
    con = duckdb.connect(db_path)
    
    # Insertar algunos datos de prueba para 2027 (Solo Varsovia)
    mock_listings = [
        # Varsovia
        ("OT-101", "otodom", "https://www.otodom.pl/pl/oferta/nowoczesne-2-pokoje-2027-ID4abc.html", "warszawa", "Białołęka", "Dom Development", 650000, 14444, 45, 2, 1, 4, "Q1 2027", "Phase 1", 52.33, 20.95),
        ("OT-102", "otodom", "https://www.otodom.pl/pl/oferta/mokotow-premium-2027-ID5xyz.html", "warszawa", "Mokotów", "Murapol", 1100000, 18965, 58, 3, 3, 6, "Q2 2027", "Central", 52.18, 21.01),
        ("OT-103", "otodom", "https://www.otodom.pl/pl/oferta/ursynow-blisko-metro-2027-ID6def.html", "warszawa", "Ursynów", "Robyg", 850000, 17000, 50, 2, 2, 5, "Q1 2027", "Parkowa 2", 52.14, 21.04),
        ("OT-104", "otodom", "https://www.otodom.pl/pl/oferta/praga-polnoc-loft-2027-ID7ghi.html", "warszawa", "Praga-Północ", "Atal", 920000, 18400, 50, 2, 4, 8, "Q2 2027", "Port Praski", 52.25, 21.03),
        ("OT-105", "otodom", "https://www.otodom.pl/pl/oferta/wola-business-center-2027-ID8jkl.html", "warszawa", "Wola", "Skanska", 1250000, 25000, 50, 2, 10, 15, "Q1 2027", "Skyline", 52.23, 20.98)
    ]
    
    for row in mock_listings:
        con.execute("""
            INSERT OR REPLACE INTO listings 
            (id, portal, url, city, district, developer, price_pln_gross, price_per_sqm, area_sqm, rooms, floor, total_floors, delivery_date, phase, lat, lon)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, row)
    
    print(f"✅ Se han insertado {len(mock_listings)} registros de prueba en {db_path}")
    con.close()

if __name__ == "__main__":
    populate()
