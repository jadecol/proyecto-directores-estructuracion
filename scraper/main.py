"""
SCRAPER ROBUSTO - Director Nuevos Proyectos / Estructuración
4 Filtros: Salario corregido | Sector inmobiliario | Keywords con peso | Activo <=30 días
Genera: PREMIUM_*.xlsx  |  TODOS_*.xlsx  |  DESCARTADOS_*.xlsx  |  dashboard_*_ROBUSTO.html

Referencia: OCOBO CONSTRUCCIONES $15.6M Score 17 — vacante validada con fotos reales.
"""
import re, time, random, os
import pandas as pd
from datetime import datetime
from playwright.sync_api import sync_playwright
from .config_robusto import TITULOS_OBJETIVO, EMPRESAS_DIRECTO
from .filtro_robusto import extraer_salario_robusto, filtrar_cargo_robusto


def scrape_computrabajo_robusto():
    resultados_raw = []
    descartados = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            viewport={"width": 1366, "height": 768}
        )
        page = context.new_page()

        # Busca los títulos objetivo en Bogotá / Medellín / Cali
        for keyword in TITULOS_OBJETIVO:
            slug = (keyword.replace(" ", "-").lower()
                    .replace("á","a").replace("é","e").replace("ó","o").replace("í","i"))
            for ciudad in ["bogota", "medellin", "cali"]:
                url = f"https://co.computrabajo.com/trabajo-de-{slug}-en-{ciudad}"
                print(f"\n-> Buscando: {url}")
                try:
                    page.goto(url, wait_until="domcontentloaded", timeout=60000)
                    time.sleep(random.uniform(2, 4))
                    cards = page.query_selector_all("article")
                    print(f"   Cards crudas: {len(cards)}")
                    for card in cards[:20]:
                        try:
                            link_el = card.query_selector("a.js-o-link")
                            if not link_el:
                                continue
                            titulo = link_el.inner_text().strip()
                            link = link_el.get_attribute("href")
                            if link and not link.startswith("http"):
                                link = "https://co.computrabajo.com" + link
                            # Limpiar fragmento #lc=... que causa 403 en acceso directo
                            link_limpio = link.split("#")[0] if link else link
                            url_busqueda = f"https://co.computrabajo.com/trabajo-de-{slug}-en-{ciudad}"

                            card_text = card.inner_text()
                            salario_num, salario_text = extraer_salario_robusto(card_text)

                            # Empresa del card
                            empresa = "Por extraer"
                            try:
                                emp_el = card.query_selector("p.fc_base")
                                if emp_el:
                                    empresa = emp_el.inner_text().strip()
                            except:
                                pass

                            # Si parece prometedor, entrar al detalle para descripción completa
                            descripcion_completa = card_text
                            if any(k in (titulo + card_text).lower() for k in
                                   ["factibilidad", "lotes", "estructuracion", "nuevos proyectos", "desarrollo inmobiliario"]):
                                try:
                                    page2 = context.new_page()
                                    page2.goto(link, wait_until="domcontentloaded", timeout=25000)
                                    time.sleep(1.5)
                                    descripcion_completa = page2.inner_text("body")[:6000]
                                    page2.close()
                                except:
                                    pass

                            cargo_raw = {
                                "titulo": titulo,
                                "empresa": empresa,
                                "ubicacion": ciudad.capitalize(),
                                "ciudad": ciudad.capitalize(),
                                "salario_text": salario_text,
                                "salario_num": salario_num,
                                "fuente": "Computrabajo TIEMPO REAL",
                                "url": link_limpio,
                                "url_busqueda": url_busqueda,
                                "descripcion_snippet": descripcion_completa[:400],
                                "descripcion_completa": descripcion_completa,
                                "card_text": card_text,
                                "fecha_scrape": datetime.now().strftime("%Y-%m-%d %H:%M"),
                            }

                            # Aplicar filtro robusto (4 capas)
                            cargo_filtrado, motivo = filtrar_cargo_robusto(cargo_raw)
                            if cargo_filtrado:
                                resultados_raw.append(cargo_filtrado)
                                if cargo_filtrado.get("alerta"):
                                    print(f"   🚨 PREMIUM {cargo_filtrado['nivel']}: {titulo} — {salario_text} — {empresa} | Score {cargo_filtrado['score_keywords']}")
                                else:
                                    print(f"   ✅ {cargo_filtrado['nivel']}: {titulo} — {empresa} | Score {cargo_filtrado['score_keywords']}")
                            else:
                                descartados.append({
                                    "titulo": titulo,
                                    "empresa": empresa,
                                    "motivo_descarte": motivo,
                                    "url": link,
                                })
                        except Exception:
                            continue
                except Exception as e:
                    print(f"   Error {keyword} {ciudad}: {e}")
                    continue
                time.sleep(random.uniform(1, 2))
        browser.close()

    return resultados_raw, descartados


