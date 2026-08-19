from flask import Flask, render_template, request, redirect, url_for, Response
import sqlite3, os
import pandas as pd
from io import BytesIO

app = Flask(__name__)
DB_PATH = r"C:\Users\Pc\Desktop\MiAppPython\MiBaseDatos\database.db"

os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

# Funciones auxiliares para conversión segura
def to_int(value):
    try:
        return int(value)
    except (ValueError, TypeError):
        return 0

def to_float(value):
    try:
        return float(value)
    except (ValueError, TypeError):
        return 0.0

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    # Reportes de células
    c.execute('''CREATE TABLE IF NOT EXISTS cell_reports (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        cell_name TEXT,
        meeting_date TEXT,
        adults INTEGER,
        youth INTEGER,
        children INTEGER,
        friends INTEGER,
        visits INTEGER,
        house_leader TEXT,
        biblical_theme TEXT,
        central_text TEXT,
        offering REAL,
        needs TEXT,
        spiritual_level TEXT,
        attendance_level INTEGER
    )''')

    # Nuevos convertidos
    c.execute('''CREATE TABLE IF NOT EXISTS new_converts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        full_name TEXT,
        contact TEXT,
        address TEXT,
        birth_date TEXT,
        age INTEGER,
        status TEXT,
        conversion_date TEXT,
        decision_type TEXT,
        assigned_cell TEXT,
        observation TEXT
    )''')

    # Estadísticas de miembros
    c.execute('''CREATE TABLE IF NOT EXISTS members_stats (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        full_name TEXT,
        cell TEXT,
        sex TEXT,
        growth_eval INTEGER,
        discipleship_type TEXT,
        ministry TEXT,
        status TEXT DEFAULT 'activo'
    )''')

    conn.commit()
    conn.close()

init_db()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/cell_report', methods=['POST'])
def cell_report():
    data = request.form.to_dict()
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''INSERT INTO cell_reports (
        cell_name, meeting_date, adults, youth, children, friends, visits,
        house_leader, biblical_theme, central_text, offering, needs, spiritual_level, attendance_level
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
    (
        data['cell_name'],
        data['meeting_date'],
        to_int(data.get('adults')),
        to_int(data.get('youth')),
        to_int(data.get('children')),
        to_int(data.get('friends')),
        to_int(data.get('visits')),
        data['house_leader'],
        data['biblical_theme'],
        data['central_text'],
        to_float(data.get('offering')),
        data['needs'],
        data['spiritual_level'],
        to_int(data.get('attendance_level'))
    ))
    conn.commit()
    conn.close()
    return redirect(url_for('reports'))

@app.route('/new_convert', methods=['POST'])
def new_convert():
    data = request.form.to_dict()
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''INSERT INTO new_converts (
        full_name, contact, address, birth_date, age, status,
        conversion_date, decision_type, assigned_cell, observation
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
    (
        data['full_name'], data['contact'], data['address'], data['birth_date'],
        to_int(data.get('age')),
        data['status'], data['conversion_date'], data['decision_type'],
        data['assigned_cell'], data['observation']
    ))
    conn.commit()
    conn.close()
    return redirect(url_for('reports'))

@app.route('/member_stats', methods=['POST'])
def member_stats():
    data = request.form.to_dict()
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''INSERT INTO members_stats (
        full_name, cell, sex, growth_eval, discipleship_type, ministry
    ) VALUES (?, ?, ?, ?, ?, ?)''',
    (
        data['full_name'], data['cell'], data['sex'],
        to_int(data.get('growth_eval')),
        data['discipleship_type'], data['ministry']
    ))
    conn.commit()
    conn.close()
    return redirect(url_for('reports'))

@app.route('/reports')
def reports():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    # Filtros
    date_filter = request.args.get('date')
    cell_filter = request.args.get('cell_name')

    query = "SELECT * FROM cell_reports WHERE 1=1"
    params = []

    if date_filter:
        query += " AND meeting_date = ?"
        params.append(date_filter)

    if cell_filter:
        query += " AND cell_name = ?"
        params.append(cell_filter)

    c.execute(query, params)
    cell_rows = c.fetchall()

    # Convertir columnas numéricas
    cell_rows = [
        (
            r[0], r[1], r[2],
            to_int(r[3]), to_int(r[4]), to_int(r[5]),
            to_int(r[6]), to_int(r[7]),
            r[8], r[9], r[10], to_float(r[11]),
            r[12], r[13], to_int(r[14])
        )
        for r in cell_rows
    ]

    c.execute("SELECT * FROM new_converts")
    convert_rows = c.fetchall()

    c.execute("SELECT * FROM members_stats")
    member_rows = c.fetchall()

    conn.close()
    return render_template('reports.html',
                           cell_reports=cell_rows,
                           new_converts=convert_rows,
                           members_stats=member_rows)

# Exportar CSV
@app.route('/export/cell_reports')
def export_cell_reports():
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query("SELECT * FROM cell_reports", conn)
    conn.close()
    output = df.to_csv(index=False)
    return Response(output,
                    mimetype="text/csv",
                    headers={"Content-Disposition": "attachment;filename=cell_reports.csv"})

# Exportar Excel
@app.route('/export/cell_reports_excel')
def export_cell_reports_excel():
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query("SELECT * FROM cell_reports", conn)
    conn.close()
    output = BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Reportes")
    excel_data = output.getvalue()
    return Response(excel_data,
                    mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    headers={"Content-Disposition": "attachment;filename=cell_reports.xlsx"})

# Detalle de célula
@app.route('/cell/<int:cell_id>')
def cell_detail(cell_id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT * FROM cell_reports WHERE id=?", (cell_id,))
    cell = c.fetchone()
    conn.close()
    return render_template('cell_detail.html', cell=cell)

# Marcar miembro como desertó
@app.route('/member/<int:member_id>/update')
def member_update(member_id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("UPDATE members_stats SET status='desertó' WHERE id=?", (member_id,))
    conn.commit()
    conn.close()
    return redirect(url_for('reports'))

@app.route('/cell/<int:cell_id>/update', methods=['POST'])
def cell_update(cell_id):
    data = request.form.to_dict()
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''UPDATE cell_reports 
                 SET needs=?, spiritual_level=?, attendance_level=? 
                 WHERE id=?''',
              (data['needs'], data['spiritual_level'], to_int(data.get('attendance_level')), cell_id))
    conn.commit()
    conn.close()
    return redirect(url_for('cell_detail', cell_id=cell_id))

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)

