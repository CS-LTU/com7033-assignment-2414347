from flask import Flask, render_template, request, redirect, session, flash
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
import logging
from datetime import datetime
from pymongo import MongoClient
from bson.objectid import ObjectId
from flask_wtf import FlaskForm, CSRFProtect
from wtforms import StringField, IntegerField, FloatField, SelectField, validators
import csv

logging.basicConfig(
    filename="app_log.txt",
    level=logging.INFO,          # logs info, warnings, errors
    format="%(asctime)s - %(levelname)s - %(message)s",
)

app = Flask(__name__)
app.secret_key = "yoursecretkey"

# -------------------------------
# SQLite Config
# -------------------------------
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///users.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)

# -------------------------------
# Enable CSRF Protection
# -------------------------------
csrf = CSRFProtect(app)
csrf.init_app(app)

# -------------------------------
# User Model (ONLY ONCE)
# -------------------------------
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)

def import_patients_from_csv(csv_file_path):
    """
    Reads a CSV file and inserts all patient records into MongoDB.
    Only run this once to import existing data.
    """
    with open(csv_file_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            # Handle missing BMI or other numeric fields
            try:
                bmi_val = float(row["bmi"]) if row["bmi"] not in ("", "N/A") else None
            except:
                bmi_val = None
            try:
                avg_glucose_val = float(row["avg_glucose_level"]) if row["avg_glucose_level"] not in ("", "N/A") else None
            except:
                avg_glucose_val = None

            patient_data = {
                "id": row["id"],
                "gender": row["gender"].capitalize(),
                "age": int(float(row["age"])),
                "hypertension": int(row["hypertension"]),
                "ever_married": row["ever_married"].capitalize(),
                "work_type": row["work_type"],
                "Residence_type": row["Residence_type"],
                "avg_glucose_level": avg_glucose_val,
                "bmi": bmi_val,
                "smoking_status": row["smoking_status"].capitalize(),
                "stroke": int(row["stroke"]),
                "added_by_user_id": None,          # since this is bulk import
                "added_by_username": "CSV Import"  # indicate source
            }
            try:
                patients_collection.insert_one(patient_data)
                logging.info(f"Imported patient: {patient_data['id']}")
            except Exception as e:
                logging.error(f"Error importing patient {patient_data['id']}: {e}")


class PatientForm(FlaskForm):
    id = StringField("ID", [validators.DataRequired(), validators.Length(max=50)])
    gender = SelectField("Gender", choices=["Male", "Female", "Other"], validators=[validators.DataRequired()])
    age = IntegerField("Age", [validators.DataRequired(), validators.NumberRange(min=0, max=150)])
    hypertension = IntegerField("Hypertension", [validators.DataRequired(), validators.AnyOf([0, 1])])
    ever_married = SelectField("Ever Married", choices=["No", "Yes"], validators=[validators.DataRequired()])
    work_type = SelectField("Work Type", choices=["Children", "Govt_job", "Never_worked", "Private", "Self-employed"], validators=[validators.DataRequired()])
    Residence_type = SelectField("Residence Type", choices=["Rural", "Urban"], validators=[validators.DataRequired()])
    avg_glucose_level = FloatField("Avg Glucose Level", [validators.DataRequired(), validators.NumberRange(min=0)])
    bmi = FloatField("BMI", [validators.DataRequired(), validators.NumberRange(min=0)])
    smoking_status = SelectField("Smoking Status", choices=["Formerly smoked", "Never smoked", "Smokes", "Unknown"], validators=[validators.DataRequired()])
    stroke = IntegerField("Stroke", [validators.DataRequired(), validators.AnyOf([0, 1])])


# -------------------------------
# MongoDB Config
# -------------------------------
client = MongoClient("mongodb://localhost:27017/")
mongo_db = client["hospital_db"]
patients_collection = mongo_db["patients"]

# -------------------------------
# Routes
# -------------------------------
@app.route("/")
def home():
    if "user_id" in session:
        return redirect("/dashboard")
    return redirect("/login")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        try:
            hashed = bcrypt.generate_password_hash(password).decode("utf-8")
            new_user = User(username=username, password_hash=hashed)
            db.session.add(new_user)
            db.session.commit()

            logging.info(f"New user registered: {username}")
            flash(f"You are Registered: {username}")
            return redirect("/login")
        except Exception as e:
            logging.error(f"Error during registration for {username}: {e}")
            flash(f"Error during registration for {username}")
            return "An error occurred during registration."
    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        try:
            user = User.query.filter_by(username=username).first()
            if user and bcrypt.check_password_hash(user.password_hash, password):
                session["user_id"] = user.id
                session["username"] = user.username
                logging.info(f"User logged in: {username}")
                flash(f"User logged in: {username}")
                return redirect("/")
            else:
                logging.warning(f"Failed login attempt: {username}")
                flash(f"Failed login attempt: {username}")
                return redirect("/login")
                # return "Invalid username or password"
        except Exception as e:
            logging.error(f"Error during login for {username}: {e}")
            flash(f"Error during login for {username}")
            return "An error occurred during login."
    return render_template("login.html")

@app.route("/dashboard")
def dashboard():
    if "user_id" in session:
        username = session["username"]
        try:
            patients = list(patients_collection.find())
        except Exception as e:
            logging.error(f"Error fetching patients: {e}")
            flash(f"Error fetching patients")
            patients = []
        logging.info(f"Dashboard accessed by: {username}")
        # flash(f"Dashboard accessed by: {username}")
        return render_template("dashboard.html", username=username, patients=patients)
    else:
        logging.warning("Unauthorized access attempt to dashboard")
        flash("Unauthorized access attempt to dashboard")
        return redirect("/login")

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")

@app.route("/add_patient", methods=["GET", "POST"])
def add_patient():
    if "user_id" not in session:
        return redirect("/login")
    
    form = PatientForm()
    if form.validate_on_submit():
        patient_data = {
            "id": form.id.data,
            "gender": form.gender.data,
            "age": form.age.data,
            "hypertension": form.hypertension.data,
            "ever_married": form.ever_married.data,
            "work_type": form.work_type.data,
            "Residence_type": form.Residence_type.data,
            "avg_glucose_level": form.avg_glucose_level.data,
            "bmi": form.bmi.data,
            "smoking_status": form.smoking_status.data,
            "stroke": form.stroke.data,
            "added_by_user_id": session["user_id"],
            "added_by_username": session["username"]
        }
        try:
            patients_collection.insert_one(patient_data)
            logging.info(f"New patient added: {patient_data['id']} by user {session['username']}")
            flash(f"New patient added: {patient_data['id']} by user {session['username']}")
            return redirect("/dashboard")
        except Exception as e:
            logging.error(f"Error adding patient {patient_data['id']}: {e}")
            flash(f"Error adding patient {patient_data['id']}")
            return "An error occurred while adding the patient."
    
    return render_template("add_patient.html", form=form)

@app.route("/my_patients")
def my_patients():
    if "user_id" not in session:
        return redirect("/login")
    try:
        patients = list(patients_collection.find({"added_by_user_id": session["user_id"]}))
    except Exception as e:
        logging.error(f"Error fetching user's patients: {e}")
        flash(f"Error fetching user's patients")
        patients = []
    return render_template("my_patients.html", patients=patients)

@app.route("/edit_patient/<patient_id>", methods=["GET", "POST"])
def edit_patient(patient_id):
    if "user_id" not in session:
        return redirect("/login")
    patient = patients_collection.find_one({"_id": ObjectId(patient_id)})
    if not patient or patient["added_by_user_id"] != session["user_id"]:
        return "Unauthorized"
    
    if request.method == "POST":
        updated_data = {
            "gender": request.form["gender"],
            "age": int(request.form["age"]),
            "hypertension": int(request.form["hypertension"]),
            "ever_married": request.form["ever_married"],
            "work_type": request.form["work_type"],
            "Residence_type": request.form["Residence_type"],
            "avg_glucose_level": float(request.form["avg_glucose_level"]),
            "bmi": float(request.form["bmi"]),
            "smoking_status": request.form["smoking_status"],
            "stroke": int(request.form["stroke"])
        }
        patients_collection.update_one({"_id": ObjectId(patient_id)}, {"$set": updated_data})
        logging.info(f"Patient {patient_id} updated by user {session['user_id']}")
        flash(f"Patient {patient_id} updated by user {session['user_id']}")
        return redirect("/my_patients")
    
    return render_template("edit_patient.html", patient=patient)

@app.route("/delete_patient/<patient_id>")
def delete_patient(patient_id):
    if "user_id" not in session:
        return redirect("/login")
    patient = patients_collection.find_one({"_id": ObjectId(patient_id)})
    if not patient or patient["added_by_user_id"] != session["user_id"]:
        return "Unauthorized"
    
    patients_collection.delete_one({"_id": ObjectId(patient_id)})
    logging.info(f"Patient {patient_id} deleted by user {session['user_id']}")
    flash(f"Patient {patient_id} deleted by user {session['user_id']}")
    return redirect("/my_patients")

if __name__ == "__main__":
    app.run(debug=True)
