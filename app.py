from flask import Flask, render_template, request, redirect, url_for, Response
import sqlite3
import os
import pandas as pd
from io import BytesIO

app = Flask(__name__)

# Ruta dinámica adaptada a cualquier sistema (Windows local o Servidor Linux/Cloud)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "MiBaseDatos", "database.db")
os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

# Funciones auxiliares para conversión segura
def to_int(valor):
    try:
        return int(valor)
    except (ValueError, TypeError):
        return 0

def to_float(valor):
    try:
        return float(valor)
    except (ValueError, TypeError):
        return 0.0

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    # Reportes de células
    c.execute('''CREATE TABLE IF NOT EXISTS cell_reports (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre_celda TEXT,
        fecha_reunion TEXT,
        adultos INTEGER,
        jovenes INTEGER,
        ninos INTEGER,
        amigos INTEGER,
        visitas INTEGER,
        lider_casa TEXT,
        tema_biblico TEXT,
        texto_central TEXT,
        ofrenda REAL,
        necesidades TEXT,
        nivel_espiritual TEXT,
        nivel_asistencia INTEGER
    )''')
    
    # Nuevos convertidos
    c.execute('''CREATE TABLE IF NOT EXISTS new_converts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre_completo TEXT,
        contacto TEXT,
        direccion TEXT,
        fecha_nacimiento TEXT,
        edad INTEGER,
        estado TEXT,
        fecha_conversion TEXT,
        tipo_decision TEXT,
        celda_asignada TEXT,
        observacion TEXT
    )''')
    
    # Estadísticas de miembros
    c.execute('''CREATE TABLE IF NOT EXISTS members_stats (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre_completo TEXT,
        celula TEXT,
        sexo TEXT,
        evaluacion_crecimiento INTEGER,
        tipo_discipulado TEXT,
        ministerio TEXT,
        estado TEXT DEFAULT 'activo'
    )''')
    
    conn.commit()
    conn.close()

init_db()

@app.route('/')
def index():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT DISTINCT nombre_celda FROM cell_reports WHERE nombre_celda IS NOT NULL AND nombre_celda != ''")
    celulas = [fila[0] for fila in c.fetchall()]
    conn.close()
    return render_template('index.html', celulas=celulas)

@app.route('/cell_report', methods=['POST'])
def cell_report():
    datos = request.form.to_dict()
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''INSERT INTO cell_reports (
        nombre_celda, fecha_reunion, adultos, jovenes, ninos, amigos, visitas,
        lider_casa, tema_biblico, texto_central, ofrenda, necesidades,
        nivel_espiritual, nivel_asistencia
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''', (
        datos.get('cell_name'),
        datos.get('fecha_reunion'),
        to_int(datos.get('adults')),
        to_int(datos.get('youth')),
        to_int(datos.get('children')),
        to_int(datos.get('friends')),
        to_int(datos.get('visits')),
        datos.get('lider_casa'),
        datos.get('tema_biblico'),
        datos.get('texto_central'),
        to_float(datos.get('offering')),
        datos.get('necesidades') or datos.get('needs'),
        datos.get('nivel_espiritual') or datos.get('spiritual_level'),
        to_int(datos.get('attendance_level'))
    ))
    conn.commit()
    conn.close()
    return redirect(url_for('informes'))

@app.route('/new_convert', methods=['POST'])
def new_convert():
    datos = request.form.to_dict()
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''INSERT INTO new_converts (
        nombre_completo, contacto, direccion, fecha_nacimiento, edad, estado,
        fecha_conversion, tipo_decision, celda_asignada, observacion
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''', (
        datos.get('full_name'),
        datos.get('contact'),
        datos.get('address'),
        datos.get('birth_date'),
        to_int(datos.get('age')),
        datos.get('estado'),
        datos.get('fecha_conversion'),
        datos.get('tipo_decision'),
        datos.get('celda_asignada'),
        datos.get('observacion')
    ))
    conn.commit()
    conn.close()
    return redirect(url_for('informes'))

