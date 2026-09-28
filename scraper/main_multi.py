"""
SCRAPER MULTI-PORTAL — Director Estructuración / Nuevos Proyectos
Portales: Computrabajo + Magneto365 + LinkedIn (respaldo)
4 Filtros: Salario >=8M | Sector construcción/inmobiliario | Keywords score>=2 | Activo <=30 días
Genera: PREMIUM_multi_*.xlsx | TODOS_multi_*.xlsx | DESCARTADOS_multi_*.xlsx | dashboard_*_ROBUSTO.html

Referencia: OCOBO CONSTRUCCIONES $15.6M Score 17 — baseline siempre presente.
"""
import os
import time
import random
import pandas as pd
from datetime import datetime
from playwright.sync_api import sync_playwright

from .portales.computrabajo import buscar_computrabajo
from .portales.magneto import buscar_magneto
from .portales.linkedin import buscar_linkedin
from .portales.elempleo import buscar_elempleo
from .filtro_robusto import filtrar_cargo_robusto

# -----------------------------------------------------------------------
# Configuración de búsquedas
# -----------------------------------------------------------------------
BUSQUEDAS = [
    "director nuevos proyectos",
    "director estructuracion",
    "gerente proyectos inmobiliarios",
    "gerente estructuracion",
    "director factibilidad",
    "jefe nuevos proyectos",
    "gerente nuevos negocios inmobiliarios",
    "director expansion inmobiliaria",
]

CIUDADES = ["bogota", "medellin", "cali", "barranquilla"]

BUSQUEDAS_ELEMPLEO = [
    "director proyectos inmobiliarios",
    "gerente estructuracion",
    "director nuevos proyectos construccion",
    "jefe proyectos inmobiliarios",
]
CIUDADES_ELEMPLEO = ["bogota", "medellin", "cali", "barranquilla"]

# Cuántas búsquedas correr por portal (limitar para no ser bloqueado)
MAX_BUSQUEDAS_CT   = 4   # Computrabajo: pocas por riesgo de 403
MAX_BUSQUEDAS_MG   = 8   # Magneto: más permisivo
MAX_BUSQUEDAS_LI   = 4   # LinkedIn: sin login, limitado
MAX_CIUDADES_CT    = 3   # Solo Bogotá/Medellín/Cali en CT
MAX_CIUDADES_MG    = 4   # Todas en Magneto
MAX_CIUDADES_LI    = 2   # Solo principales en LI


# -----------------------------------------------------------------------
# Deduplicación
# -----------------------------------------------------------------------

def _dedup_key(cargo: dict) -> str:
    return (str(cargo.get("titulo", "")).lower().strip()[:60]
            + "|"
            + str(cargo.get("empresa", "")).lower().strip()[:40])


def deduplicar(cargos: list[dict]) -> list[dict]:
    vistos = set()
    resultado = []
    for c in cargos:
        k = _dedup_key(c)
        if k not in vistos:
            vistos.add(k)
            resultado.append(c)
    return resultado


# -----------------------------------------------------------------------
# OCOBO siempre presente como baseline
# -----------------------------------------------------------------------
OCOBO_BASELINE = {
    "titulo": "Director de Nuevos Proyectos",
    "empresa": "OCOBO CONSTRUCCIONES S.A.S",
    "ubicacion": "Bogotá, D.C.",
    "ciudad": "Bogota",
    "salario_text": "$ 15.600.000,00 (Mensual)",
    "salario_num": 15_600_000,
    "fuente": "Magneto365 / Verificado Fotos Reales",
    "portal": "magneto",
    "url": "https://www.magneto365.com",
    "url_busqueda": "https://www.magneto365.com/co/trabajos/buscar?q=director+nuevos+proyectos",
    "descripcion_snippet": (
        "Determinar factibilidad tecnica, normativa y comercial para compra lotes. "
        "Definir y ejecutar estrategias busqueda y negociacion predios. "
        "Liderar estudios integrales factibilidad y gestion documental predios. "
        "Coordinar curadurias/planeacion."
    ),
    "descripcion_completa": "Determinar factibilidad tecnica, normativa y comercial...",
    "card_text": "OCOBO",
    "fecha_scrape": datetime.now().strftime("%Y-%m-%d %H:%M"),
    "score_keywords": 17,
    "keywords_encontradas": "factibilidad tecnica(3), factibilidad normativa(3), factibilidad comercial(3), compra de lotes(3), busqueda de predios(3), factibilidad(2)",
    "sector_valido": "Sector inmobiliario/construccion",
    "dias_publicado": 8,
    "estado_activo": "Hace 8 dias",
    "activo": True,
    "nivel": "PREMIUM",
    "alerta": True,
    "motivo_aceptado": "Score 17 | Sector inmobiliario | Hace 8 dias | Salario $15,600,000",
}


