"""
CONFIGURACION ROBUSTA - FILTRO ADECUADO
Director Nuevos Proyectos / Estructuracion
"""

# === 1. SALARIOS ===
SALARIO_MINIMO_FILTRO = 5_000_000  # >=5M (captura ALTO 5-8M y PREMIUM >=12M)
SALARIO_ALERTA_BOGOTA = 12_000_000
SALARIO_ALERTA_REGIONAL = 10_000_000
SALARIO_SOSPECHOSO_MAX = 100_000_000  # Si dice $1,560,000,000 es error de parseo, es 15.6M

# === 2. PALABRAS CLAVE - PESO ===
KEYWORDS_ESTRUCTURACION = {
    # Alta relevancia (3 puntos)
    "factibilidad tecnica": 3,
    "factibilidad normativa": 3,
    "factibilidad comercial": 3,
    "estructuracion y gestion de nuevos proyectos": 3,
    "compra de lotes": 3,
    "banco de lotes": 3,
    "busqueda de predios": 3,
    "negociacion predios": 3,
    "estructuracion inmobiliaria": 3,
    # Media relevancia (2 puntos)
    "factibilidad": 2,
    "prefactibilidad": 2,
    "estructuracion": 2,
    "desarrollo inmobiliario": 2,
    "curaduria": 2,
    "planeacion": 2,
    "gestion documental de predios": 2,
    "estudios integrales": 2,
    "nuevos proyectos inmobiliarios": 2,
    "nuevos negocios inmobiliarios": 2,
    # Baja relevancia (1 punto) - pero suma
    "lotes": 1,
    "predios": 1,
    "dueños de tierra": 1,
    "potencial": 1,
    "normativa": 1,
    "comercial": 1,
}

# === 3. SECTOR ===
SECTORES_VALIDOS = [
    # Alta prioridad — constructoras directas
    "constructora", "construccion", "constructor", "edificacion",
    # Inmobiliario
    "inmobiliario", "inmobiliaria", "desarrollo inmobiliario",
    "proyectos inmobiliarios", "finca raiz",
    # Urbanismo
    "desarrollo urbano", "obra civil", "obra",
]

SECTORES_EXCLUIR_SI_NO_TIENE_KEYWORD = [
    "tecnologia", "software", "ti ", "sistemas", "desarrollador",
    "salud", "enfermeria", "medic", "contable", "contador",
    "call center", "ventas retail",
    # Gastronomia y retail — no son constructoras
    "restaurante", "alimentos", "bebidas", "gastronomia", "hosteleria",
    "supermercado", "cadena de tiendas",
]

# === 4. TITULOS ===
TITULOS_OBJETIVO = [
    "Director de Nuevos Proyectos",
    "Director de Estructuracion",
    "Director de Desarrollo Inmobiliario",
    "Gerente de Nuevos Negocios Inmobiliarios",
    "Gerente de Proyectos Inmobiliarios",
    "Director de Factibilidad",
    "Gerente de Estructuracion",
    "Jefe de Nuevos Proyectos",
    "Coordinador de nuevos negocios y proyectos",
    "Director de Expansion Inmobiliaria"
]

# === 5. ACTIVO ===
DIAS_MAX_ACTIVO = 30  # Solo vacantes de ultimos 30 dias
DIAS_MAX_PREMIUM = 45  # Para OCOBO y similares damos 45 dias

# 15 CONSTRUCTORAS TOP
EMPRESAS_DIRECTO = [
    {"empresa": "OCOBO CONSTRUCCIONES S.A.S", "ciudad": "Bogota", "web": "https://ocobo.com.co/trabaja-con-nosotros", "dominio": "ocobo.com.co", "estado": "VACANTE ACTIVA $15.6M", "prioridad": "ALTA"},
    {"empresa": "Constructora Bolivar", "ciudad": "Bogota", "web": "https://constructorabolivar.com", "dominio": "constructorabolivar.com", "prioridad": "ALTA"},
    {"empresa": "Amarilo", "ciudad": "Bogota/Medellin", "web": "https://amarilo.com.co", "dominio": "amarilo.com.co", "prioridad": "ALTA"},
    {"empresa": "Marval", "ciudad": "Cali/Bogota", "web": "https://marval.com.co", "dominio": "marval.com.co", "prioridad": "MEDIA"},
    {"empresa": "Conconcreto", "ciudad": "Medellin", "web": "https://conconcreto.com", "dominio": "conconcreto.com", "prioridad": "ALTA"},
    {"empresa": "Cusezar", "ciudad": "Bogota/Pereira", "web": "https://cusezar.com", "dominio": "cusezar.com", "prioridad": "MEDIA"},
    {"empresa": "Constructora Colpatria", "ciudad": "Bogota", "web": "https://constructoracolpatria.com", "dominio": "colpatria.com", "prioridad": "MEDIA"},
    {"empresa": "Prodesa", "ciudad": "Bogota", "web": "https://prodesa.com.co", "dominio": "prodesa.com.co", "prioridad": "MEDIA"},
    {"empresa": "AR Construcciones", "ciudad": "Bogota", "web": "https://www.arconstrucciones.com", "dominio": "arconstrucciones.com", "prioridad": "MEDIA"},
    {"empresa": "Constructora Capital", "ciudad": "Medellin", "web": "https://www.constructoracapital.com", "dominio": "constructoracapital.com", "prioridad": "MEDIA"},
    {"empresa": "Bienes & Bienes", "ciudad": "Medellin", "web": "https://www.bienesybienes.com", "dominio": "bienesybienes.com", "prioridad": "MEDIA"},
    {"empresa": "Ingeurbe", "ciudad": "Armenia/Eje", "web": "https://www.ingeurbe.com", "dominio": "ingeurbe.com", "prioridad": "ALTA EJE"},
    {"empresa": "Camu Constructores", "ciudad": "Pereira/Eje", "web": "https://www.camu.com.co", "dominio": "camu.com.co", "prioridad": "ALTA EJE"},
    {"empresa": "CFC & A", "ciudad": "Cali", "web": "https://www.cfcya.com", "dominio": "cfcya.com", "prioridad": "MEDIA"},
    {"empresa": "Constr. Nuevo Proyecto", "ciudad": "Bogota", "web": "http://construnuevoproyecto.com", "dominio": "construnuevoproyecto.com", "prioridad": "BAJA"},
]
