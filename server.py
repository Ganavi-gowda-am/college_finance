from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import func

app = Flask(__name__)
app.secret_key = "secret_key"

# ------------------- DATABASE -------------------
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///college_finance.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class ExpenditureCategory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    budget = db.Column(db.Float, nullable=False)
    expenditures = db.relationship("Finance", backref="category", lazy=True)

class Finance(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    category_id = db.Column(db.Integer, db.ForeignKey("expenditure_category.id"), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    description = db.Column(db.String(200), nullable=True)

# Create tables if they do not exist
with app.app_context():
    db.create_all()
    if ExpenditureCategory.query.count() == 0:
        categories = [
            ("Professor", 72000000),
            ("Associate Professor", 19200000),
            ("Assistant Professor", 10000000),
            ("Guest Faculty", 2400000),
            ("Cleaning Staff", 240000),
            ("Electricity", 1500000),
            ("Lab Maintenance", 400000),
            ("Library", 5000000),
            ("Exam/Markscard", 5000000),
            ("Hostel Maintenance", 5400000),
            ("Workshop/Events", 3000000),
        ]
        for name, budget in categories:
            db.session.add(ExpenditureCategory(name=name, budget=budget))
        db.session.commit()

# ------------------- LOGIN -------------------
@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        role = request.form['role']
        password = request.form.get('password', '')

        # Default passwords
        passwords = {
            "financer": "fin123",
            "principal": "princ123"
        }

        # Check password for financer/principal
        if role in ["financer", "principal"]:
            if password != passwords.get(role):
                flash("Incorrect password!", "error")
                return redirect(url_for('login'))

        # Set session and redirect
        session['username'] = username
        session['role'] = role
        if role == "financer":
            return redirect(url_for('financer_dashboard'))
        elif role == "principal":
            return redirect(url_for('principal_dashboard'))
        else:  # General
            return redirect(url_for('general_dashboard'))

    return render_template("login.html")

# ------------------- FINANCER DASHBOARD -------------------
@app.route('/financer_dashboard', methods=['GET', 'POST'])
def financer_dashboard():
    categories = ExpenditureCategory.query.all()
    if request.method == "POST":
        category_id = int(request.form['category'])
        amount = float(request.form['amount'])
        category = ExpenditureCategory.query.get(category_id)
        if category:
            spent = db.session.query(func.sum(Finance.amount)).filter_by(category_id=category_id).scalar() or 0
            if spent + amount > category.budget:
                flash(f"Budget exceeded for {category.name}! Limit: {category.budget}, Spent: {spent}", "error")
            else:
                db.session.add(Finance(category_id=category_id, amount=amount, description=f"Added {amount}"))
                db.session.commit()
                flash(f"Added {amount} to {category.name} successfully!", "success")
        return redirect(url_for('financer_dashboard'))

    expenditures = []
    for cat in categories:
        spent = db.session.query(func.sum(Finance.amount)).filter_by(category_id=cat.id).scalar() or 0
        expenditures.append({
            "id": cat.id,
            "name": cat.name,
            "budget": cat.budget,
            "spent": spent,
            "remaining": cat.budget - spent,
            "status": "Over Spent" if spent > cat.budget else "OK"
        })

    return render_template("financer_dashboard.html", expenditures=expenditures, categories=categories)

# ------------------- PRINCIPAL DASHBOARD -------------------
# ------------------- PRINCIPAL DASHBOARD -------------------
@app.route('/principal_dashboard')
def principal_dashboard():
    return render_template("principal_dashboard.html")


@app.route('/api/principal/set_fund', methods=['POST'])
def set_fund():
    data = request.get_json()
    total_fund = data.get("totalFund")
    # You can store total_fund in a table or session if needed
    return jsonify({"success": True, "message": f"Total Fund set to {total_fund}"})


@app.route('/api/principal/view', methods=['GET'])
def view_expenditures():
    categories = ExpenditureCategory.query.all()
    exp_list = []
    for cat in categories:
        spent = db.session.query(func.sum(Finance.amount)).filter_by(category_id=cat.id).scalar() or 0
        exp_list.append({
            "category": cat.name,
            "budget": cat.budget,
            "spent": spent,
            "remaining": cat.budget - spent,
            "status": "Over Spent" if spent > cat.budget else "OK"
        })
    return jsonify(exp_list)

# ------------------- GENERAL DASHBOARD -------------------
@app.route('/general_dashboard')
def general_dashboard():
    categories = ExpenditureCategory.query.all()
    expenditures = []
    for cat in categories:
        spent = db.session.query(func.sum(Finance.amount)).filter_by(category_id=cat.id).scalar() or 0
        expenditures.append({
            "name": cat.name,
            "budget": cat.budget,
            "spent": spent,
            "remaining": cat.budget - spent
        })
    return render_template("general_dashboard.html", expenditures=expenditures)

# ------------------- LOGOUT -------------------
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

# ------------------- RUN -------------------
if __name__ == "__main__":
    app.run(debug=True)