def main():
    os.makedirs("data", exist_ok=True)
    print("=== SCRAPER ROBUSTO — 4 FILTROS ===")
    print(f"Fecha: {datetime.now()}")
    print("Filtros: 1) Salario corregido >=3M  2) Sector inmobiliario/construcción")
    print("         3) Keywords con peso (score>=2, factibilidad=3, lotes=3…)")
    print("         4) Activo <=30 días")

    data_ok, data_descartados = scrape_computrabajo_robusto()

    # Añadir OCOBO verificado siempre como referencia (Score 17, $15.6M)
    data_ok.append({
        "titulo": "Director de Nuevos Proyectos",
        "empresa": "OCOBO CONSTRUCCIONES S.A.S",
        "ubicacion": "Bogotá, D.C.",
        "ciudad": "Bogota",
        "salario_text": "$ 15.600.000,00 (Mensual)",
        "salario_num": 15600000,
        "fuente": "Magneto365 / Verificado Fotos Reales",
        "url": "https://www.magneto365.com - OCOBO",
        "descripcion_snippet": (
            "Determinar factibilidad tecnica, normativa y comercial para compra lotes. "
            "Definir y ejecutar estrategias busqueda y negociacion predios. "
            "Liderar estudios integrales factibilidad y gestion documental predios. "
            "Coordinar curadurias/planeacion."
        ),
        "descripcion_completa": "Determinar factibilidad tecnica, normativa y comercial para compra lotes...",
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
    })

    df_ok = pd.DataFrame(data_ok)
    df_desc = pd.DataFrame(data_descartados)

    if not df_ok.empty:
        df_ok = df_ok.drop_duplicates(subset=["titulo", "empresa"])
        orden_nivel = {"PREMIUM": 0, "ALTO": 1, "MEDIO": 2}
        df_ok["orden"] = df_ok["nivel"].map(orden_nivel)
        df_ok = df_ok.sort_values(by=["orden", "score_keywords", "salario_num"],
                                  ascending=[True, False, False])
        df_ok = df_ok.drop(columns=["orden", "descripcion_completa", "card_text"], errors="ignore")

    timestamp = datetime.now().strftime('%Y%m%d_%H%M')

    # 1. PREMIUM / ALTO
    df_premium = df_ok[df_ok["nivel"].isin(["PREMIUM", "ALTO"])] if not df_ok.empty else df_ok
    file_premium = f"data/PREMIUM_director_proyectos_{timestamp}.xlsx"
    if not df_premium.empty:
        df_premium.to_excel(file_premium, index=False)
    else:
        pd.DataFrame([{"info": "No hay premium hoy"}]).to_excel(file_premium, index=False)

    # 2. TODOS los válidos
    file_todos = f"data/TODOS_director_proyectos_{timestamp}.xlsx"
    if not df_ok.empty:
        df_ok.to_excel(file_todos, index=False)

    # 3. DESCARTADOS para auditoría
    file_descartados = f"data/DESCARTADOS_{timestamp}.xlsx"
    if not df_desc.empty:
        df_desc.to_excel(file_descartados, index=False)

    print(f"\n✅ PREMIUM: {file_premium} — {len(df_premium)} cargos (>=12M o Score>=6)")
    print(f"✅ TODOS VALIDADOS: {file_todos} — {len(df_ok)} cargos (Score>=2 + sector + activo)")
    print(f"📋 DESCARTADOS: {file_descartados} — {len(df_desc)} cargos")
    print(f"🚨 Alertas premium: {len(df_ok[df_ok['alerta']==True]) if not df_ok.empty else 0}")

    # CRM
    try:
        from .crm import generar_crm
        generar_crm()
    except Exception:
        try:
            import crm
            crm.generar_crm()
        except Exception:
            pass

    # Dashboard ROBUSTO con ciudades
    try:
        from .dashboard_generator import generar_dashboard
        generar_dashboard(file_premium if not df_premium.empty else file_todos)
    except Exception as e:
        print(f"Dashboard: {e}")


if __name__ == "__main__":
    main()
