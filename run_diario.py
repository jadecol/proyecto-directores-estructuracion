"""
Script de ejecución diaria. Corre el scraper completo por 1 hora máximo,
luego genera los reportes. Útil para ejecutar vía Windows Task Scheduler.
"""
import schedule
import time
import datetime
import subprocess
import sys
import glob
import os

def job():
    inicio = datetime.datetime.now()
    print(f"\n[{inicio.strftime('%Y-%m-%d %H:%M:%S')}] Iniciando scraper automatizado...")
    
    try:
        # 1. Correr scraper con timeout de 1 hora (3600 segundos)
        print(" Ejecutando main.py...")
        subprocess.run([sys.executable, "main.py"], timeout=3600)
        
        # Encontrar el TODOS_multi más reciente
        archivos_todos = glob.glob("data/TODOS_multi_*.xlsx")
        
        if archivos_todos:
            ultimo_todos = max(archivos_todos, key=os.path.getctime)
            
            # 2. Generar dashboard
            print(f" Generando dashboard con {ultimo_todos}...")
            subprocess.run([sys.executable, "-m", "scraper.dashboard_generator", ultimo_todos], timeout=300)
            
            # 3. Generar reporte aplicar
            print(" Generando reporte para aplicar...")
            subprocess.run([sys.executable, "-m", "scraper.reporte_aplicar"], timeout=60)
        else:
            print(" No se encontró TODOS_multi_*.xlsx para generar reportes.")
            
    except subprocess.TimeoutExpired:
        print("\n[!] Timeout de 1 hora alcanzado. El scraper fue detenido.")
        print("Guardando el estado actual...")
        # Intentar generar reportes con lo que haya
        archivos_todos = glob.glob("data/TODOS_multi_*.xlsx")
        if archivos_todos:
            ultimo_todos = max(archivos_todos, key=os.path.getctime)
            subprocess.run([sys.executable, "-m", "scraper.dashboard_generator", ultimo_todos], timeout=300)
            subprocess.run([sys.executable, "-m", "scraper.reporte_aplicar"], timeout=60)

    except Exception as e:
        print(f"\n[!] Error en ejecución: {e}")
        
    fin = datetime.datetime.now()
    duracion = (fin - inicio).total_seconds() / 60
    print(f"[{fin.strftime('%Y-%m-%d %H:%M:%S')}] Tarea finalizada en {duracion:.1f} minutos.")

def start_scheduler():
    print("=" * 60)
    print(" PROGRAMADOR AUTOMÁTICO INICIADO")
    print(" El scraper se ejecutará todos los días a las 06:00 AM")
    print(" Para ejecutar ahora, usa: python run_diario.py --now")
    print("=" * 60)
    
    schedule.every().day.at("06:00").do(job)
    
    while True:
        schedule.run_pending()
        time.sleep(60)

if __name__ == "__main__":
    if "--now" in sys.argv:
        print("Ejecución manual iniciada (--now)")
        job()
    else:
        start_scheduler()
