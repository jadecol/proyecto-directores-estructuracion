import re
import requests
from bs4 import BeautifulSoup
from ..utils_red import retry_with_backoff, get_base_headers

@retry_with_backoff(max_retries=3, base_delay=3)
def buscar_computrabajo(busqueda: str, ciudad: str) -> list[dict]:
    slug = busqueda.lower().replace(" ", "-")
    ciudad_slug = ciudad.lower().replace(" ", "-")
    url = f"https://co.computrabajo.com/trabajo-de-{slug}-en-{ciudad_slug}"
    
    headers = get_base_headers()
    response = requests.get(url, headers=headers, timeout=15)
    
    if response.status_code == 429:
        raise Exception("Error 429: Too Many Requests")
    response.raise_for_status()
    
    soup = BeautifulSoup(response.text, "html.parser")
    cards = soup.find_all("article", class_="box_offer")
    
    resultados = []
    for card in cards:
        titulo_elem = card.find("h1", class_="fs18") or card.find("h2", class_="fs18")
        if not titulo_elem:
            continue
            
        a_tag = titulo_elem.find("a")
        if not a_tag:
            continue
            
        titulo = a_tag.text.strip()
        link = "https://co.computrabajo.com" + a_tag["href"].split("?")[0]
        
        empresa = "Empresa Confidencial"
        ubicacion = ciudad
        
        info_p = card.find("p", class_="fs16")
        if info_p:
            a_empresa = info_p.find("a")
            if a_empresa:
                empresa = a_empresa.text.strip()
                ubicacion_text = info_p.text.replace(empresa, "").strip(" -,\n")
                if ubicacion_text:
                    ubicacion = ubicacion_text
            else:
                partes = info_p.text.split("-")
                if len(partes) >= 2:
                    empresa = partes[0].strip()
                    ubicacion = partes[-1].strip()
                else:
                    empresa = info_p.text.strip()
        
        card_text = card.get_text(separator=' ', strip=True)
        salario_texto = "No indica"
        salario_matches = re.findall(r'\$[^a-zA-Z]+', card_text)
        if salario_matches:
            for match in salario_matches:
                match_limpio = match.strip(" -/,\n")
                if len(match_limpio) > 4:
                    salario_texto = match_limpio
                    break
        
        desc_elem = card.find("p", class_="fc_mut")
        descripcion = desc_elem.text.strip() if desc_elem else card_text[:150]
        
        resultados.append({
            "titulo": titulo,
            "empresa": empresa[:80],
            "ciudad": ciudad.capitalize(),
            "ubicacion": ubicacion[:80],
            "salario_texto": salario_texto,
            "salario_numerico": 0,
            "url": link,
            "descripcion": descripcion
        })
        
    return resultados
