import os
from flask import Flask, request, render_template, redirect, url_for, send_from_directory
from db_utils import init_db, insert_or_update, fetch_all_records, delete_by_id
from image_filter import convert_to_colored_sketch
import pandas as pd
import uuid
import cv2

# Setup
app = Flask(__name__)
UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# DB Setup
DB_PATH = 'students.db'
TABLE_NAME = 'students'
SCHEMA = {
    'student_id': 'TEXT',
    'first_name': 'TEXT',
    'last_name': 'TEXT',
    'dob': 'TEXT',
    'amount_due': 'TEXT'
}
PRIMARY_KEY = 'student_id'
init_db(DB_PATH, TABLE_NAME, SCHEMA, PRIMARY_KEY)


@app.route('/')
def index():
    students = fetch_all_records(DB_PATH, TABLE_NAME)
    return render_template('index.html', students=students)

@app.route('/edit_student/<student_id>')
def edit_student(student_id):
    df = fetch_all_records(DB_PATH, TABLE_NAME)
    student = df[df['student_id'] == student_id].iloc[0].to_dict()
    return render_template('index.html', students=df, edit_student=student)

@app.route('/update_student', methods=['POST'])
def update_student():
    data = {
        'student_id': request.form['student_id'],
        'first_name': request.form['first_name'],
        'last_name': request.form['last_name'],
        'dob': request.form['dob'],
        'amount_due': request.form['amount_due'],
    }
    insert_or_update(DB_PATH, TABLE_NAME, data, PRIMARY_KEY)
    return redirect(url_for('index'))


@app.route('/add_student', methods=['POST'])
def add_student():
    data = {
        'student_id': request.form['student_id'],
        'first_name': request.form['first_name'],
        'last_name': request.form['last_name'],
        'dob': request.form['dob'],
        'amount_due': request.form['amount_due'],
    }
    insert_or_update(DB_PATH, TABLE_NAME, data, PRIMARY_KEY)
    return redirect(url_for('index'))


@app.route('/delete_student/<student_id>', methods=['GET', 'POST'])
def delete_student(student_id):
    delete_by_id(DB_PATH, TABLE_NAME, student_id)
    return redirect(url_for('index'))


@app.route('/upload_image', methods=['POST'])
def upload_image():
    file = request.files['image']
    if not file:
        return redirect(url_for('index'))

    # Save original
    filename = str(uuid.uuid4()) + '.png'
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)

    # Apply sketch filter
    sketch = convert_to_colored_sketch(filepath)
    sketch_path = os.path.join(app.config['UPLOAD_FOLDER'], 'sketch_' + filename)
    cv2.imwrite(sketch_path, sketch)

    # Display sketch
    students = fetch_all_records(DB_PATH, TABLE_NAME)
    return render_template('index.html', students=students, sketch_filename='sketch_' + filename)


@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


if __name__ == '__main__':
    app.run(debug=True)