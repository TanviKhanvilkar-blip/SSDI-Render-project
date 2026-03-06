import os
from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "dev_secret_key_123")

# DATABASE CONFIGURATION
# Render provides the DATABASE_URL environment variable automatically.
# We keep your hardcoded URL as a backup for local testing.
DEFAULT_DB = 'postgresql://ssdi_student_database_user:XVsK3dNaRlQmIKR78HukE87lPkbJfj5J@dpg-d6l382paae7s73fuim90-a.singapore-postgres.render.com/ssdi_student_database'
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', DEFAULT_DB)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    sapid = db.Column(db.String(20), unique=True, nullable=False)
    age = db.Column(db.Integer, nullable=False)
    marks = db.Column(db.Float, nullable=False)

with app.app_context():
    db.create_all()

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST' and 'submit_student' in request.form:
        try:
            new_student = Student(
                name=request.form['name'],
                sapid=request.form['sapid'],
                age=int(request.form['age']),
                marks=float(request.form['marks'])
            )
            db.session.add(new_student)
            db.session.commit()
            return redirect(url_for('index', active_tab='view'))
        except Exception as e:
            db.session.rollback()
            return f"Error: {e}"

    # Filtering Logic
    query = Student.query
    name_filter = request.args.get('name')
    sapid_filter = request.args.get('sapid')
    if name_filter:
        query = query.filter(Student.name.ilike(f'%{name_filter}%'))
    if sapid_filter:
        query = query.filter(Student.sapid.contains(sapid_filter))
    
    students = query.all()
    active_tab = request.args.get('active_tab', 'entry')
    return render_template('index.html', students=students, active_tab=active_tab)

if __name__ == '__main__':
    app.run(debug=True)