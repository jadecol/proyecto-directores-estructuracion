"""
DASHBOARD GENERATOR ROBUSTO
Genera dashboard HTML interactivo con diseño mock completo:
- Header sticky con chips de ciudades
- 5 stats cards (PREMIUM / ALTO / MEDIO / Salario / Score)
- Banner de alertas
- Filtros por nivel y ciudad
- Cards detalladas con keywords, score, motivo y badge de nivel
"""
import os
import pandas as pd
from datetime import datetime
from collections import Counter


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _fmt_money(n: int) -> str:
    try:
        return f"${int(n):,}"
    except Exception:
        return "$0"


def _safe_int(val, default=0) -> int:
    try:
        return int(val)
    except Exception:
        return default


def _safe_str(val, max_len: int = 0) -> str:
    s = str(val) if val is not None else ""
    if s.lower() in ("nan", "none", ""):
        s = ""
    if max_len and len(s) > max_len:
        s = s[:max_len] + "…"
    return s


# ---------------------------------------------------------------------------
# HTML fragments
# ---------------------------------------------------------------------------

def _build_header(excel_path: str, total: int, n_alertas: int, ciudades_counter: Counter, fecha: str) -> str:
    chips = ""
    for ciudad, count in ciudades_counter.most_common():
        if not ciudad or ciudad.lower() in ("nan", "none"):
            continue
        chips += (
            f'<span class="bg-slate-100 border border-slate-300 px-3 py-1 '
            f'rounded-full text-xs font-medium text-slate-700">'
            f'{ciudad}: {count}</span> '
        )

    return f"""
<div class="bg-slate-900 text-white p-5 sticky top-0 z-10 shadow-xl">
  <div class="max-w-7xl mx-auto">
    <div class="flex justify-between items-start">
      <div>
        <h1 class="text-2xl font-bold tracking-tight">
          <i class="fa-solid fa-building mr-2 text-amber-400"></i>
          Director Proyectos &mdash; Dashboard ROBUSTO
        </h1>
        <p class="text-xs text-slate-400 mt-1">
          Fuente: <span class="text-slate-300">{os.path.basename(excel_path)}</span>
          &nbsp;|&nbsp; {total} validados &nbsp;|&nbsp; {n_alertas} alertas
          &nbsp;|&nbsp; {fecha}
        </p>
        <div class="flex flex-wrap gap-2 mt-3">
          {chips if chips else '<span class="text-slate-500 text-xs">Sin datos de ciudad</span>'}
        </div>
      </div>
      <span class="bg-green-600 px-3 py-1 rounded-full text-xs font-semibold h-fit animate-pulse mt-1">
        &#9679; TIEMPO REAL &mdash; 4 FILTROS
      </span>
    </div>
  </div>
</div>
"""


def _build_stats(total_premium: int, total_alto: int, total_medio: int,
                 salario_prom: int, salario_max: int, score_prom: float) -> str:
    return f"""
<div class="max-w-7xl mx-auto px-4 grid grid-cols-2 md:grid-cols-5 gap-3 mt-4">

  <div class="bg-white rounded-xl p-4 shadow border-l-4 border-amber-500">
    <p class="text-[11px] text-gray-500 font-semibold uppercase tracking-wide">PREMIUM</p>
    <p class="text-3xl font-extrabold text-amber-600 mt-1">{total_premium}</p>
    <p class="text-[10px] text-gray-400 mt-1">&ge;12M o Score &ge;6</p>
  </div>

  <div class="bg-white rounded-xl p-4 shadow border-l-4 border-orange-500">
    <p class="text-[11px] text-gray-500 font-semibold uppercase tracking-wide">ALTO</p>
    <p class="text-3xl font-extrabold text-orange-600 mt-1">{total_alto}</p>
    <p class="text-[10px] text-gray-400 mt-1">&ge;6M o Score &ge;4</p>
  </div>

  <div class="bg-white rounded-xl p-4 shadow border-l-4 border-blue-500">
    <p class="text-[11px] text-gray-500 font-semibold uppercase tracking-wide">MEDIO</p>
    <p class="text-3xl font-extrabold text-blue-600 mt-1">{total_medio}</p>
    <p class="text-[10px] text-gray-400 mt-1">&ge;3M + sector</p>
  </div>

  <div class="bg-white rounded-xl p-4 shadow border-l-4 border-green-500">
    <p class="text-[11px] text-gray-500 font-semibold uppercase tracking-wide">SALARIO PROM</p>
    <p class="text-lg font-extrabold text-green-600 mt-1">{_fmt_money(salario_prom)}</p>
    <p class="text-[10px] text-gray-400 mt-1">Max {_fmt_money(salario_max)}</p>
  </div>

  <div class="bg-white rounded-xl p-4 shadow border-l-4 border-purple-500">
    <p class="text-[11px] text-gray-500 font-semibold uppercase tracking-wide">SCORE PROM</p>
    <p class="text-3xl font-extrabold text-purple-600 mt-1">{score_prom:.1f}</p>
    <p class="text-[10px] text-gray-400 mt-1">Factibilidad / lotes</p>
  </div>

</div>
"""


