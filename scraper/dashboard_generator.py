import pandas as pd
from datetime import datetime
from .db import get_connection

def generar_dashboard():
    """Genera un reporte HTML leyendo directamente de SQLite (estado NUEVA)."""
    conn = get_connection()
    df = pd.read_sql_query("SELECT * FROM ofertas WHERE estado = 'NUEVA' ORDER BY nivel ASC, score_keywords DESC", conn)
    conn.close()
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M')
    file_path = f"data/dashboard_{timestamp}_ROBUSTO.html"
    
    html_content = f"""
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <meta name="referrer" content="no-referrer">
        <title>Dashboard de Vacantes Estratégicas</title>
        <style>
            body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #f4f7f6; color: #333; margin: 0; padding: 20px; }}
            h1 {{ color: #2c3e50; text-align: center; }}
            .stats {{ display: flex; justify-content: center; gap: 20px; margin-bottom: 30px; }}
            .stat-box {{ background: white; padding: 15px 25px; border-radius: 8px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); text-align: center; }}
            .stat-box h3 {{ margin: 0; color: #7f8c8d; font-size: 14px; text-transform: uppercase; }}
            .stat-box p {{ margin: 10px 0 0 0; font-size: 24px; font-weight: bold; color: #2980b9; }}
            table {{ width: 100%; border-collapse: collapse; background: white; box-shadow: 0 4px 6px rgba(0,0,0,0.1); border-radius: 8px; overflow: hidden; }}
            th, td {{ padding: 12px 15px; text-align: left; border-bottom: 1px solid #ddd; }}
            th {{ background-color: #2980b9; color: white; text-transform: uppercase; font-size: 14px; }}
            tr:hover {{ background-color: #f1f1f1; }}
            .nivel-PREMIUM {{ font-weight: bold; color: #d35400; }}
            .nivel-ALTO {{ font-weight: bold; color: #27ae60; }}
            .nivel-MEDIO {{ font-weight: bold; color: #f39c12; }}
            .btn {{ display: inline-block; padding: 6px 12px; background-color: #3498db; color: white; text-decoration: none; border-radius: 4px; font-size: 12px; }}
            .btn:hover {{ background-color: #2980b9; }}
        </style>
    </head>
    <body>
        <h1>Reporte de Vacantes (Extraídas Hoy)</h1>
        
        <div class="stats">
            <div class="stat-box"><h3>Total Nuevas</h3><p>{len(df)}</p></div>
            <div class="stat-box"><h3>PREMIUM</h3><p>{len(df[df['nivel'] == 'PREMIUM']) if not df.empty else 0}</p></div>
            <div class="stat-box"><h3>ALTO</h3><p>{len(df[df['nivel'] == 'ALTO']) if not df.empty else 0}</p></div>
        </div>

        <table>
            <thead>
                <tr>
                    <th>Nivel</th>
                    <th>Título</th>
                    <th>Empresa</th>
                    <th>Ciudad</th>
                    <th>Salario Extraído</th>
                    <th>Score</th>
                    <th>Acción</th>
                </tr>
            </thead>
            <tbody>
    """
    
    if not df.empty:
        for _, row in df.iterrows():
            html_content += f"""
                <tr>
                    <td class="nivel-{row.get('nivel', '')}">{row.get('nivel', '')}</td>
                    <td>{row.get('titulo', '')}</td>
                    <td>{row.get('empresa', '')}</td>
                    <td>{row.get('ciudad', '')}</td>
                    <td>${row.get('salario_num', 0):,}</td>
                    <td>{row.get('score_keywords', 0)}</td>
                    <td><a href="{row.get('url', '#')}" target="_blank" class="btn">Ver Oferta</a></td>
                </tr>
            """
    else:
        html_content += "<tr><td colspan='7' style='text-align: center;'>No se encontraron vacantes nuevas hoy.</td></tr>"
        
    html_content += """
            </tbody>
        </table>
    </body>
    </html>
    """
    
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(html_content)
        
    print(f"[*] Dashboard HTML generado: {file_path}")

if __name__ == "__main__":
    generar_dashboard()
