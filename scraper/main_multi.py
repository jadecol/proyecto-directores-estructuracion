import os
import time
import pandas as pd
from datetime import datetime
from playwright.sync_api import sync_playwright

# Importaciones de los portales
from .portales.magneto import buscar_magneto
from .portales.computrabajo import buscar_computrabajo
from .portales.elempleo import buscar_elempleo
from .portales.linkedin import buscar_linkedin

# Importaciones de lógica de negocio y utilidades
from .filtro_robusto import filtrar_cargo_robusto
from .deduplicacion import cargar_procesados, guardar_procesados, generar_id_unico
from .db import guardar_ofertas_db
from .dashboard_generator import generar_dashboard

# -----------------------------------------------------------------------
# Configuración de búsquedas
# -----------------------------------------------------------------------
CIUDADES_OBJETIVO = [
    "Bogota", 
    "Cali", 
    "Medellin", 
    "Pereira", 
    "Manizales", 
    "Armenia"
]

TITULOS_OBJETIVO = [
    "Director de nuevos proyectos",
    "Gerente de nuevos proyectos",
    "Director de desarrollo inmobiliario",
    "Gerente de estructuracion",
    "Viabilidad de lotes",
    "Cabidas arquitectonicas",
    "Norma urbana",
    "Estructuracion de proyectos inmobiliarios"
]

def main():
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Iniciando Scraper Multi-Portal...")
    cargos_crudos_total = []

    # -----------------------------------------------------------------------
    # 1. Extracción de Datos
    # -----------------------------------------------------------------------
    with sync_playwright() as p:
        # Iniciar navegador Chromium (Headless)
        browser = p.chromium.launch(headless=True)
        pw_context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            extra_http_headers={"Accept-Language": "es-ES,es;q=0.9"}
        )
        
        for ciudad in CIUDADES_OBJETIVO:
            for titulo in TITULOS_OBJETIVO:
                print(f"\n[*] Buscando: '{titulo}' en {ciudad}")
                
                # 1. CompuTrabajo
                try:
                    print("  -> Consultando CompuTrabajo...")
                    res_ct = buscar_computrabajo(titulo, ciudad)
                    for r in res_ct: r['portal'] = 'computrabajo'
                    cargos_crudos_total.extend(res_ct)
                except Exception as e:
                    print(f"  [X] Error en CompuTrabajo: {e}")
                    
                # 2. Magneto
                try:
                    print("  -> Consultando Magneto...")
                    res_mg = buscar_magneto(titulo, ciudad, pw_context)
                    for r in res_mg: r['portal'] = 'magneto'
                    cargos_crudos_total.extend(res_mg)
                except Exception as e:
                    print(f"  [X] Error en Magneto: {e}")
                    
                # 3. ElEmpleo
                try:
                    print("  -> Consultando ElEmpleo...")
                    res_ee = buscar_elempleo(titulo, ciudad)
                    for r in res_ee: r['portal'] = 'elempleo'
                    cargos_crudos_total.extend(res_ee)
                except Exception as e:
                    print(f"  [X] Error en ElEmpleo: {e}")
                    
                # 4. LinkedIn
                try:
                    print("  -> Consultando LinkedIn...")
                    res_li = buscar_linkedin(titulo, ciudad)
                    for r in res_li: r['portal'] = 'linkedin'
                    cargos_crudos_total.extend(res_li)
                except Exception as e:
                    print(f"  [X] Error en LinkedIn: {e}")
                    
                time.sleep(2) # Pausa ligera entre iteraciones

        browser.close()

    print(f"\n[!] Extracción finalizada. Total crudos: {len(cargos_crudos_total)}")

    # -----------------------------------------------------------------------
    # 2. Deduplicación y Filtrado
    # -----------------------------------------------------------------------
    print("============================================================")
    print("FILTRADO, VALIDACIÓN Y DEDUPLICACIÓN HISTÓRICA:")
    print("============================================================")
    
    data_ok = []
    data_desc = []
    nuevos_ids_procesados = set()
    historial_vistos = cargar_procesados()

    for cargo in cargos_crudos_total:
        cargo_id = generar_id_unico(cargo)
        if cargo_id in historial_vistos:
            continue # Ignorar si ya fue procesado en dias anteriores
            
        nuevos_ids_procesados.add(cargo_id)
        
        filtrado, motivo = filtrar_cargo_robusto(cargo)
        if filtrado:
            filtrado['id_unico'] = cargo_id
            data_ok.append(filtrado)
        else:
            data_desc.append({
                "titulo": cargo.get("titulo", ""),
                "empresa": cargo.get("empresa", ""),
                "portal": cargo.get("portal", ""),
                "ciudad": cargo.get("ciudad", ""),
                "salario_text": cargo.get("salario_texto", "") or cargo.get("salario_text", ""),
                "motivo_descarte": motivo,
                "url": cargo.get("url", ""),
            })

    # Guardar los nuevos IDs para no volverlos a evaluar mañana
    if nuevos_ids_procesados:
        guardar_procesados(nuevos_ids_procesados)

    print(f"[*] Válidos: {len(data_ok)} | Descartados: {len(data_desc)}")

    # -----------------------------------------------------------------------
    # 3. Ordenamiento y Exportación
    # -----------------------------------------------------------------------
    df_ok = pd.DataFrame(data_ok)
    df_desc = pd.DataFrame(data_desc) if data_desc else pd.DataFrame()

    if not df_ok.empty:
        df_ok = df_ok.drop_duplicates(subset=["titulo", "empresa"])
        orden_nivel = {"PREMIUM": 0, "ALTO": 1, "MEDIO": 2}
        df_ok["orden"] = df_ok.get("nivel", pd.Series(["MEDIO"] * len(df_ok))).map(orden_nivel).fillna(2)
        df_ok = df_ok.sort_values(
            by=["orden", "score_keywords", "salario_num"],
            ascending=[True, False, False]
        )
        df_ok = df_ok.drop(columns=["orden", "descripcion_completa", "card_text"], errors="ignore")

    timestamp = datetime.now().strftime('%Y%m%d_%H%M')
    os.makedirs("data", exist_ok=True)

    # Exportar PREMIUM/ALTO
    df_premium = df_ok[df_ok["nivel"].isin(["PREMIUM", "ALTO"])] if not df_ok.empty else df_ok
    file_premium = f"data/PREMIUM_multi_{timestamp}.xlsx"
    if not df_premium.empty:
        df_premium.to_excel(file_premium, index=False)
    else:
        pd.DataFrame([{"info": "Sin premium hoy"}]).to_excel(file_premium, index=False)

    # Exportar TODOS
    file_todos = f"data/TODOS_multi_{timestamp}.xlsx"
    if not df_ok.empty:
        df_ok.to_excel(file_todos, index=False)
    else:
        pd.DataFrame([{"info": "Sin resultados hoy"}]).to_excel(file_todos, index=False)

    # Exportar DESCARTADOS
    file_descartados = f"data/DESCARTADOS_multi_{timestamp}.xlsx"
    if not df_desc.empty:
        df_desc.to_excel(file_descartados, index=False)

    print(f"\n[OK] Generación de archivos completa:")
    print(f" - {file_premium}")
    print(f" - {file_todos}")
    print(f" - {file_descartados}")

    # Guardar en SQLite
    if data_ok:
        guardar_ofertas_db(data_ok)
        print("[OK] Datos guardados en SQLite (data/vacantes.db)")

    # Disparar Generación de Dashboard
    generar_dashboard()

if __name__ == "__main__":
    main()
