# 🏗️ Director de Estructuración — Scraper de Vacantes

Scraper inteligente que busca en **Computrabajo** vacantes de **Director de Nuevos Proyectos / Estructuración Inmobiliaria** con 4 filtros robustos, y genera 3 Excels + dashboard interactivo.

> **Referencia real:** OCOBO CONSTRUCCIONES S.A.S — *Director de Nuevos Proyectos* — **$15.600.000/mes — Score 17** (factibilidad técnica, compra de lotes, predios…). Vacante validada con fotos. Aparece siempre como baseline en cada corrida.

---

## ⚡ Instalación rápida

```bash
# 1. Crear entorno virtual con Python 3.11 y seed (pip incluido)
uv venv --python 3.11 --seed

# 2. Activar
.venv\Scripts\activate          # Windows PowerShell
# source .venv/bin/activate     # macOS / Linux

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Instalar browsers de Playwright (solo la primera vez)
playwright install chromium
```

---

## ▶️ Correr el scraper

### Ejecución Manual
```bash
# Correr el scraper completo una sola vez
python main.py

# Generar el dashboard manualmente
python -m scraper.dashboard_generator "data/PREMIUM_director_proyectos_X.xlsx"
```

### Ejecución Diaria Automatizada (Recomendado)
El proyecto incluye un script `run_diario.py` que corre el scraper completo (con un timeout seguro de 1 hora) y luego genera automáticamente el dashboard y el `reporte_aplicar.xlsx`.

Para probarlo ahora mismo:
```bash
python run_diario.py --now
```

**Automatización en Windows Task Scheduler:**
1. Abre el "Programador de Tareas" en Windows.
2. Clic en "Crear tarea básica..."
3. Nombre: `DirectoresEstructuracion Diario`
4. Desencadenador: Diariamente, a las 6:00 AM.
5. Acción: "Iniciar un programa".
   - **Programa/script:** `C:\Dev\Python\proyecto-directores-estructuracion\.venv\Scripts\python.exe`
   - **Argumentos:** `C:\Dev\Python\proyecto-directores-estructuracion\run_diario.py --now`
6. En las "Condiciones" de la tarea, puedes habilitar "Detener la tarea si se ejecuta durante más de 1 hora".

---

## 📦 Qué genera cada corrida

| Archivo | Contenido |
|---|---|
| `data/reporte_aplicar_YYYYMMDD.xlsx` | **(NUEVO)** Reporte con URLs directas y carta sugerida para aplicar. |
| `data/PREMIUM_multi_*.xlsx` | Solo PREMIUM + ALTO (salario ≥12M o Score ≥6) |
| `data/TODOS_multi_*.xlsx` | Todos los válidos que pasaron los 4 filtros |
| `data/DESCARTADOS_multi_*.xlsx` | Los descartados con su motivo |
| `data/dashboard_*_ROBUSTO.html` | Dashboard interactivo con badges de portal (CT/MG/LI/EE) |

---

## 🔍 Los 4 filtros robustos

| # | Filtro | Criterio |
|---|---|---|
| 1 | **Salario corregido** | Descarta si indica < $3M. Corrige errores de parseo ($1.560.000.000 → $15.6M) |
| 2 | **Sector inmobiliario/construcción** | Solo constructoras, inmobiliarias, desarrollo urbano |
| 3 | **Keywords con peso** | `factibilidad técnica`=3, `compra de lotes`=3, `lotes`=1… Score ≥ 2 para pasar |
| 4 | **Activo ≤ 30 días** | Descarta vacantes antiguas. Empresas TOP obtienen 45 días de margen |

### Niveles de clasificación

| Nivel | Criterio |
|---|---|
| 🟡 **PREMIUM** | Salario ≥ $12M **o** Score ≥ 6 |
| 🟠 **ALTO** | Salario ≥ $6M **o** Score ≥ 4 |
| 🔵 **MEDIO** | Salario ≥ $3M + sector válido + Score ≥ 2 |

---

## 🗂️ Estructura del proyecto

```
proyecto-directores-estructuracion/
├── main.py                        # Punto de entrada → llama scraper/main.py
├── requirements.txt
├── .gitignore
├── data/
│   └── ejemplo_OCOBO.xlsx         # Referencia real ($15.6M Score 17) ← en git
└── scraper/
    ├── __init__.py
    ├── config_robusto.py          # ← Fuente única de configuración
    ├── config.py                  # Re-export de config_robusto (compatibilidad)
    ├── filtro_robusto.py          # Lógica de los 4 filtros
    ├── main.py                    # Scraper principal (robusto, 3 Excels + dashboard)
    ├── dashboard_generator.py     # Dashboard HTML con ciudades, niveles, score
    └── crm.py                     # CRM de constructoras objetivo
```

---

## 🔧 Configuración

Editar **`scraper/config_robusto.py`** para ajustar:
- Salarios mínimos / umbrales de alerta
- Keywords y sus pesos
- Títulos objetivo
- Empresas constructoras top (contacto directo)

---

## 📋 Variables de entorno (opcional)

```bash
cp .env.example .env
# Editar .env si se necesitan tokens adicionales
```