def _build_alert_banner(n_alertas: int) -> str:
    if not n_alertas:
        return ""
    return f"""
<div class="max-w-7xl mx-auto px-4 mt-4">
  <div class="bg-gradient-to-r from-amber-500 to-orange-600 text-white p-4 rounded-xl shadow">
    <p class="font-bold text-sm">
      <i class="fa-solid fa-fire mr-1"></i>
      {n_alertas} ALERTA{'S' if n_alertas > 1 else ''} PREMIUM &gt;$12M
      &mdash; Incluye OCOBO $15.6M
    </p>
    <p class="text-xs opacity-90 mt-0.5">
      Score &ge;6 + sector inmobiliario + activo &le;30 d&iacute;as
    </p>
  </div>
</div>
"""


def _build_filters(total: int, total_premium: int, total_alto: int, total_medio: int) -> str:
    btn_active = "filter-btn bg-slate-900 text-white px-4 py-1.5 rounded-full text-xs font-medium"
    btn_idle   = "filter-btn bg-white border border-slate-200 px-4 py-1.5 rounded-full text-xs font-medium hover:bg-slate-100 transition"

    return f"""
<div class="max-w-7xl mx-auto px-4 mt-4 flex gap-2 flex-wrap items-center">
  <button onclick="filtrar('todos')"   class="{btn_active}" data-filter="todos">Todos ({total})</button>
  <button onclick="filtrar('PREMIUM')" class="{btn_idle}"   data-filter="PREMIUM">&#11088; PREMIUM ({total_premium})</button>
  <button onclick="filtrar('ALTO')"    class="{btn_idle}"   data-filter="ALTO">&#128516; ALTO ({total_alto})</button>
  <button onclick="filtrar('MEDIO')"   class="{btn_idle}"   data-filter="MEDIO">&#128309; MEDIO ({total_medio})</button>
  <span class="border-l border-slate-300 h-5 mx-1"></span>
  <button onclick="filtrar('Bogota')"   class="{btn_idle}" data-filter="Bogota">&#128205; Bogot&aacute;</button>
  <button onclick="filtrar('Medellin')" class="{btn_idle}" data-filter="Medellin">&#128205; Medell&iacute;n</button>
  <button onclick="filtrar('Cali')"     class="{btn_idle}" data-filter="Cali">&#128205; Cali</button>
</div>
"""


