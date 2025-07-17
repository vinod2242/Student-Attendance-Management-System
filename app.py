from flask import Flask, render_template, request, redirect, url_for
import sqlite3

app = Flask(__name__)

# Database setup
def init_db():
    conn = sqlite3.connect('attendance.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            roll_number TEXT NOT NULL UNIQUE
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS attendance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER,
            date TEXT,
            status TEXT,
            FOREIGN KEY(student_id) REFERENCES students(id)
        )
    ''')
    conn.commit()
    conn.close()

init_db()

@app.route('/')
def index():
    conn = sqlite3.connect('attendance.db')
    c = conn.cursor()
    c.execute('SELECT * FROM students')
    students = c.fetchall()
    conn.close()
    return render_template('index.html', students=students)

@app.route('/add', methods=['GET', 'POST'])
def add_student():
    if request.method == 'POST':
        name = request.form['name']
        roll_number = request.form['roll_number']
        conn = sqlite3.connect('attendance.db')
        c = conn.cursor()
        try:
            c.execute('INSERT INTO students (name, roll_number) VALUES (?, ?)', (name, roll_number))
            conn.commit()
        except sqlite3.IntegrityError:
            pass  # Handles duplicate roll_number gracefully
        conn.close()
        return redirect(url_for('add_student'))
    
    # Fetch existing students to display for removal
    conn = sqlite3.connect('attendance.db')
    c = conn.cursor()
    c.execute('SELECT * FROM students')
    students = c.fetchall()
    conn.close()
    return render_template('add_student.html', students=students)

@app.route('/remove_student/<int:student_id>', methods=['POST'])
def remove_student(student_id):
    conn = sqlite3.connect('attendance.db')
    c = conn.cursor()
    # Remove related attendance records first to maintain FK integrity
    c.execute('DELETE FROM attendance WHERE student_id = ?', (student_id,))
    c.execute('DELETE FROM students WHERE id = ?', (student_id,))
    conn.commit()
    conn.close()
    return redirect(url_for('add_student'))

@app.route('/mark', methods=['GET', 'POST'])
def mark_attendance():
    conn = sqlite3.connect('attendance.db')
    c = conn.cursor()
    c.execute('SELECT * FROM students')
    students = c.fetchall()
    if request.method == 'POST':
        date = request.form['date']
        for student in students:
            status = request.form.get(f'status_{student[0]}')
            c.execute('INSERT INTO attendance (student_id, date, status) VALUES (?, ?, ?)', (student[0], date, status))
        conn.commit()
        conn.close()
        return redirect(url_for('index'))
    conn.close()
    return render_template('mark_attendance.html', students=students)

@app.route('/attendance')
def view_attendance():
    conn = sqlite3.connect('attendance.db')
    c = conn.cursor()
    c.execute('''
        SELECT students.name, students.roll_number, attendance.date, attendance.status
        FROM attendance
        JOIN students ON attendance.student_id = students.id
        ORDER BY attendance.date DESC
    ''')
    records = c.fetchall()
    conn.close()
    if not records:
        message = "No attendance records available."
        return render_template('view_attendance.html', records=None, message=message)
    return render_template('view_attendance.html', records=records)


if __name__ == '__main__':
    app.run(debug=True)
