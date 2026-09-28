import requests
from bs4 import BeautifulSoup
from urllib.parse import quote
from ..utils_red import retry_with_backoff, get_base_headers

@retry_with_backoff(max_retries=3, base_delay=3)
def buscar_linkedin(busqueda: str, ciudad: str) -> list[dict]:
    query_encoded = quote(busqueda)
    loc_encoded = quote(f"{ciudad}, Colombia")
    url = f"https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search?keywords={query_encoded}&location={loc_encoded}&start=0"
    
    headers = get_base_headers()
    response = requests.get(url, headers=headers, timeout=15)
    
    if response.status_code == 429:
        raise Exception("Error 429: Too Many Requests")
    response.raise_for_status()
    
    soup = BeautifulSoup(response.text, "html.parser")
    cards = soup.find_all("li")
    
    resultados = []
    for card in cards:
        titulo_elem = card.find("h3", class_="base-search-card__title")
        if not titulo_elem:
            continue
        titulo = titulo_elem.text.strip()
        
        a_tag = card.find("a", class_="base-card__full-link")
        link = a_tag["href"].split("?")[0] if a_tag else ""
        
        empresa_elem = card.find("h4", class_="base-search-card__subtitle")
        empresa = empresa_elem.text.strip() if empresa_elem else "Por ver en vacante"
        
        ubicacion_elem = card.find("span", class_="job-search-card__location")
        ubicacion = ubicacion_elem.text.strip() if ubicacion_elem else ciudad
        
        resultados.append({
            "titulo": titulo,
            "empresa": empresa,
            "ciudad": ciudad.capitalize(),
            "ubicacion": ubicacion,
            "salario_texto": "No indica",
            "salario_numerico": 0,
            "url": link,
            "descripcion": ""  # El API guest devuelve fragmentos sin la descripcion completa
        })
        
    return resultados