def _build_card(job: dict) -> str:
    nivel = _safe_str(job.get("nivel", "MEDIO")).upper() or "MEDIO"

    # Card border / background
    if nivel == "PREMIUM":
        card_class = "job-card rounded-xl shadow-md p-4 border-2 border-amber-400 bg-gradient-to-br from-amber-50 to-orange-50"
    elif nivel == "ALTO":
        card_class = "job-card rounded-xl shadow p-4 border border-orange-300 bg-white"
    else:
        card_class = "job-card rounded-xl shadow p-4 border border-slate-200 bg-white"

    # OCOBO badge
    empresa = _safe_str(job.get("empresa", ""))
    ocobo_badge = ""
    if "OCOBO" in empresa.upper():
        ocobo_badge = (
            '<div class="bg-slate-900 text-amber-300 text-[10px] px-2 py-1 rounded w-fit mb-2 font-bold">'
            '<i class="fa-solid fa-crown mr-1"></i>OCOBO REAL &mdash; $15.6M'
            '</div>'
        )

    # Level badge
    if nivel == "PREMIUM":
        badge_nivel = '<span class="bg-amber-500 text-white text-[10px] px-2 py-0.5 rounded-full font-bold">PREMIUM</span>'
    elif nivel == "ALTO":
        badge_nivel = '<span class="bg-orange-500 text-white text-[10px] px-2 py-0.5 rounded-full font-semibold">ALTO</span>'
    else:
        badge_nivel = '<span class="bg-blue-500 text-white text-[10px] px-2 py-0.5 rounded-full">MEDIO</span>'

    estado_activo = _safe_str(job.get("estado_activo", "Activo"))
    dias = job.get("dias_publicado", "")
    dias_str = f"({dias}d)" if str(dias).isdigit() else ""

    titulo     = _safe_str(job.get("titulo", "Sin título"))
    ciudad       = _safe_str(job.get("ciudad") or job.get("ubicacion", "-"))
    salario      = _safe_str(job.get("salario_text", "No indica"))
    score        = _safe_int(job.get("score_keywords", 0))
    keywords     = _safe_str(job.get("keywords_encontradas", ""), max_len=120)
    sector       = _safe_str(job.get("sector_valido", ""), max_len=80)
    motivo       = _safe_str(job.get("motivo_aceptado", ""), max_len=160)
    snippet      = _safe_str(job.get("descripcion_snippet", ""), max_len=280)
    url          = _safe_str(job.get("url", "#")) or "#"
    url_busqueda = _safe_str(job.get("url_busqueda", "")) or url
    es_ocobo     = "OCOBO" in empresa.upper() or "magneto" in url.lower()
    portal       = _safe_str(job.get("portal") or job.get("fuente", "")).lower()
    li_query     = empresa.replace(" ", "%20") + "%20Gerente%20Desarrollo"

    # Portal badge
    if "magneto" in portal:
        portal_badge = '<span class="bg-violet-100 text-violet-700 text-[9px] px-2 py-0.5 rounded-full border border-violet-200 font-semibold"><i class="fa-solid fa-magnet mr-0.5"></i>Magneto365</span>'
    elif "computrabajo" in portal or "computrabajo" in url.lower():
        portal_badge = '<span class="bg-blue-100 text-blue-700 text-[9px] px-2 py-0.5 rounded-full border border-blue-200 font-semibold"><i class="fa-solid fa-briefcase mr-0.5"></i>Computrabajo</span>'
    elif "linkedin" in portal:
        portal_badge = '<span class="bg-sky-100 text-sky-700 text-[9px] px-2 py-0.5 rounded-full border border-sky-200 font-semibold"><i class="fa-brands fa-linkedin mr-0.5"></i>LinkedIn</span>'
    elif "elempleo" in portal:
        portal_badge = '<span class="bg-emerald-100 text-emerald-700 text-[9px] px-2 py-0.5 rounded-full border border-emerald-200 font-semibold"><i class="fa-solid fa-briefcase mr-0.5"></i>ElEmpleo</span>'
    else:
        portal_badge = '<span class="bg-gray-100 text-gray-500 text-[9px] px-2 py-0.5 rounded-full border border-gray-200">Portal</span>'

    # Score color
    if score >= 6:
        score_class = "text-amber-600 font-extrabold"
    elif score >= 4:
        score_class = "text-orange-500 font-bold"
    else:
        score_class = "text-slate-600 font-semibold"

    return f"""
<div class="{card_class}" data-nivel="{nivel}" data-ciudad="{ciudad}" data-portal="{portal}">
  {ocobo_badge}

  <div class="flex justify-between items-start mb-2">
    <div class="flex gap-1.5 flex-wrap">{badge_nivel} {portal_badge}</div>
    <span class="text-[10px] text-gray-400">{estado_activo} {dias_str}</span>
  </div>

  <h3 class="font-bold text-sm leading-snug text-slate-800">{titulo}</h3>

  <p class="text-xs text-gray-700 mt-1">
    <i class="fa-solid fa-building text-gray-400 mr-1"></i>{empresa}
  </p>
  <p class="text-xs text-gray-500">
    <i class="fa-solid fa-location-dot text-gray-400 mr-1"></i>{ciudad}
  </p>

  <div class="flex justify-between items-center mt-2">
    <p class="text-sm font-bold text-green-600">{salario}</p>
    <p class="text-xs {score_class}">Score {score}</p>
  </div>

  <div class="bg-slate-50 border border-slate-100 rounded-lg p-2 mt-2">
    <p class="text-[10px] text-gray-500 font-bold uppercase tracking-wide">Keywords:</p>
    <p class="text-[10px] text-gray-600 mt-0.5">{keywords if keywords else 'No detectadas'}</p>
    {f'<p class="text-[10px] text-slate-400 mt-1">{sector}</p>' if sector else ''}
  </div>

  {f'<p class="text-[11px] text-gray-600 mt-2 leading-relaxed">{snippet}</p>' if snippet else ''}

  <div class="flex flex-col gap-1.5 mt-3">
    <div class="flex gap-2">
      {'<!-- OCOBO: link directo a Magneto, sin riesgo de 403 -->' if es_ocobo else '<!-- Computrabajo: 2 botones para evitar 403 -->'}
      <a href="{url}" target="_blank" rel="noopener noreferrer"
         class="flex-1 bg-slate-900 hover:bg-slate-700 text-white text-xs px-3 py-2 rounded-lg text-center font-medium transition">
        <i class="fa-solid fa-eye mr-1"></i>Ver Oferta
      </a>
      <a href="https://www.linkedin.com/search/results/people/?keywords={li_query}"
         target="_blank" rel="noopener noreferrer"
         class="bg-blue-600 hover:bg-blue-700 text-white text-xs px-3 py-2 rounded-lg text-center transition"
         title="Buscar contacto en LinkedIn">
        <i class="fa-brands fa-linkedin"></i>
      </a>
    </div>
    {'<!-- Boton de busqueda generica para evitar 403 (solo Computrabajo) -->' if not es_ocobo else ''}
    {f'<a href="{url_busqueda}" target="_blank" rel="noopener noreferrer" class="w-full bg-slate-100 hover:bg-slate-200 text-slate-700 text-xs px-3 py-2 rounded-lg text-center transition border border-slate-200"><i class="fa-solid fa-magnifying-glass mr-1"></i>Buscar en Computrabajo <span class="text-[9px] text-slate-400">(sin 403)</span></a>' if not es_ocobo else ''}
  </div>

  {f'<p class="text-[9px] text-gray-400 mt-2 truncate" title="{motivo}">{motivo}</p>' if motivo else ''}
</div>
"""


