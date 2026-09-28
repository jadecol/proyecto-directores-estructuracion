"""
Portal: Computrabajo Colombia
URL base: https://co.computrabajo.com/trabajo-de-{slug}-en-{ciudad}
Anti-403: headers + delays aleatorios + retry si 0 cards + fragmento #lc limpiado
"""
import re
import time
import random
from datetime import datetime
from ..filtro_robusto import extraer_salario_robusto

# User-Agents reales rotados para anti-bot
_USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
]


def _slug(texto: str) -> str:
    return (texto.replace(" ", "-").lower()
            .replace("á", "a").replace("é", "e").replace("ó", "o")
            .replace("í", "i").replace("ú", "u").replace("ñ", "n"))


def buscar_computrabajo(busqueda: str, ciudad: str, pw_context) -> list[dict]:
    """
    Busca en Computrabajo y retorna lista de cargos crudos.
    Anti-403: delay 4-7s, headers reales, limpiar #lc del URL, retry tras bloqueo.
    """
    slug_b = _slug(busqueda)
    slug_c = _slug(ciudad)
    url_busqueda = f"https://co.computrabajo.com/trabajo-de-{slug_b}-en-{slug_c}"
    resultados = []

    page = pw_context.new_page()
    try:
        print(f"  [CT] {url_busqueda}")
        page.goto(url_busqueda, wait_until="domcontentloaded", timeout=60_000)
        time.sleep(random.uniform(4, 7))  # Anti-bot delay

        cards = page.query_selector_all("article")

        # Retry si detecta bloqueo (0 cards cuando esperábamos resultados)
        if len(cards) == 0:
            print(f"  [CT] 0 cards — esperando 70s y reintentando...")
            time.sleep(70)
            try:
                page.reload(wait_until="domcontentloaded", timeout=60_000)
                time.sleep(random.uniform(3, 5))
                cards = page.query_selector_all("article")
            except Exception:
                pass
            if len(cards) == 0:
                print(f"  [CT] BLOQUEO 403 detectado en {url_busqueda} — saltando")
                return []

        print(f"  [CT] {len(cards)} cards en {slug_b}/{slug_c}")

        for card in cards[:20]:
            try:
                link_el = card.query_selector("a.js-o-link")
                if not link_el:
                    continue
                titulo = link_el.inner_text().strip()
                link = link_el.get_attribute("href") or ""
                if link and not link.startswith("http"):
                    link = "https://co.computrabajo.com" + link
                link_limpio = link.split("#")[0]  # quitar #lc=...

                card_text = card.inner_text()
                salario_num, salario_text = extraer_salario_robusto(card_text)

                empresa = "Por extraer"
                try:
                    emp_el = card.query_selector("p.fc_base")
                    if emp_el:
                        empresa = emp_el.inner_text().strip()
                except Exception:
                    pass

                # Descripcion detallada: entrar si el titulo O el card sugiere un cargo relevante
                descripcion_completa = card_text
                _palabras_clave_detalle = [
                    "factibilidad", "lotes", "estructuracion", "nuevos proyectos",
                    "desarrollo inmobiliario", "expansion inmobiliaria",
                    "director", "gerente", "jefe",  # todos los directivos van al detalle
                    "inmobili", "construccion", "constructora", "predios",
                ]
                if any(k in (titulo + card_text).lower() for k in _palabras_clave_detalle):
                    try:
                        p2 = pw_context.new_page()
                        p2.goto(link_limpio, wait_until="domcontentloaded", timeout=25_000)
                        time.sleep(1.5)
                        descripcion_completa = p2.inner_text("body")[:6000]
                        p2.close()
                    except Exception:
                        pass

                resultados.append({
                    "titulo": titulo,
                    "empresa": empresa,
                    "ciudad": ciudad.capitalize(),
                    "ubicacion": ciudad.capitalize(),
                    "salario_text": salario_text,
                    "salario_num": salario_num,
                    "fuente": "Computrabajo",
                    "portal": "computrabajo",
                    "url": link_limpio,
                    "url_busqueda": url_busqueda,
                    "descripcion_snippet": descripcion_completa[:400],
                    "descripcion_completa": descripcion_completa,
                    "card_text": card_text,
                    "fecha_scrape": datetime.now().strftime("%Y-%m-%d %H:%M"),
                })
            except Exception:
                continue

    except Exception as e:
        print(f"  [CT] Error: {e}")
    finally:
        try:
            page.close()
        except Exception:
            pass

    return resultados