@app.route('/member_stats', methods=['POST'])
def member_stats():
    datos = request.form.to_dict()
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''INSERT INTO members_stats (
        nombre_completo, celula, sexo, evaluacion_crecimiento, tipo_discipulado, ministerio
    ) VALUES (?, ?, ?, ?, ?, ?)''', (
        datos.get('full_name'),
        datos.get('cell'),
        datos.get('sex'),
        to_int(datos.get('growth_eval')),
        datos.get('tipo_discipulado'),
        datos.get('ministerio')
    ))
    conn.commit()
    conn.close()
    return redirect(url_for('informes'))

@app.route('/converts')
def converts():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT * FROM new_converts ORDER BY id DESC")
    convertir_filas = c.fetchall()
    
    c.execute("SELECT DISTINCT nombre_celda FROM cell_reports WHERE nombre_celda IS NOT NULL AND nombre_celda != ''")
    celulas = [fila[0] for fila in c.fetchall()]
    conn.close()
    
    return render_template('converts.html', nuevos_convertidores=convertir_filas, celulas=celulas)

@app.route('/reports')
def informes():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    # Filtros
    filtro_fecha = request.args.get('fecha')
    filtro_celda = request.args.get('nombre_celda')
    
    consulta = "SELECT * FROM cell_reports WHERE 1=1"
    params = []
    
    if filtro_fecha:
        consulta += " AND fecha_reunion = ?"
        params.append(filtro_fecha)
    if filtro_celda:
        consulta += " AND nombre_celda = ?"
        params.append(filtro_celda)
        
    c.execute(consulta, params)
    filas_de_celdas = c.fetchall()
    
    # Mapeo corregido columna por columna según el schema
    filas_de_celdas = [
        (
            r[0],                  # id
            r[1],                  # nombre_celda
            r[2],                  # fecha_reunion
            to_int(r[3]),          # adultos
            to_int(r[4]),          # jovenes
            to_int(r[5]),          # ninos
            to_int(r[6]),          # amigos
            to_int(r[7]),          # visitas
            r[8],                  # lider_casa
            r[9],                  # tema_biblico
            r[10],                 # texto_central
            to_float(r[11]),       # ofrenda
            r[12],                 # necesidades
            r[13],                 # nivel_espiritual
            to_int(r[14])          # nivel_asistencia
        )
        for r in filas_de_celdas
    ]
    
    c.execute("SELECT * FROM new_converts ORDER BY id DESC")
    convertir_filas = c.fetchall()
    
    c.execute("SELECT * FROM members_stats ORDER BY id DESC")
    filas_miembro = c.fetchall()
    
    c.execute("SELECT DISTINCT nombre_celda FROM cell_reports WHERE nombre_celda IS NOT NULL AND nombre_celda != ''")
    celulas = [fila[0] for fila in c.fetchall()]
    
    conn.close()
    return render_template(
        'reports.html', 
        informes_de_celda=filas_de_celdas, 
        nuevos_convertidores=convertir_filas, 
        estadisticas_miembros=filas_miembro,
        celulas=celulas
    )

# Exportar CSV
@app.route('/export/cell_reports')
def export_cell_reports():
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query("SELECT * FROM cell_reports", conn)
    conn.close()
    salida = df.to_csv(index=False)
    return Response(
        salida, 
        mimetype="text/csv", 
        headers={"Content-Disposition": "attachment;filename=cell_reports.csv"}
    )

# Exportar Excel
@app.route('/export/cell_reports_excel')
def export_cell_reports_excel():
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query("SELECT * FROM cell_reports", conn)
    conn.close()
    salida = BytesIO()
    with pd.ExcelWriter(salida, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Informes")
    datos_de_excel = salida.getvalue()
    return Response(
        datos_de_excel, 
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", 
        headers={"Content-Disposition": "attachment;filename=cell_reports.xlsx"}
    )

# Detalle de célula
@app.route('/cell/<int:cell_id>')
def cell_detail(cell_id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT * FROM cell_reports WHERE id=?", (cell_id,))
    celda = c.fetchone()
    conn.close()
    return render_template('cell_detail.html', cell=celda)

# Marcar miembro como desertó
@app.route('/member/<int:member_id>/update')
def member_update(member_id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("UPDATE members_stats SET estado='desertó' WHERE id=?", (member_id,))
    conn.commit()
    conn.close()
    return redirect(url_for('informes'))

@app.route('/cell/<int:cell_id>/update', methods=['POST'])
def cell_update(cell_id):
    datos = request.form.to_dict()
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''UPDATE cell_reports SET necesidades=?, nivel_espiritual=?, nivel_asistencia=? WHERE id=?''', (
        datos.get('needs') or datos.get('necesidades'), 
        datos.get('spiritual_level') or datos.get('nivel_espiritual'), 
        to_int(datos.get('attendance_level')), 
        cell_id
    ))
    conn.commit()
    conn.close()
    return redirect(url_for('cell_detail', cell_id=cell_id))

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