_JS = """
<script>
(function(){
  var NIVEL_FILTERS = ['PREMIUM','ALTO','MEDIO'];
  var CIUDAD_FILTERS = ['Bogota','Medellin','Cali'];

  function filtrar(f){
    // reset all buttons
    document.querySelectorAll('.filter-btn').forEach(function(b){
      b.classList.remove('bg-slate-900','text-white');
      b.classList.add('bg-white','border','border-slate-200');
    });
    // activate clicked button
    var active = document.querySelector('[data-filter="'+f+'"]');
    if(active){
      active.classList.remove('bg-white','border','border-slate-200');
      active.classList.add('bg-slate-900','text-white');
    }
    // show/hide cards
    document.querySelectorAll('.job-card').forEach(function(c){
      var n  = (c.getAttribute('data-nivel')  || '').toUpperCase();
      var ci = (c.getAttribute('data-ciudad') || '').toLowerCase();
      if(f === 'todos'){
        c.style.display = '';
      } else if(NIVEL_FILTERS.indexOf(f) !== -1){
        c.style.display = (n === f) ? '' : 'none';
      } else {
        c.style.display = ci.toLowerCase().includes(f.toLowerCase()) ? '' : 'none';
      }
    });
  }
  window.filtrar = filtrar;
})();
</script>
"""


# ---------------------------------------------------------------------------
# Main entry point
# ---------------------------------------------------------------------------