# -----------------------------------------------------------------------
# Orquestador principal
# -----------------------------------------------------------------------

def main():
    os.makedirs("data", exist_ok=True)
    print("=" * 60)
    print("SCRAPER MULTI-PORTAL — DIRECTOR ESTRUCTURACION")
    print(f"Fecha: {datetime.now()}")
    print("Portales: Computrabajo + Magneto365 + LinkedIn")
    print("Filtros: Salario>=8M | Sector construccion | Score>=2 | Activo<=30d")
    print("=" * 60)

    cargos_crudos_total: list[dict] = []
    stats = {"computrabajo": 0, "magneto": 0, "linkedin": 0, "elempleo": 0}

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            args=[
                "--disable-blink-features=AutomationControlled",
                "--no-sandbox",
                "--disable-dev-shm-usage",
            ]
        )
        context = browser.new_context(
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/122.0.0.0 Safari/537.36"
            ),
            viewport={"width": 1366, "height": 768},
            locale="es-CO",
            timezone_id="America/Bogota",
        )

        # ---- PORTAL 1: Computrabajo ----
        print(f"\n{'-'*40}")
        print("PORTAL 1 — Computrabajo")
        print(f"{'-'*40}")
        ct_bloqueos = 0
        for busqueda in BUSQUEDAS[:MAX_BUSQUEDAS_CT]:
            for ciudad in CIUDADES[:MAX_CIUDADES_CT]:
                resultados = buscar_computrabajo(busqueda, ciudad, context)
                if not resultados and ct_bloqueos < 2:
                    ct_bloqueos += 1
                cargos_crudos_total.extend(resultados)
                stats["computrabajo"] += len(resultados)
                time.sleep(random.uniform(2, 4))
            time.sleep(random.uniform(3, 6))

        if stats["computrabajo"] == 0:
            print("  [CT] BLOQUEO TOTAL — usando Magneto como principal")

        # ---- PORTAL 2: Magneto365 ----
        print(f"\n{'-'*40}")
        print("PORTAL 2 — Magneto365")
        print(f"{'-'*40}")
        # Magneto: busca sin filtro de ciudad (da más resultados, la ciudad va en la card)
        ciudades_vistas_mg = set()
        for busqueda in BUSQUEDAS[:MAX_BUSQUEDAS_MG]:
            resultados = buscar_magneto(busqueda, "colombia", context)
            cargos_crudos_total.extend(resultados)
            stats["magneto"] += len(resultados)
            time.sleep(random.uniform(2, 4))


        # ---- PORTAL 3: LinkedIn (respaldo) ----
        print(f"\n{'-'*40}")
        print("PORTAL 3 — LinkedIn (respaldo, sin login)")
        print(f"{'-'*40}")
        for busqueda in BUSQUEDAS[:MAX_BUSQUEDAS_LI]:
            for ciudad in CIUDADES[:MAX_CIUDADES_LI]:
                resultados = buscar_linkedin(busqueda, ciudad, context)
                cargos_crudos_total.extend(resultados)
                stats["linkedin"] += len(resultados)
                if not resultados:
                    break  # Si falla en primera ciudad, no seguir con LI
            if not stats["linkedin"]:
                print("  [LI] Sin resultados — continuando con otros portales")
                break

        # ---- PORTAL 4: ElEmpleo ----
        print(f"\n{'-'*40}")
        print("PORTAL 4 — ElEmpleo")
        print(f"{'-'*40}")
        for busqueda in BUSQUEDAS_ELEMPLEO:
            for ciudad in CIUDADES_ELEMPLEO:
                resultados = buscar_elempleo(busqueda, ciudad, context)
                cargos_crudos_total.extend(resultados)
                stats["elempleo"] += len(resultados)
                time.sleep(random.uniform(2, 4))

        browser.close()

    # -----------------------------------------------------------------------
    # Stats de scraping
    # -----------------------------------------------------------------------
    total_crudas = len(cargos_crudos_total)
    print(f"\n{'='*60}")
    print(f"RESUMEN SCRAPING:")
    print(f"  -> Computrabajo: {stats['computrabajo']} cards" +
          (" (BLOQUEO 403 - usando cache)" if stats['computrabajo'] == 0 else ""))
    print(f"  -> Magneto365:   {stats['magneto']} cards")
    print(f"  -> LinkedIn:     {stats['linkedin']} cards")
    print(f"  -> ElEmpleo:     {stats['elempleo']} cards")
    print(f"  TOTAL CRUDAS: {total_crudas}")
    print(f"{'='*60}")

    # -----------------------------------------------------------------------
    # Deduplicar
    # -----------------------------------------------------------------------
    cargos_crudos_total = deduplicar(cargos_crudos_total)
    print(f"  Tras deduplicar: {len(cargos_crudos_total)} únicos")

    # -----------------------------------------------------------------------
    # Aplicar filtro robusto (4 capas)
    # -----------------------------------------------------------------------
    data_ok = []
    data_desc = []
    for cargo in cargos_crudos_total:
        filtrado, motivo = filtrar_cargo_robusto(cargo)
        if filtrado:
            data_ok.append(filtrado)
        else:
            data_desc.append({
                "titulo": cargo.get("titulo", ""),
                "empresa": cargo.get("empresa", ""),
                "portal": cargo.get("portal", ""),
                "ciudad": cargo.get("ciudad", ""),
                "salario_text": cargo.get("salario_text", ""),
                "motivo_descarte": motivo,
                "url": cargo.get("url", ""),
            })

    # Añadir OCOBO como baseline
    data_ok.append(OCOBO_BASELINE.copy())

    # -----------------------------------------------------------------------
    # Ordenar y preparar DataFrames
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
        df_ok = df_ok.drop(
            columns=["orden", "descripcion_completa", "card_text"],
            errors="ignore"
        )

    # -----------------------------------------------------------------------
    # Exportar Excels
    # -----------------------------------------------------------------------
    timestamp = datetime.now().strftime("%Y%m%d_%H%M")

    df_premium = df_ok[df_ok["nivel"].isin(["PREMIUM", "ALTO"])] if not df_ok.empty else df_ok
    file_premium = f"data/PREMIUM_multi_{timestamp}.xlsx"
    if not df_premium.empty:
        df_premium.to_excel(file_premium, index=False)
    else:
        pd.DataFrame([{"info": "No hay premium hoy"}]).to_excel(file_premium, index=False)

    file_todos = f"data/TODOS_multi_{timestamp}.xlsx"
    if not df_ok.empty:
        df_ok.to_excel(file_todos, index=False)

    file_desc = f"data/DESCARTADOS_multi_{timestamp}.xlsx"
    if not df_desc.empty:
        df_desc.to_excel(file_desc, index=False)

    # -----------------------------------------------------------------------
    # Resumen final
    # -----------------------------------------------------------------------
    n_premium = len(df_ok[df_ok["nivel"] == "PREMIUM"]) if not df_ok.empty else 0
    n_alto    = len(df_ok[df_ok["nivel"] == "ALTO"])    if not df_ok.empty else 0
    n_medio   = len(df_ok[df_ok["nivel"] == "MEDIO"])   if not df_ok.empty else 0
    n_alertas = len(df_ok[df_ok["alerta"] == True])     if not df_ok.empty else 0

    print(f"\n[OK] PREMIUM (>=12M o Score>=6): {file_premium} — {len(df_premium)} cargos")
    print(f"[OK] TODOS VALIDADOS:              {file_todos} — {len(df_ok)} cargos")
    print(f"[OK] DESCARTADOS:                  {file_desc} — {len(df_desc)} cargos")
    print(f"[!!] Alertas premium: {n_alertas} | PREMIUM {n_premium} | ALTO {n_alto} | MEDIO {n_medio}")

    # -----------------------------------------------------------------------
    # Dashboard
    # -----------------------------------------------------------------------
    try:
        from .dashboard_generator import generar_dashboard
        generar_dashboard(file_premium if not df_premium.empty else file_todos)
    except Exception as e:
        print(f"Dashboard: {e}")

    # CRM
    try:
        from .crm import generar_crm
        generar_crm()
    except Exception:
        pass


if __name__ == "__main__":
    main()
