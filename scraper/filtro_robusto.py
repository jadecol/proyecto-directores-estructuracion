"""
FILTRO ROBUSTO - Director Estructuracion
4 Filtros: Palabras clave + Activo + Salario + Sector
"""
import re
from datetime import datetime, timedelta
from .config_robusto import *

def limpiar_texto(texto):
    if not texto: return ""
    return texto.lower()

def extraer_salario_robusto(texto):
    """Extrae salario y corrige errores tipo $1,560,000,000 que en realidad es $15.6M"""
    if not texto:
        return 0, "No indica"
    
    # Busca patrones: $ 15.600.000,00 / $15,600,000 / 15600000 / 15.6M
    patrones = [
        r"\$\s*([\d\.\,]+)\s*\(?mensual\)?",
        r"\$\s*([\d\.\,]+)",
        r"(\d{1,3}(?:\.\d{3})+)",
        r"(\d{7,10})"  # 15600000
    ]
    
    for pat in patrones:
        m = re.search(pat, texto, re.IGNORECASE)
        if m:
            raw = m.group(1)
            # Limpiar
            num_str = raw.replace(".", "").replace(",", "")
            # Quitar decimales ,00
            if len(num_str) > 2 and num_str.endswith("00"):
                num_str = num_str[:-2]
            try:
                num = int(num_str)
                # Corrección: si es > 100M es error de parseo (ej: 1,560,000,000 -> 15,600,000)
                if num >= SALARIO_SOSPECHOSO_MAX:
                    # Si termina en 000, dividir entre 100
                    if num % 100 == 0:
                        num = num // 100
                return num, f"${num:,} (Mensual)"
            except:
                continue
    return 0, "No indica / A convenir"

def calcular_score_keywords(descripcion):
    """Calcula puntaje por palabras clave con peso"""
    desc = limpiar_texto(descripcion)
    score = 0
    keywords_encontradas = []
    for kw, peso in KEYWORDS_ESTRUCTURACION.items():
        if kw.lower() in desc:
            score += peso
            keywords_encontradas.append(f"{kw}({peso})")
    return score, keywords_encontradas

def es_sector_valido(titulo, descripcion, empresa=""):
    """Valida sector inmobiliario / construccion.
    Para tarjetas delgadas (LinkedIn, Magneto) donde la card no incluye
    texto de sector, infiere el sector desde el titulo.
    """
    texto = f"{titulo} {descripcion} {empresa}".lower()
    titulo_l = titulo.lower()

    # Si tiene sector valido en cualquier texto, ok
    tiene_sector_valido = any(s in texto for s in SECTORES_VALIDOS)

    # Sector IMPLICITO desde el titulo — critico para LinkedIn/Magneto thin cards
    TITULOS_SECTOR_IMPLICITO = [
        "estructuracion", "estructuración",
        "nuevos proyectos", "nuevo proyecto",
        "factibilidad", "prefactibilidad",
        "inmobili",       # inmobiliario, inmobiliaria, inmobiliarios
        "construccion", "constructora",
        "desarrollo urbano", "expansion inmobiliaria",
        "banco de lotes", "predios",
        "finca raiz", "finca raíz",
    ]
    tiene_sector_en_titulo = any(k in titulo_l for k in TITULOS_SECTOR_IMPLICITO)

    # Si tiene sector a excluir Y no tiene sector valido ni keywords fuertes, rechazar
    tiene_sector_excluir = any(s in texto for s in SECTORES_EXCLUIR_SI_NO_TIENE_KEYWORD)

    score_kw, _ = calcular_score_keywords(descripcion)

    if tiene_sector_excluir and not tiene_sector_valido and not tiene_sector_en_titulo and score_kw < 3:
        return False, "Sector no relevante (TI/salud/retail) sin keywords"

    if tiene_sector_valido:
        return True, "Sector inmobiliario/construccion"

    # Sector implicito por titulo (tarjeta delgada sin descripcion de sector)
    if tiene_sector_en_titulo:
        return True, f"Sector implicito por titulo: '{titulo[:60]}'"

    # Si no dice sector pero tiene keywords altas, aceptar (como OCOBO)
    if score_kw >= 3:
        return True, f"Sector implicito por keywords score {score_kw}"

    return False, "Sin sector inmobiliario"

