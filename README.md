# Proyecto Directores Estructuración - Scraper ROBUSTO

Scraper multi-portal 4 portales: Computrabajo, Magneto365, LinkedIn Guest API, ElEmpleo.

Filtra Director/Gerente Estructuración + Nuevos Proyectos constructoras >=5M.

## Flujo
4 filtros: Salario >=5M | Sector inmobiliario/construcción | Keywords con peso (factibilidad=3, lotes=3) | Activo <=30 días

## Archivos que genera
- `data/PREMIUM_multi_*.xlsx` - >=12M o Score >=6
- `data/TODOS_multi_*.xlsx` - >=3M + sector + score >=2
- `data/dashboard_*_ROBUSTO.html` - Dashboard con badges de portal
- `data/reporte_aplicar_*.xlsx` - Listo para aplicar con URLs corregidas y carta sugerida

## Uso
```powershell
.\.venv\Scripts\python.exe run_diario.py --now
