import pandas as pd
from datetime import datetime
from .db import get_connection

def generar_dashboard():
    """Genera un reporte HTML leyendo directamente de SQLite (estado NUEVA)."""
    conn = get_connection()
    df = pd.read_sql_query("SELECT * FROM ofertas WHERE estado = 'NUEVA' ORDER BY nivel ASC, score_keywords DESC", conn)
    conn.close()
    
    # Nombre estático para no generar basura en el repositorio
    file_path = "index.html"
    
    # Obtener ciudades únicas para el filtro
    cities = sorted([c for c in df['ciudad'].dropna().unique() if str(c).strip()]) if not df.empty else []
    city_options = '<option value="">Todas las Ciudades</option>' + ''.join([f'<option value="{c}">{c}</option>' for c in cities])
    
    html_content = f"""
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <meta name="referrer" content="no-referrer">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Dashboard Corporativo - Vacantes</title>
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
        <script src="https://cdn.tailwindcss.com"></script>
        <script>
            tailwind.config = {{
                theme: {{
                    extend: {{
                        fontFamily: {{
                            sans: ['Inter', 'sans-serif'],
                        }},
                        colors: {{
                            navy: {{
                                800: '#1e3a8a',
                                900: '#1e3a5f',
                            }},
                        }}
                    }}
                }}
            }}
        </script>
        <style>
            body {{ font-family: 'Inter', sans-serif; }}
            .nivel-PREMIUM {{ color: #b45309; background-color: #fef3c7; border-color: #f59e0b; }}
            .nivel-ALTO {{ color: #15803d; background-color: #dcfce7; border-color: #22c55e; }}
            .nivel-MEDIO {{ color: #4338ca; background-color: #e0e7ff; border-color: #6366f1; }}
            .badge {{ display: inline-block; padding: 0.25em 0.75em; font-size: 0.75rem; font-weight: 600; border-radius: 9999px; border-width: 1px; text-align: center; }}
        </style>
    </head>
    <body class="bg-slate-50 text-slate-800 antialiased">
        <div class="min-h-screen p-6 md:p-10 max-w-7xl mx-auto">
            
            <header class="mb-10">
                <h1 class="text-3xl font-bold text-navy-900 mb-2">Reporte Ejecutivo de Vacantes</h1>
                <p class="text-slate-500">Última actualización: {datetime.now().strftime('%Y-%m-%d %H:%M')}</p>
            </header>

            <!-- Stats -->
            <div class="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
                <div class="bg-white rounded-xl shadow-sm border border-slate-200 p-6 flex flex-col items-center">
                    <h3 class="text-sm font-semibold text-slate-400 uppercase tracking-wider">Total Nuevas</h3>
                    <p class="text-4xl font-bold text-navy-800 mt-2">{len(df)}</p>
                </div>
                <div class="bg-white rounded-xl shadow-sm border border-slate-200 p-6 flex flex-col items-center">
                    <h3 class="text-sm font-semibold text-slate-400 uppercase tracking-wider">Nivel Premium</h3>
                    <p class="text-4xl font-bold text-amber-600 mt-2">{len(df[df['nivel'] == 'PREMIUM']) if not df.empty else 0}</p>
                </div>
                <div class="bg-white rounded-xl shadow-sm border border-slate-200 p-6 flex flex-col items-center">
                    <h3 class="text-sm font-semibold text-slate-400 uppercase tracking-wider">Nivel Alto</h3>
                    <p class="text-4xl font-bold text-emerald-600 mt-2">{len(df[df['nivel'] == 'ALTO']) if not df.empty else 0}</p>
                </div>
            </div>

            <!-- Filters -->
            <div class="bg-white rounded-xl shadow-sm border border-slate-200 p-4 mb-6 flex flex-col md:flex-row gap-4 items-center">
                <div class="flex-1 w-full relative">
                    <svg class="w-5 h-5 absolute left-3 top-2.5 text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"></path></svg>
                    <input type="text" id="searchInput" placeholder="Buscar por cargo o empresa..." class="w-full pl-10 pr-4 py-2 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-navy-800 focus:border-transparent text-sm">
                </div>
                <div class="w-full md:w-64">
                    <select id="citySelect" class="w-full px-4 py-2 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-navy-800 focus:border-transparent text-sm text-slate-600 bg-white cursor-pointer">
                        {city_options}
                    </select>
                </div>
            </div>

            <!-- Table -->
            <div class="bg-white rounded-xl shadow-sm border border-slate-200 overflow-hidden">
                <div class="overflow-x-auto">
                    <table class="w-full text-left border-collapse" id="jobsTable">
                        <thead>
                            <tr class="bg-slate-100 border-b border-slate-200 text-slate-600 uppercase text-xs tracking-wider">
                                <th class="px-6 py-4 font-semibold">Portal</th>
                                <th class="px-6 py-4 font-semibold">Nivel</th>
                                <th class="px-6 py-4 font-semibold">Título</th>
                                <th class="px-6 py-4 font-semibold">Empresa</th>
                                <th class="px-6 py-4 font-semibold">Ciudad</th>
                                <th class="px-6 py-4 font-semibold">Salario</th>
                                <th class="px-6 py-4 font-semibold">Score</th>
                                <th class="px-6 py-4 font-semibold text-center">Acción</th>
                            </tr>
                        </thead>
                        <tbody class="divide-y divide-slate-100 text-sm">
    """
    
    if not df.empty:
        for _, row in df.iterrows():
            portal_str = str(row.get('portal', '')).capitalize()
            if not portal_str:
                portal_str = str(row.get('origen', '')).capitalize()
            
            titulo = str(row.get('titulo', ''))
            empresa = str(row.get('empresa', ''))
            ciudad = str(row.get('ciudad', ''))
            nivel = str(row.get('nivel', ''))
            salario = row.get('salario_num', 0)
            score = row.get('score_keywords', 0)
            url = row.get('url', '#')
            
            html_content += f"""
                            <tr class="hover:bg-slate-50 transition-colors duration-150 job-row">
                                <td class="px-6 py-4 font-medium text-slate-700">{portal_str}</td>
                                <td class="px-6 py-4"><span class="badge nivel-{nivel}">{nivel}</span></td>
                                <td class="px-6 py-4 font-semibold text-navy-800 job-title">{titulo}</td>
                                <td class="px-6 py-4 text-slate-600 job-company">{empresa}</td>
                                <td class="px-6 py-4 text-slate-500 job-city">{ciudad}</td>
                                <td class="px-6 py-4 text-slate-600 font-medium">${salario:,}</td>
                                <td class="px-6 py-4 text-slate-500">{score}</td>
                                <td class="px-6 py-4 text-center">
                                    <a href="{url}" target="_blank" rel="noopener noreferrer" class="inline-flex items-center px-4 py-2 bg-navy-800 text-white rounded-lg text-xs font-semibold tracking-wide hover:bg-navy-900 hover:shadow-md transition-all duration-200">
                                        Ver Oferta
                                    </a>
                                </td>
                            </tr>
            """
    else:
        html_content += """
                            <tr><td colspan="8" class="px-6 py-10 text-center text-slate-500">No se encontraron vacantes nuevas hoy.</td></tr>
        """
        
    html_content += """
                        </tbody>
                    </table>
                </div>
            </div>
            
        </div>

        <script>
            document.addEventListener('DOMContentLoaded', function() {
                const searchInput = document.getElementById('searchInput');
                const citySelect = document.getElementById('citySelect');
                const rows = document.querySelectorAll('.job-row');

                function filterTable() {
                    const searchTerm = searchInput.value.toLowerCase();
                    const selectedCity = citySelect.value.toLowerCase();

                    rows.forEach(row => {
                        const title = row.querySelector('.job-title').textContent.toLowerCase();
                        const company = row.querySelector('.job-company').textContent.toLowerCase();
                        const city = row.querySelector('.job-city').textContent.toLowerCase();

                        const matchesSearch = title.includes(searchTerm) || company.includes(searchTerm);
                        const matchesCity = selectedCity === "" || city === selectedCity;

                        if (matchesSearch && matchesCity) {
                            row.style.display = '';
                        } else {
                            row.style.display = 'none';
                        }
                    });
                }

                searchInput.addEventListener('input', filterTable);
                citySelect.addEventListener('change', filterTable);
            });
        </script>
    </body>
    </html>
    """
    
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(html_content)
        
    print(f"[*] Dashboard HTML generado: {file_path}")

if __name__ == "__main__":
    generar_dashboard()