def generar_dashboard(excel_path: str) -> str:
    # --- Load data ---
    try:
        df = pd.read_excel(excel_path)
    except Exception as e:
        print(f"⚠️  No se pudo leer {excel_path}: {e}")
        df = pd.DataFrame()

    if df.empty:
        df = pd.DataFrame([{
            "titulo": "Sin datos hoy",
            "empresa": "-",
            "ubicacion": "N/A",
            "ciudad": "N/A",
            "nivel": "MEDIO",
            "score_keywords": 0,
            "salario_num": 0,
            "salario_text": "—",
            "alerta": False,
        }])

    jobs = df.to_dict(orient="records")

    # --- Stats ---
    total          = len(jobs)
    total_premium  = sum(1 for j in jobs if str(j.get("nivel","")).upper() == "PREMIUM")
    total_alto     = sum(1 for j in jobs if str(j.get("nivel","")).upper() == "ALTO")
    total_medio    = sum(1 for j in jobs if str(j.get("nivel","")).upper() == "MEDIO")
    n_alertas      = sum(1 for j in jobs if j.get("alerta") is True or str(j.get("alerta","")).lower() == "true")

    salarios       = [_safe_int(j.get("salario_num", 0)) for j in jobs if _safe_int(j.get("salario_num", 0)) > 0]
    salario_prom   = sum(salarios) // len(salarios) if salarios else 0
    salario_max    = max(salarios) if salarios else 0

    scores         = [_safe_int(j.get("score_keywords", 0)) for j in jobs]
    score_prom     = sum(scores) / len(scores) if scores else 0.0

    raw_ciudades   = [str(j.get("ciudad") or j.get("ubicacion") or "").strip().capitalize() for j in jobs]
    ciudades_counter = Counter(c for c in raw_ciudades if c and c.lower() not in ("nan","none",""))

    fecha = datetime.now().strftime("%Y-%m-%d %H:%M")

    # --- Build HTML ---
    head = f"""<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Dashboard ROBUSTO {fecha} — {total} cargos director estructuraci&oacute;n</title>
  <meta name="description" content="Dashboard de vacantes Director Nuevos Proyectos / Estructuraci&oacute;n Inmobiliaria. {total} cargos validados con 4 filtros robustos.">
  <script src="https://cdn.tailwindcss.com"></script>
  <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
  <style>
    body {{ font-family: 'Inter', system-ui, -apple-system, sans-serif; }}
    .filter-btn {{ cursor: pointer; transition: all .15s; }}
    .job-card {{ transition: box-shadow .2s; }}
    .job-card:hover {{ box-shadow: 0 8px 24px rgba(0,0,0,.12); }}
  </style>
</head>
<body class="bg-gray-50 min-h-screen">
"""

    # Cards HTML
    cards_html = ""
    for job in jobs:
        cards_html += _build_card(job)

    cards_section = f"""
<div class="max-w-7xl mx-auto px-4 pb-4">
  <div id="cards" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 mt-2">
    {cards_html}
  </div>
  <p class="text-center text-xs text-gray-400 mt-8 pb-4">
    Generado {fecha} &mdash; Scraper Robusto 4 filtros &mdash; Referencia OCOBO $15.6M Score 17
  </p>
</div>
"""

    html = (
        head
        + _build_header(excel_path, total, n_alertas, ciudades_counter, fecha)
        + _build_stats(total_premium, total_alto, total_medio, salario_prom, salario_max, score_prom)
        + _build_alert_banner(n_alertas)
        + _build_filters(total, total_premium, total_alto, total_medio)
        + cards_section
        + _JS
        + "\n</body>\n</html>"
    )

    out = f"data/dashboard_{datetime.now().strftime('%Y%m%d_%H%M')}_ROBUSTO.html"
    with open(out, "w", encoding="utf-8") as fh:
        fh.write(html)

    print(f"[OK] Dashboard ROBUSTO generado: {out} -- {total} cargos | Premium {total_premium} | Alto {total_alto} | Medio {total_medio}")
    return out


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Uso: python scraper/dashboard_generator.py data/PREMIUM_director_proyectos_*.xlsx")
        sys.exit(1)
    generar_dashboard(sys.argv[1])
