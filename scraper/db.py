import sqlite3
import os

DB_PATH = "data/vacantes.db"

def get_connection():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    return sqlite3.connect(DB_PATH)

def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    # Tabla principal de vacantes válidas
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS ofertas (
            id TEXT PRIMARY KEY,
            titulo TEXT,
            empresa TEXT,
            portal TEXT,
            ciudad TEXT,
            ubicacion TEXT,
            salario_texto TEXT,
            salario_num INTEGER,
            url TEXT,
            descripcion TEXT,
            nivel TEXT,
            score_keywords INTEGER,
            estado TEXT DEFAULT 'NUEVA',
            fecha_procesamiento TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    # Tabla de deduplicación histórica (todos los analizados)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS procesados (
            id TEXT PRIMARY KEY,
            fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

def guardar_ofertas_db(ofertas: list[dict]):
    """Inserta las vacantes válidas completas en SQLite."""
    if not ofertas: return
    conn = get_connection()
    cursor = conn.cursor()
    for o in ofertas:
        cursor.execute('''
            INSERT OR IGNORE INTO ofertas 
            (id, titulo, empresa, portal, ciudad, ubicacion, salario_texto, salario_num, url, descripcion, nivel, score_keywords)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            o.get('id_unico', ''), o.get('titulo', ''), o.get('empresa', ''), 
            o.get('portal', ''), o.get('ciudad', ''), o.get('ubicacion', ''), 
            o.get('salario_texto', ''), o.get('salario_num', 0), o.get('url', ''), 
            o.get('descripcion', ''), o.get('nivel', ''), o.get('score_keywords', 0)
        ))
    conn.commit()
    conn.close()
