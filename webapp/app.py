import os
import sys
from pathlib import Path

# сделать корневую папку проекта доступной для импортов, когда скрипт запускают из webapp/
ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from flask import Flask, render_template, request, redirect, url_for, flash, session
from database.models import SessionLocal, Student
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET', 'dev-secret')

# simple password protection (optional)
UI_PASSWORD = os.getenv('UI_PASSWORD')


def check_auth():
    if UI_PASSWORD is None:
        return True
    return session.get('logged_in')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if UI_PASSWORD is None:
        return redirect(url_for('students'))
    if request.method == 'POST':
        pwd = request.form.get('password')
        if pwd == UI_PASSWORD:
            session['logged_in'] = True
            return redirect(url_for('students'))
        flash('Неверный пароль', 'danger')
    return render_template('login.html')


@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('login'))


@app.route('/')
@app.route('/students')
def students():
    if not check_auth():
        return redirect(url_for('login'))
    db = SessionLocal()
    students = db.query(Student).order_by(Student.id).all()
    db.close()
    return render_template('students.html', students=students)


@app.route('/students/add', methods=['GET', 'POST'])
def add_student():
    if not check_auth():
        return redirect(url_for('login'))
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        if not name:
            flash('Имя не может быть пустым', 'warning')
            return redirect(url_for('add_student'))
        db = SessionLocal()
        s = Student(name=name)
        db.add(s)
        db.commit()
        db.refresh(s)
        db.close()
        flash(f'Ученик {name} добавлен (ID {s.id})', 'success')
        return redirect(url_for('students'))
    return render_template('form.html', action='add')


@app.route('/students/edit/<int:student_id>', methods=['GET', 'POST'])
def edit_student(student_id):
    if not check_auth():
        return redirect(url_for('login'))
    db = SessionLocal()
    student = db.get(Student, student_id)
    if not student:
        db.close()
        flash('Ученик не найден', 'danger')
        return redirect(url_for('students'))
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        if not name:
            flash('Имя не может быть пустым', 'warning')
            return redirect(url_for('edit_student', student_id=student_id))
        student.name = name
        db.commit()
        db.close()
        flash('Изменения сохранены', 'success')
        return redirect(url_for('students'))
    db.close()
    return render_template('form.html', action='edit', student=student)


@app.route('/students/delete/<int:student_id>', methods=['POST'])
def delete_student(student_id):
    if not check_auth():
        return redirect(url_for('login'))
    db = SessionLocal()
    student = db.get(Student, student_id)
    if not student:
        db.close()
        flash('Ученик не найден', 'danger')
        return redirect(url_for('students'))
    db.delete(student)
    db.commit()
    db.close()
    flash('Ученик удалён', 'success')
    return redirect(url_for('students'))


if __name__ == '__main__':
    app.run(debug=True)
