import pandas as pd
from datetime import datetime
from .config import EMPRESAS_DIRECTO

def generar_crm():
    df = pd.DataFrame(EMPRESAS_DIRECTO)
    # Añadir columnas para contacto directo
    df['Decisor Tipico'] = df['empresa'].apply(lambda x: "Gerente Desarrollo Inmobiliario" if "OCOBO" in x else "Director Nuevos Negocios / Gerente Proyectos")
    df['LinkedIn Buscar'] = df['empresa'] + " Gerente Desarrollo"
    df['Email Patron'] = df['dominio'].apply(lambda d: f"nombre.apellido@{d}" if d != "-" else "-")
    df['Mensaje Directo Sugerido'] = "Hola, vi vacante Director Nuevos Proyectos enfocada en factibilidad y compra lotes. ¿15 min para conversar?"
    df['Fecha Actualizacion'] = datetime.now().strftime("%Y-%m-%d %H:%M")
    
    path = f"data/CRM_Directores_Estructuracion_{datetime.now().strftime('%Y%m%d')}.xlsx"
    df.to_excel(path, index=False)
    print(f"✅ CRM generado: {path} con {len(df)} empresas")
    return path