def es_activo(texto_card, descripcion=""):
    """Detecta si está activo: Hoy, Hace X dias, etc."""
    texto = f"{texto_card} {descripcion}".lower()
    
    # Palabras que indican activo
    if "hoy" in texto or "ayer" in texto or "hace" in texto:
        # Extraer dias
        m = re.search(r"hace\s+(\d+)\s+dias", texto)
        if m:
            dias = int(m.group(1))
            activo = dias <= DIAS_MAX_ACTIVO
            return activo, dias, f"Hace {dias} dias"
        m = re.search(r"hace\s+(\d+)\s+horas", texto)
        if m:
            return True, 0, f"Hace {m.group(1)} horas"
        # Si dice "Hace" sin numero, asumimos reciente
        if "hace" in texto:
            return True, 5, "Hace pocos dias"
    
    # Si no dice fecha, lo consideramos activo pero con advertencia
    # Computrabajo siempre muestra fecha, si no la vemos es porque no la parseamos
    return True, 999, "Fecha no detectada - Asumido activo (verificar)"

def filtrar_cargo_robusto(cargo_raw):
    """
    Filtro robusto 4 capas:
    1. Salario minimo
    2. Sector valido
    3. Keywords (score >=2)
    4. Activo
    Retorna dict enriquecido con motivo rechazo o aceptacion
    """
    titulo = cargo_raw.get("titulo", "")
    desc = cargo_raw.get("descripcion_snippet", "") + " " + cargo_raw.get("descripcion_completa", "")
    empresa = cargo_raw.get("empresa", "")
    card_text = cargo_raw.get("card_text", "")
    salario_num = cargo_raw.get("salario_num", 0)
    
    # === FILTRO 1: SALARIO MINIMO ===
    if salario_num > 0 and salario_num < SALARIO_MINIMO_FILTRO:
        return None, f"Descartado por salario bajo ${salario_num:,} < ${SALARIO_MINIMO_FILTRO:,}"
    
    # === FILTRO 2: SECTOR ===
    sector_ok, motivo_sector = es_sector_valido(titulo, desc, empresa)
    if not sector_ok:
        return None, f"Descartado por sector: {motivo_sector}"
    
    # === FILTRO 3: KEYWORDS (score) ===
    score_kw, kws = calcular_score_keywords(desc + " " + titulo)
    if score_kw < 2:
        # Permitir si titulo es exacto de objetivo
        titulo_lower = titulo.lower()
        es_titulo_objetivo = any(t.lower() in titulo_lower for t in ["nuevos proyectos", "estructuracion", "desarrollo inmobiliario", "factibilidad", "expansion inmobiliaria"])
        if not es_titulo_objetivo:
            return None, f"Descartado por keywords bajo score {score_kw} < 2, encontradas: {kws}"
    
    # === FILTRO 4: ACTIVO ===
    activo, dias, motivo_fecha = es_activo(card_text, desc)
    if not activo and dias > DIAS_MAX_ACTIVO:
        # Excepto si es empresa TOP como OCOBO, dar mas margen
        es_premium = any(e["empresa"].lower() in empresa.lower() for e in __import__("scraper.config_robusto", fromlist=["EMPRESAS_DIRECTO"]).EMPRESAS_DIRECTO) if empresa else False
        if not es_premium and dias > DIAS_MAX_PREMIUM:
            return None, f"Descartado por inactivo: {motivo_fecha} ({dias} dias > {DIAS_MAX_ACTIVO})"
    
    # === SI PASA TODO, ES VALIDO ===
    # Determinar nivel (umbral mínimo 8M alineado con SALARIO_MINIMO_FILTRO)
    salario = salario_num
    es_alerta = False
    nivel = "ALTO"  # default para los que pasan el filtro de 8M

    if salario >= SALARIO_ALERTA_BOGOTA or score_kw >= 6:
        # >=12M Bogotá / >=10M Regional  o  score keyword muy alto
        nivel = "PREMIUM"
        es_alerta = True
    elif salario >= SALARIO_MINIMO_FILTRO or score_kw >= 4:
        # >=8M  o  score alto aunque no indique salario
        nivel = "ALTO"
        es_alerta = False
    else:
        # Pasó filtros por score/sector pero sin salario declarado
        nivel = "MEDIO"
    
    # Enriquecer cargo
    cargo_raw["score_keywords"] = score_kw
    cargo_raw["keywords_encontradas"] = ", ".join(kws)
    cargo_raw["sector_valido"] = motivo_sector
    cargo_raw["dias_publicado"] = dias
    cargo_raw["estado_activo"] = motivo_fecha
    cargo_raw["activo"] = activo
    cargo_raw["nivel"] = nivel
    cargo_raw["alerta"] = es_alerta
    cargo_raw["motivo_aceptado"] = f"Score {score_kw} | {motivo_sector} | {motivo_fecha} | Salario ${salario:,}"
    
    return cargo_raw, "Aceptado"
