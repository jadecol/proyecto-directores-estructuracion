"""
Portal: LinkedIn Jobs (Guest API)
URL: https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search?keywords={query}&location={ciudad}
Si pide login, usa el endpoint guest que retorna HTML con los resultados.
"""
import time
import random
import re
from datetime import datetime
from ..filtro_robusto import extraer_salario_robusto

_CIUDAD_LI = {
    "bogota": "Bogota",
    "medellin": "Medellin",
    "cali": "Cali",
    "barranquilla": "Barranquilla",
}

def buscar_linkedin(busqueda: str, ciudad: str, pw_context) -> list[dict]:
    """
    Busca en LinkedIn Jobs. Intenta la vista normal, si hay login wall
    usa el endpoint guest de paginación que es más abierto.
    """
    resultados = []
    q = busqueda.replace(" ", "%20")
    loc = _CIUDAD_LI.get(ciudad.lower(), ciudad.replace(" ", "%20"))
    
    # URL normal
    url_search = f"https://www.linkedin.com/jobs/search/?keywords={q}&location={loc}%2C%20Colombia&f_TPR=r2592000"
    # URL guest API (devuelve fragmentos de HTML)
    url_guest = f"https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search?keywords={q}&location={loc}&start=0"

    page = pw_context.new_page()
    try:
        print(f"  [LI] Intentando: {url_search}")
        page.goto(url_search, wait_until="domcontentloaded", timeout=45_000)
        time.sleep(random.uniform(3, 5))

        # Detectar login wall
        current = page.url
        body_text = page.inner_text("body")
        if "login" in current or "authwall" in current or "checkpoint" in current or "iniciar sesión" in body_text.lower() or "sign in" in body_text.lower():
            print(f"  [LI] Login wall detectado — usando Guest API...")
            page.goto(url_guest, wait_until="domcontentloaded", timeout=45_000)
            time.sleep(random.uniform(2, 4))
            
        SELECTORES = [
            "div.job-search-card",
            "li.jobs-search-results__list-item",
            "div[data-entity-urn]",
            "article[data-occludable-job-id]",
            "ul.jobs-search__results-list li",
            "li", # para la guest API
        ]

        cards = []
        for sel in SELECTORES:
            try:
                found = page.query_selector_all(sel)
                if found and len(found) > 0:
                    cards = found
                    break
            except Exception:
                continue

        if not cards:
            print(f"  [LI] 0 cards estructuradas en {ciudad}")
            return []

        print(f"  [LI] {len(cards)} cards en {ciudad}")

        for card in cards[:15]:
            try:
                card_text = card.inner_text().strip()
                if not card_text:
                    continue

                titulo = ""
                for t_sel in ["h3.base-search-card__title", "h3", "h4", "a[class*='job-card-list__title']",
                               "span[class*='title']", "span.sr-only"]:
                    try:
                        el = card.query_selector(t_sel)
                        if el:
                            titulo = el.inner_text().strip()
                            if titulo:
                                break
                    except Exception:
                        pass
                
                if not titulo:
                    lineas = [l.strip() for l in card_text.split("\n") if l.strip()]
                    titulo = lineas[0][:100] if lineas else ""

                empresa = "Ver en LinkedIn"
                for e_sel in ["h4.base-search-card__subtitle a", "h4", "span[class*='company']",
                               "a[class*='company']"]:
                    try:
                        el = card.query_selector(e_sel)
                        if el:
                            t = el.inner_text().strip()
                            if t:
                                empresa = t
                                break
                    except Exception:
                        pass

                url_cargo = url_search
                try:
                    a_el = card.query_selector("a[href*='/jobs/']")
                    if a_el:
                        href = a_el.get_attribute("href") or ""
                        url_cargo = href.split("?")[0] if href.startswith("http") else "https://www.linkedin.com" + href.split("?")[0]
                except Exception:
                    pass

                salario_num = 0
                salario_text = "No indica"

                # Fecha
                dias_pub = 999
                try:
                    t_el = card.query_selector("time")
                    if t_el:
                        txt = t_el.inner_text()
                        m = re.search(r"(\d+)", txt)
                        if "hora" in txt.lower() or "hour" in txt.lower() or "minut" in txt.lower():
                            dias_pub = 0
                        elif "día" in txt.lower() or "day" in txt.lower():
                            dias_pub = int(m.group(1)) if m else 1
                        elif "semana" in txt.lower() or "week" in txt.lower():
                            dias_pub = (int(m.group(1)) if m else 1) * 7
                except Exception:
                    pass

                resultados.append({
                    "titulo": titulo,
                    "empresa": empresa,
                    "ciudad": ciudad.capitalize(),
                    "ubicacion": ciudad.capitalize(),
                    "salario_text": salario_text,
                    "salario_num": salario_num,
                    "fuente": "LinkedIn Jobs",
                    "portal": "linkedin",
                    "url": url_cargo,
                    "url_busqueda": url_search,
                    "descripcion_snippet": card_text[:400],
                    "descripcion_completa": card_text,
                    "card_text": card_text,
                    "fecha_scrape": datetime.now().strftime("%Y-%m-%d %H:%M"),
                    "dias_publicado": dias_pub,
                    "estado_activo": f"Hace {dias_pub} dias" if dias_pub < 999 else "Fecha no detectada",
                })

            except Exception:
                continue

    except Exception as e:
        print(f"  [LI] Error ({e}) — LinkedIn descartado para esta busqueda")
    finally:
        try:
            page.close()
        except Exception:
            pass

    return resultados
