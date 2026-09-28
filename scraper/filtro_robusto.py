import re

KEYWORDS_INMOBILIARIAS = [
    "director", "gerente", "cabida", "norma", "viabilidad", 
    "estructuracion", "lote", "nuevo proyecto", "desarrollo inmobiliario", 
    "real estate"
]

KEYWORDS_EXCLUYENTES = [
    "medicamento", "salud", "tecnolog", "ti", "software", "seguridad privada", 
    "hospital", "clinica", "eps", "docente", "colegio", "alimentos", 
    "farmac", "medico", "desarrollador", "it"
]

def extraer_salario_robusto(texto: str):
    if not texto: return 0, "No indica"
    
    match = re.search(r'\$\s*([\d\.\,]+)', texto.replace("'", ""))
    if not match:
        return 0, texto
        
    num_str = match.group(1)
    num_str = re.sub(r'[,.]\d{2}$', '', num_str)
    num_str = num_str.replace('.', '').replace(',', '')
    
    if not num_str.isdigit():
        return 0, texto
        
    val = int(num_str)
    return val, f"$ {val:,}"

def filtrar_cargo_robusto(cargo: dict):
    titulo = str(cargo.get("titulo", "")).lower()
    descripcion = str(cargo.get("descripcion", "")).lower()
    salario_texto = str(cargo.get("salario_texto", "") or cargo.get("salario_text", "")).lower()
    salario_num = cargo.get("salario_num") or cargo.get("salario_numerico") or 0
    
    if salario_num == 0 and ("$" in salario_texto or "$" in descripcion):
        salario_num, _ = extraer_salario_robusto(salario_texto)
        if salario_num == 0:
            salario_num, _ = extraer_salario_robusto(descripcion)
            
    cargo["salario_num"] = salario_num

    texto_completo = f"{titulo} {descripcion} {salario_texto}"
    
    # Exclusión por sector basura
    if any(ex in texto_completo for ex in KEYWORDS_EXCLUYENTES):
        return None, "Descartado: Sector excluido (Basura)"

    # Exclusión Académica Estricta
    if "maestria" in texto_completo or "maestría" in texto_completo or "doctorado" in texto_completo:
        if "deseable" not in texto_completo and "opcional" not in texto_completo:
            return None, "Descartado: Requiere Maestría/Doctorado obligatorios"

    if salario_num >= 7_000_000:
        cargo["nivel"] = "PREMIUM" if salario_num >= 12_000_000 else "ALTO"
        cargo["score_keywords"] = 10
        return cargo, None

    salario_oculto = (salario_num == 0) or any(w in salario_texto for w in ["convenir", "confidencial", "no indica"]) or any(w in descripcion for w in ["a convenir", "salario confidencial"])
    
    if not salario_oculto:
        return None, f"Descartado: Salario explícito por debajo de 7M ({salario_num})"

    tiene_kw = any(kw in titulo or kw in descripcion for kw in KEYWORDS_INMOBILIARIAS)
    
    if tiene_kw:
        cargo["nivel"] = "MEDIO"
        cargo["score_keywords"] = 5
        return cargo, None
        
    return None, "Descartado: Salario a convenir pero sin keywords técnicas inmobiliarias"
