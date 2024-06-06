# app.py
from flask import Flask, request, jsonify, render_template, redirect, url_for, session, flash
from models import db, User, TrainingDataset, Model, Score
from flask_migrate import Migrate
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'your_secret_key'

db.init_app(app)
migrate = Migrate(app, db)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(Username=username).first()
        if user and check_password_hash(user.password, password):
            session['user_id'] = user.UserID
            session['username'] = user.Username
            session['user_type'] = user.UserType
            flash('Login successful!', 'success')
            return redirect(url_for('index'))
        flash('Invalid credentials', 'danger')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('username', None)
    session.pop('user_type', None)
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))

#@app.route('/register', methods=['GET', 'POST'])
#def register():
    #if request.method == 'POST':
        #password = request.form['password']
        #user_type = request.form['user_type']
        #hashed_password = generate_password_hash(password, method='sha256')
        #new_user = User(Username=username, password=hashed_password, UserType=user_type)
        #db.session.add(new_user)
        #db.session.commit()
        #flash('Registration successful!', 'success')
        #return redirect(url_for('login'))
    #return render_template('register.html')

# 教師端
@app.route('/teacher', methods=['GET', 'POST'])
def teacher_dashboard():
    if 'user_type' in session and session['user_type'] == 'Teacher':
        if request.method == 'POST':
            dataset_name = request.form['dataset_name']
            training_data_path = request.form['training_data_path']
            validation_data_path = request.form['validation_data_path']
            new_dataset = TrainingDataset(
                DatasetName=dataset_name,
                TeacherID=session['user_id'],
                TrainingDataPath=training_data_path,
                ValidationDataPath=validation_data_path
            )
            db.session.add(new_dataset)
            db.session.commit()
            flash('Dataset uploaded successfully!', 'success')
        datasets = TrainingDataset.query.filter_by(TeacherID=session['user_id']).all()
        return render_template('teacher.html', datasets=datasets)
    flash('Unauthorized access!', 'danger')
    return redirect(url_for('login'))

# 學生端
@app.route('/student', methods=['GET', 'POST'])
def student_dashboard():
    if 'user_type' in session and session['user_type'] == 'Student':
        datasets = TrainingDataset.query.all()
        if request.method == 'POST':
            model_name = request.form['model_name']
            dataset_id = request.form['dataset_id']
            model_path = request.form['model_path']
            new_model = Model(
                ModelName=model_name,
                StudentID=session['user_id'],
                DatasetID=dataset_id,
                ModelPath=model_path
            )
            db.session.add(new_model)
            db.session.commit()
            flash('Model uploaded successfully!', 'success')
            return redirect(url_for('rankings'))
        return render_template('student.html', datasets=datasets)
    flash('Unauthorized access!', 'danger')
    return redirect(url_for('login'))

@app.route('/rankings')
def rankings():
    models = Model.query.order_by(Model.Accuracy.desc()).all()
    return render_template('rankings.html', models=models)

if __name__ == '__main__':
    app.run(debug=True)
