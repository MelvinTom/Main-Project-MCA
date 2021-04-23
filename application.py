from datetime import datetime
from flask import Flask, request, render_template,redirect,url_for,session
from flask_cors import CORS,cross_origin
import pickle
import pandas as pd
import numpy as np
from flask_sqlalchemy import SQLAlchemy
app=Flask(__name__)
cors=CORS(app)
model=pickle.load(open('LinearRegressionModel.pkl','rb'))
car=pd.read_csv('Cleaned_Car_data.csv')
app.secret_key = "secreetkey"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
db = SQLAlchemy(app)
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    Email = db.Column(db.String(80), unique=True, nullable=False)
    Name = db.Column(db.String(50),  nullable=False)
    Mobile = db.Column(db.String(20),  nullable=False)
    Password = db.Column(db.String(50),  nullable=False)
  
    
    def __init__(self,Email,Name,Mobile,Pass):
        self.Email = Email
        self.Name=Name
        self.Mobile=Mobile
        self.Password=Pass

    def __repr__(self):
        return f"User('{self.Email}', '{self.Name}')"
db.create_all()        


@app.route("/")
@cross_origin()
def default():
    return redirect(url_for("login"))


@app.route("/Login", methods=["GET","POST"])
@cross_origin()
def login():
    if request.method == "POST":
        email = request.form['email']
        password = request.form['password']
        loguser = User.query.filter_by(Email=email,Password=password).first()
        if loguser:
            session["loggedIn"]= True
            return redirect(url_for("home"))
        else:
            return redirect(url_for('login'))
    else:
        if 'loggedIn' in session:
            return redirect(url_for("home"))
        else:    
            return render_template('Login.html')

@app.route("/logout")
@cross_origin()
def logout():
    session.pop("loggedIn",None)
    return redirect(url_for("login"))
    


@app.route("/Registration", methods = ["GET", "POST"])
@cross_origin()
def register():
    if request.method == "POST":
        name = request.form['name']
        email = request.form['email']
        mobile = request.form['mobile']
        password = request.form['Password']
        user = User(Email=email,Name=name,Mobile=mobile,Pass=password)
        db.session.add(user)
        db.session.commit()
        return redirect(url_for("login"))
    else:
        return render_template("Registration.html")



@app.route("/home")
@cross_origin()
def home():
    if 'loggedIn' in session:
        return render_template("home.html")
    else:
        return redirect(url_for('login'))

@app.route('/',methods=['GET','POST'])
def index():
    companies=sorted(car['company'].unique())
    car_models=sorted(car['name'].unique())
    year=sorted(car['year'].unique(),reverse=True)
    fuel_type=car['fuel_type'].unique()

    companies.insert(0,'Select Company')
    return render_template('home.html',companies=companies, car_models=car_models, years=year,fuel_types=fuel_type)


@app.route('/predict',methods=['POST'])
@cross_origin()
def predict():

    company=request.form.get('company')

    car_model=request.form.get('car_models')
    year=request.form.get('year')
    fuel_type=request.form.get('fuel_type')
    driven=request.form.get('kilo_driven')

    prediction=model.predict(pd.DataFrame(columns=['name', 'company', 'year', 'kms_driven', 'fuel_type'],data=np.array([car_model,company,year,driven,fuel_type]).reshape(1, 5)))
    print(prediction)

    return str(np.round(prediction[0],2))
    
 




if __name__ == "__main__":
    db.create_all()
    app.run(debug=True)
