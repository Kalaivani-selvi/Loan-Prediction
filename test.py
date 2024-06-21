from flask import Flask, request, render_template, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
# from werkzeug.security import generate_password_hash, check_password_hash
import joblib
import random
import string
import urllib.parse
import pandas as pd
import logging

app = Flask(__name__, static_url_path='/static')
app.secret_key = ''.join(random.choices(string.ascii_letters + string.digits, k=16))
password = urllib.parse.quote_plus('NikiKalai@2003')  # URL encode the password
app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+pymysql://root:{password}@localhost/loan_data'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Define the LoanApp model matching your existing table
# class LoanApp(db.Model):
#     __tablename__ = 'loan_app'
#     id = db.Column(db.Integer, primary_key=True, autoincrement=True)
#     email = db.Column(db.String(120), unique=True, nullable=False)
#     password = db.Column(db.String(120), nullable=False)
#     security_question = db.Column(db.String(120), nullable=False)
#     no_of_dependents = db.Column(db.Integer, nullable=False)
#     education = db.Column(db.String(50), nullable=False)
#     self_employed = db.Column(db.String(50), nullable=False)
#     income_annum = db.Column(db.Float, nullable=False)
#     loan_amount = db.Column(db.Float, nullable=False)
#     loan_term = db.Column(db.Integer, nullable=False)
#     cibil_score = db.Column(db.Integer, nullable=False)
#     residential_assets_value = db.Column(db.Float, nullable=False)
#     commercial_assets_value = db.Column(db.Float, nullable=False)
#     luxury_assets_value = db.Column(db.Float, nullable=False)
#     bank_asset_value = db.Column(db.Float, nullable=False)
#     loan_status = db.Column(db.String(20))  # Add loan_status to the model

class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    security_question = db.Column(db.String(120), nullable=False)
    loan_apps = db.relationship('LoanApp', backref='user', lazy=True)

class LoanApp(db.Model):
    __tablename__ = 'loan_app1'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    gender = db.Column(db.String(10), nullable=False)
    married = db.Column(db.String(3), nullable=False)
    dependents = db.Column(db.String(2), nullable=False)
    education = db.Column(db.String(20), nullable=False)
    self_employed = db.Column(db.String(3), nullable=False)
    applicant_income = db.Column(db.Integer, nullable=False)
    coapplicant_income = db.Column(db.Float, nullable=False)
    loan_amount = db.Column(db.Float, nullable=False)
    loan_amount_term = db.Column(db.Float, nullable=False)
    credit_history = db.Column(db.Float, nullable=False)
    property_area = db.Column(db.String(20), nullable=False)
    predicted_loan_status = db.Column(db.String(1), nullable=False)


# Load the trained model
model = joblib.load('models/loan_approval_model.pkl')

# Home route
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()
        if user and password:
            session['user_id'] = user.id
            return redirect(url_for('form'))
        else:
            flash('Invalid email or password')
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        security_question = request.form['security_question']
        
        new_user = User(email=email, password=password, security_question=security_question)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/f_password', methods=['GET', 'POST'])
def f_password():
    if request.method == 'POST':
        email = request.form['email']
        security_question = request.form['security_question']
        user = User.query.filter_by(email=email, security_question=security_question).first()
        if user:
            session['reset_user_id'] = user.id
            return redirect(url_for('reset_p'))
        else:
            flash('Invalid email or security question')
    return render_template('f_password.html')

@app.route('/reset_p', methods=['GET', 'POST'])
def reset_p():
    if request.method == 'POST':
        new_password = request.form['new_password']
        confirm_password = request.form['confirm_password']
        if new_password == confirm_password:
            user_id = session.get('reset_user_id')
            if user_id:
                user = User.query.get(user_id)
                user.password = new_password
                db.session.commit()
                session.pop('reset_user_id', None)
                return redirect(url_for('login'))
            else:
                flash('Session expired, please try again')
        else:
            flash('Passwords do not match')
    return render_template('reset_p.html')

@app.route('/form')
def form():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template('form.html')



# Route for predicting loan approval
@app.route('/predict', methods=['POST'])
def predict():
    if 'user_id' not in session:
        return redirect(url_for('login'))  # Redirect if user not logged in

    if request.method == 'POST':
        # Get form data
        gender = request.form['gender']
        married = request.form['married']
        dependents = request.form['dependents']
        education = request.form['education']
        self_employed = request.form['self_employed']
        applicant_income = int(request.form['applicant_income'])
        coapplicant_income = float(request.form['coapplicant_income'])
        loan_amount = float(request.form['loan_amount'])
        loan_amount_term = float(request.form['loan_amount_term'])
        credit_history = float(request.form['credit_history'])
        property_area = request.form['property_area']

        # Log the input data
        logging.debug(f"Input data: {request.form}")

        # Store user data in database
        new_loan_app = LoanApp(
            user_id=session['user_id'],
            gender=gender,
            married=married,
            dependents=dependents,
            education=education,
            self_employed=self_employed,
            applicant_income=applicant_income,
            coapplicant_income=coapplicant_income,
            loan_amount=loan_amount,
            loan_amount_term=loan_amount_term,
            credit_history=credit_history,
            property_area=property_area,
            predicted_loan_status=''  # Temporary placeholder
        )
        db.session.add(new_loan_app)
        db.session.commit()

        # Process user input for prediction
        input_data = {
            'Gender': [gender],
            'Married': [married],
            'Dependents': [dependents],
            'Education': [education],
            'Self_Employed': [self_employed],
            'ApplicantIncome': [applicant_income],
            'CoapplicantIncome': [coapplicant_income],
            'LoanAmount': [loan_amount],
            'Loan_Amount_Term': [loan_amount_term],
            'Credit_History': [credit_history],
            'Property_Area': [property_area]
        }
        input_df = pd.DataFrame(input_data)

        # Predict loan status using the trained model
        prediction = model.predict(input_df)[0]
        prediction_result = 'Approved' if prediction == 'Y' else 'Not Approved'


        # Log the prediction result
        logging.debug(f"Prediction result: {prediction_result}")

        # Update loan_status in the database
        new_loan_app.predicted_loan_status = prediction_result
        db.session.commit()

        # Fetch last inserted ID (current application ID)
        current_application_id = new_loan_app.id

        # Render prediction result template with prediction and current application ID
        return render_template('result.html', prediction=prediction_result, application_id=current_application_id)

@app.route('/form_list')
def form_list():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user_id = session['user_id']
    loan_apps = LoanApp.query.filter_by(user_id=user_id).all()
    return render_template('form_list.html', loan_apps=loan_apps)

@app.route('/logout')
def logout():
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)
