"""
Reporte para Aplicar - Director de Estructuración
Lee el archivo TODOS_multi_ más reciente y genera un reporte Excel simplificado
para seguimiento de postulaciones, con la URL directa y la carta de presentación sugerida.
"""
import glob
import os
from datetime import datetime
import pandas as pd

def generar_reporte_aplicar():
    # Buscar el último TODOS_multi_*.xlsx
    archivos_todos = glob.glob("data/TODOS_multi_*.xlsx")
    if not archivos_todos:
        print("No se encontró ningún archivo TODOS_multi_*.xlsx en data/")
        return

    archivo_reciente = max(archivos_todos, key=os.path.getctime)
    print(f"Generando reporte a partir de: {archivo_reciente}")

    df = pd.read_excel(archivo_reciente)
    if df.empty:
        print("El archivo está vacío.")
        return

    # Preparar datos para el reporte
    reporte_data = []
    for _, row in df.iterrows():
        titulo = str(row.get("titulo", "")).strip()
        empresa = str(row.get("empresa", "")).strip()
        portal = str(row.get("portal", "")).strip()
        url = str(row.get("url", "")).strip()
        
        # Limpiar URL para asegurar que sea directa (ya limpia en scraper, pero por si acaso)
        url_limpia = url.split("?")[0] if url else ""

        # Carta sugerida
        carta = (
            f"Estimados {empresa}, vi su vacante de {titulo} en {portal.capitalize()}, "
            f"tengo experiencia en factibilidad técnica, compra de lotes, estructuración de nuevos proyectos "
            f"y gestión inmobiliaria. Me gustaría postularme para aportar a sus objetivos."
        )

        reporte_data.append({
            "Empresa": empresa,
            "Título": titulo,
            "Ciudad": str(row.get("ciudad", "")),
            "Salario": str(row.get("salario_text", "")),
            "Portal": portal,
            "URL Vacante": url_limpia,
            "URL Búsqueda": str(row.get("url_busqueda", "")),
            "Score": row.get("score_keywords", 0),
            "Nivel": str(row.get("nivel", "")),
            "Fecha Publicación": str(row.get("estado_activo", "")),
            "Estado": "Nuevo",  # Nuevo / Por Aplicar / Aplicado
            "Carta Sugerida": carta,
            "Keywords Match": str(row.get("keywords_encontradas", ""))
        })

    df_reporte = pd.DataFrame(reporte_data)
    
    # Ordenar: primero PREMIUM, luego ALTO, luego MEDIO, y por Score
    orden_nivel = {"PREMIUM": 0, "ALTO": 1, "MEDIO": 2}
    df_reporte["orden_temp"] = df_reporte["Nivel"].map(orden_nivel).fillna(99)
    df_reporte = df_reporte.sort_values(by=["orden_temp", "Score"], ascending=[True, False])
    df_reporte = df_reporte.drop(columns=["orden_temp"])

    # Guardar Excel y CSV
    timestamp = datetime.now().strftime("%Y%m%d")
    out_excel = f"data/reporte_aplicar_{timestamp}.xlsx"
    out_csv = f"data/reporte_aplicar_{timestamp}.csv"

    df_reporte.to_excel(out_excel, index=False)
    df_reporte.to_csv(out_csv, index=False, encoding="utf-8-sig")

    print(f"Reporte generado exitosamente:")
    print(f" - {out_excel}")
    print(f" - {out_csv}")

if __name__ == "__main__":
    generar_reporte_aplicar()
