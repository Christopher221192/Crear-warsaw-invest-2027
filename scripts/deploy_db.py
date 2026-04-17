import os
import duckdb
from dotenv import load_dotenv

load_dotenv()

def migrate():
    token = os.getenv("MOTHERDUCK_TOKEN")
    if not token:
        print("❌ Error: MOTHERDUCK_TOKEN no encontrado en .env")
        return

    local_db = "data/poland_real_estate.duckdb"
    if not os.path.exists(local_db):
        print(f"❌ Error: No se encontró la base de datos local en {local_db}")
        return

    print("🚀 Iniciando migración a MotherDuck...")
    
    try:
        # Conectar a MotherDuck
        # La sintaxis md: permite conectar a la nube
        con = duckdb.connect(f"md:?motherduck_token={token}")
        
        print("📦 Cargando datos locales...")
        # Adjuntar base de datos local
        con.execute(f"ATTACH '{local_db}' AS local_db")
        
        # Crear base de datos en la nube si no existe
        con.execute("CREATE DATABASE IF NOT EXISTS poland_listings")
        
        # Copiar tabla
        print("📤 Subiendo tabla 'listings' a la nube...")
        con.execute("CREATE OR REPLACE TABLE poland_listings.listings AS SELECT * FROM local_db.listings")
        
        print("✅ Migración completada con éxito.")
        print("🔗 Tus datos ya están disponibles en MotherDuck bajo la base de datos 'poland_listings'.")
        
    except Exception as e:
        print(f"❌ Error durante la migración: {e}")

if __name__ == "__main__":
    migrate()
