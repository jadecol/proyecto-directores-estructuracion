"""
Portal: ElEmpleo
URL base: https://www.elempleo.com/co/trabajos/{slug}?l={ciudad}
"""
import time
import random
from datetime import datetime
from ..filtro_robusto import extraer_salario_robusto

def _slug(texto: str) -> str:
    return (texto.replace(" ", "-").lower()
            .replace("á", "a").replace("é", "e").replace("ó", "o")
            .replace("í", "i").replace("ú", "u").replace("ñ", "n"))

def buscar_elempleo(busqueda: str, ciudad: str, pw_context) -> list[dict]:
    """
    Busca en ElEmpleo y retorna lista de cargos crudos.
    No da 403, ideal para sector construcción.
    """
    slug_b = _slug(busqueda)
    ciudad_l = ciudad.lower()
    if ciudad_l == "bogota":
        ciudad_q = "Bogot%C3%A1"
    else:
        ciudad_q = ciudad.capitalize()

    url_busqueda = f"https://www.elempleo.com/co/trabajos/{slug_b}?l={ciudad_q}"
    resultados = []

    page = pw_context.new_page()
    try:
        print(f"  [EE] {url_busqueda}")
        page.goto(url_busqueda, wait_until="domcontentloaded", timeout=60_000)
        time.sleep(random.uniform(3, 5))

        SELECTORES = [
            "div.js-offer",
            "a.js-offer",
            "article",
            "div.result-item"
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
            print(f"  [EE] 0 cards encontradas en {slug_b}/{ciudad}")
            return []

        print(f"  [EE] {len(cards)} cards en {slug_b}/{ciudad}")

        for card in cards[:20]:
            try:
                card_text = card.inner_text().strip()
                if not card_text:
                    continue

                titulo = ""
                for t_sel in ["h2", "h3", "a.text-ellipsis"]:
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

                empresa = "Ver en ElEmpleo"
                try:
                    el = card.query_selector("span.company, span.company-name")
                    if el:
                        empresa = el.inner_text().strip()
                except Exception:
                    pass

                url_cargo = url_busqueda
                try:
                    href = ""
                    # a.js-offer o enlace interior
                    tag_name = card.evaluate("el => el.tagName").lower()
                    if tag_name == "a":
                        href = card.get_attribute("href") or ""
                    else:
                        a_el = card.query_selector("a.text-ellipsis")
                        if a_el:
                            href = a_el.get_attribute("href") or ""
                    
                    if href:
                        url_cargo = href if href.startswith("http") else "https://www.elempleo.com" + href
                except Exception:
                    pass
                
                salario_num, salario_text = extraer_salario_robusto(card_text)
                if "convenir" in card_text.lower():
                    salario_text = "A convenir"
                    salario_num = 0

                ubi_card = ciudad.capitalize()
                try:
                    el = card.query_selector("span.city, span.location")
                    if el:
                        ubi_card = el.inner_text().strip()
                except Exception:
                    pass

                resultados.append({
                    "titulo": titulo,
                    "empresa": empresa,
                    "ciudad": ubi_card,
                    "ubicacion": ubi_card,
                    "salario_text": salario_text,
                    "salario_num": salario_num,
                    "fuente": "ElEmpleo",
                    "portal": "elempleo",
                    "url": url_cargo.split("?")[0],
                    "url_busqueda": url_busqueda,
                    "descripcion_snippet": card_text[:400],
                    "descripcion_completa": card_text,
                    "card_text": card_text,
                    "fecha_scrape": datetime.now().strftime("%Y-%m-%d %H:%M"),
                })
            except Exception:
                continue

    except Exception as e:
        print(f"  [EE] Error general: {e}")
    finally:
        try:
            page.close()
        except Exception:
            pass

    return resultados
