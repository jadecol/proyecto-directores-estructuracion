"""
Portal: Magneto365
"""
import time
import random
from datetime import datetime
from ..filtro_robusto import extraer_salario_robusto

def buscar_magneto(busqueda: str, ciudad: str, pw_context) -> list[dict]:
    """
    Busca en Magneto365 utilizando React/NextJS selectors esperando que renderice el enlace real.
    """
    resultados = []
    page = pw_context.new_page()
    
    q = busqueda.replace(' ', '%20')
    url_search = f"https://www.magneto365.com/co/empleos?search={q}&l={ciudad}"
    
    try:
        print(f"  [MG] Intentando: {url_search}")
        page.goto(url_search, wait_until="networkidle", timeout=30_000)
        page.wait_for_timeout(5000)
        
        # Scroll para cargar lazy-loaded elements
        page.mouse.wheel(0, 2000)
        page.wait_for_timeout(3000)

        # Buscar enlaces que explícitamente lleven a una vacante
        cards = page.locator("a[href*='/co/empleos/'], a[href*='/empleos/']").all()
        print(f"  [MG] {len(cards)} enlaces encontrados para '{busqueda}'")
        
        for a in cards[:30]:
            href = a.get_attribute("href")
            if not href:
                continue
            if "/co/empleos/" not in href and "/empleos/" not in href:
                continue
            if href == "/co" or href == "/co/" or href == "https://www.magneto365.com/co":
                continue
                
            if href.startswith("/"):
                href = "https://www.magneto365.com" + href
                
            # Evitar enlaces rotos o recursivos a la misma home de empleos
            if href.endswith("/empleos") or href.endswith("/empleos/"):
                continue

            # Título del enlace
            titulo = a.inner_text().strip()
            # Si el título es muy corto, probablemente sea un botón "Ver más"
            if len(titulo) < 10:
                continue
            titulo = titulo[:150]

            # Extrae empresa del card padre (intento heurístico)
            try:
                empresa_bruto = a.locator("..").locator("..").inner_text().split("\n")
                if len(empresa_bruto) > 1:
                    empresa = empresa_bruto[1][:80].strip()
                else:
                    empresa = "Por ver en vacante"
            except:
                empresa = "Por ver en vacante"

            # Salario (si lo podemos extraer rápido, si no 0)
            try:
                card_text = a.locator("..").locator("..").locator("..").inner_text()
            except:
                card_text = titulo + " " + empresa
                
            salario_num, salario_text = extraer_salario_robusto(card_text)

            url_limpia = href.split("?")[0]
            
            resultados.append({
                "titulo": titulo,
                "empresa": empresa,
                "ciudad": ciudad.capitalize(),
                "ubicacion": ciudad.capitalize(),
                "salario_text": salario_text if salario_text else "No indica",
                "salario_num": salario_num,
                "fuente": "Magneto365",
                "portal": "magneto",
                "url": url_limpia,
                "url_busqueda": url_search,
                "url_limpia": url_limpia,
                "descripcion_snippet": card_text[:400].replace("\n", " ") if card_text else "",
                "descripcion_completa": card_text,
                "card_text": card_text,
                "fecha_scrape": datetime.now().strftime("%Y-%m-%d %H:%M")
            })

    except Exception as e:
        print(f"  [MG] Error: {e}")
    finally:
        try:
            page.close()
        except:
            pass

    return resultados
