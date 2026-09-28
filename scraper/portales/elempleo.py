import requests
from bs4 import BeautifulSoup
from ..utils_red import retry_with_backoff, get_base_headers

@retry_with_backoff(max_retries=3, base_delay=3)
def buscar_elempleo(busqueda: str, ciudad: str) -> list[dict]:
    slug = busqueda.lower().replace(" ", "-")
    ciudad_slug = ciudad.lower().replace(" ", "-")
    url = f"https://www.elempleo.com/co/ofertas-empleo/{slug}/{ciudad_slug}"
    
    headers = get_base_headers()
    response = requests.get(url, headers=headers, timeout=15)
    
    if response.status_code == 429:
        raise Exception("Error 429: Too Many Requests")
    response.raise_for_status()
    
    soup = BeautifulSoup(response.text, "html.parser")
    cards = soup.find_all("div", class_="result-item")
    
    resultados = []
    for card in cards:
        titulo_elem = card.find("h2", class_="js-job-title") or card.find("a", class_="text-ellipsis")
        if not titulo_elem:
            continue
            
        titulo = titulo_elem.text.strip()
        
        href = ""
        if titulo_elem.name == "a":
            href = titulo_elem.get("href", "")
        elif titulo_elem.find("a"):
            href = titulo_elem.find("a").get("href", "")
            
        link = "https://www.elempleo.com" + href if href.startswith("/") else href
        
        empresa_elem = card.find("span", class_="info-company-name")
        empresa = empresa_elem.text.strip() if empresa_elem else "Empresa Confidencial"
        
        ubicacion_elem = card.find("span", class_="info-city")
        ubicacion = ubicacion_elem.text.strip() if ubicacion_elem else ciudad
        
        salario_elem = card.find("span", class_="info-salary")
        salario_texto = salario_elem.text.strip() if salario_elem else "No indica"
        
        desc_elem = card.find("div", class_="description")
        descripcion = desc_elem.text.strip() if desc_elem else ""
        
        resultados.append({
            "titulo": titulo,
            "empresa": empresa,
            "ciudad": ciudad.capitalize(),
            "ubicacion": ubicacion,
            "salario_texto": salario_texto,
            "salario_numerico": 0,
            "url": link,
            "descripcion": descripcion
        })
        
    return resultados
