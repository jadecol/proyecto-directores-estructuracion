import os
from .db import get_connection, init_db

# Asegurar que las tablas existan antes de cualquier operación
init_db()

def cargar_procesados() -> set:
    """Carga los identificadores de vacantes procesadas en días anteriores desde SQLite."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM procesados")
    resultados = {row[0] for row in cursor.fetchall()}
    conn.close()
    return resultados

def guardar_procesados(nuevos_procesados: set):
    """Guarda nuevos identificadores evaluados en la base de datos."""
    if not nuevos_procesados: return
    
    conn = get_connection()
    cursor = conn.cursor()
    cursor.executemany("INSERT OR IGNORE INTO procesados (id) VALUES (?)", [(uid,) for uid in nuevos_procesados])
    conn.commit()
    conn.close()

def generar_id_unico(cargo: dict) -> str:
    """Genera un ID determinista usando la URL limpia o Título+Empresa."""
    url = cargo.get("url", "")
    if url and url.startswith("http"):
        return url.split("?")[0] 
    
    titulo = cargo.get("titulo", "").strip().lower()
    empresa = cargo.get("empresa", "").strip().lower()
    return f"{titulo}||{empresa}"
