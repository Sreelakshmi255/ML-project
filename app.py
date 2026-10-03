from flask import Flask, abort, render_template, request, redirect, url_for, session, jsonify, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from datetime import datetime
from pathlib import Path
import math
import os

from ml.predictor import Predictor
from services.seed import seed_database
from services.validation import validate_email, validate_prediction_input

BASE = Path(__file__).resolve().parent
app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "dev-change-this-secret")
app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{BASE/'instance'/'safemed.db'}"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["MAX_CONTENT_LENGTH"] = 2 * 1024 * 1024
app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"
db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(180), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), default="user", nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)

class Prediction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    drug_name = db.Column(db.String(120), nullable=False)
    dosage_strength = db.Column(db.Float, nullable=False)
    brand_status = db.Column(db.String(20), nullable=False)
    q1_price = db.Column(db.Float, nullable=False)
    q2_price = db.Column(db.Float, nullable=False)
    q3_price = db.Column(db.Float, nullable=False)
    q4_price = db.Column(db.Float, nullable=False)
    predicted_cost = db.Column(db.Float, nullable=False)
    low_cost = db.Column(db.Float, nullable=False)
    high_cost = db.Column(db.Float, nullable=False)
    model_name = db.Column(db.String(120), nullable=False)
    prediction_date = db.Column(db.DateTime, default=datetime.utcnow)

class HistoricalPrice(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    drug_name = db.Column(db.String(120), nullable=False, index=True)
    dosage_strength = db.Column(db.Float, nullable=False)
    quarter = db.Column(db.String(2), nullable=False)
    year = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Float, nullable=False)
    brand_status = db.Column(db.String(20), nullable=False)

class PriceAlert(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False, index=True)
    drug_name = db.Column(db.String(120), nullable=False)
    brand_status = db.Column(db.String(20), nullable=False)
    threshold_price = db.Column(db.Float, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class ContactMessage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(180), nullable=False)
    message = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

predictor = Predictor(BASE)

def current_user():
    uid = session.get("user_id")
    return db.session.get(User, uid) if uid else None

def active_account_redirect():
    user = current_user()
    if user:
        endpoint = "admin_dashboard" if user.role == "admin" else "dashboard"
        return redirect(url_for(endpoint))
    return None

def login_required(fn):
    @wraps(fn)
    def wrapped(*args, **kwargs):
        if not current_user():
            flash("Please sign in to access your workspace.", "warning")
            return redirect(url_for("login", next=request.path))
        return fn(*args, **kwargs)
    return wrapped

def admin_write_required(fn):
    @wraps(fn)
    def wrapped(*args, **kwargs):
        user = current_user()
        if not user or user.role != "admin":
            return api_error("Your account has read-only access.", "READ_ONLY", 403)
        return fn(*args, **kwargs)
    return wrapped

def admin_required(fn):
    @wraps(fn)
    def wrapped(*args, **kwargs):
        user = current_user()
        if not user or user.role != "admin":
            flash("Administrator access is required.", "danger")
            return redirect(url_for("admin_login"))
        return fn(*args, **kwargs)
    return wrapped


def api_error(message, code="VALIDATION_ERROR", status=400):
    return jsonify({"success": False, "error": {"code": code, "message": message}}), status


def parse_limit(default=25, maximum=100):
    try:
        return max(1, min(int(request.args.get("limit", default)), maximum))
    except (TypeError, ValueError):
        return default

def latest_historical_price(drug_name, brand_status):
    return HistoricalPrice.query.filter_by(drug_name=drug_name, brand_status=brand_status).order_by(
        HistoricalPrice.year.desc(), HistoricalPrice.quarter.desc(), HistoricalPrice.id.desc()
    ).first()

def alert_payload(alert):
    latest = latest_historical_price(alert.drug_name, alert.brand_status)
    current_price = latest.price if latest else None
    return {
        "id": alert.id, "drug_name": alert.drug_name, "brand_status": alert.brand_status,
        "threshold_price": alert.threshold_price, "current_price": current_price,
        "triggered": current_price is not None and current_price <= alert.threshold_price,
        "created_at": alert.created_at.strftime("%Y-%m-%d")
    }

@app.context_processor
def inject_globals():
    return {"current_user": current_user(), "year": datetime.now().year}

@app.route("/")
def home():
    return render_template("public/home.html")

@app.route("/about")
def about():
    return render_template("public/about.html")

@app.route("/features")
def features():
    return render_template("public/features.html")

@app.route("/contact", methods=["GET", "POST"])
def contact():
    if request.method == "POST":
        name = request.form.get("name","").strip()[:120]
        email = request.form.get("email","").strip()[:180]
        subject = request.form.get("subject", "").strip()[:160]
        message = request.form.get("message","").strip()[:2000]
        if not name or not validate_email(email) or not subject or not message:
            flash("Please complete your name, valid email, subject, and message.", "danger")
        else:
            db.session.add(ContactMessage(name=name, email=email, message=f"Subject: {subject}\n\n{message}"))
            db.session.commit()
            flash("Thanks. Your message has been recorded in this demo.", "success")
            return redirect(url_for("contact"))
    return render_template("public/contact.html")

@app.route("/register", methods=["GET","POST"])
def register():
    active_redirect = active_account_redirect()
    if active_redirect:
        return active_redirect
    if request.method == "POST":
        name = request.form.get("name","").strip()[:120]
        email = request.form.get("email","").strip().lower()[:180]
        password = request.form.get("password","")
        confirm = request.form.get("confirm_password","")
        if len(name) < 2 or not validate_email(email) or len(password) < 8 or password != confirm:
            flash("Use a valid name, email, and matching password of at least 8 characters.", "danger")
        elif User.query.filter_by(email=email).first():
            flash("An account with that email already exists.", "warning")
        else:
            user = User(name=name, email=email, password_hash=generate_password_hash(password))
            db.session.add(user); db.session.commit()
            session["user_id"] = user.id
            return redirect(url_for("dashboard"))
    return render_template("auth/register.html")

@app.route("/login", methods=["GET","POST"])
def login():
    active_redirect = active_account_redirect()
    if active_redirect:
        return active_redirect
    if request.method == "POST":
        email = request.form.get("email","").strip().lower()
        password = request.form.get("password","")
        user = User.query.filter_by(email=email, role="user").first()
        if user and check_password_hash(user.password_hash, password):
            session.clear(); session["user_id"] = user.id
            user.last_login = datetime.utcnow(); db.session.commit()
            return redirect(request.args.get("next") or url_for("dashboard"))
        flash("Invalid email or password.", "danger")
    return render_template("auth/login.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("home"))

@app.route("/forgot-password", methods=["GET","POST"])
def forgot_password():
    if request.method == "POST":
        flash("If an account exists, password reset instructions would be sent. Demo mode does not send email.", "info")
    return render_template("auth/forgot.html")

@app.route("/dashboard")
@login_required
def dashboard():
    user = current_user()
    recent = Prediction.query.filter_by(user_id=user.id).order_by(Prediction.prediction_date.desc()).limit(5).all()
    count = Prediction.query.filter_by(user_id=user.id).count()
    avg = db.session.query(db.func.avg(Prediction.predicted_cost)).filter(Prediction.user_id==user.id).scalar() or 0
    latest = recent[0] if recent else None
    trend = predictor.trend_for(latest.q1_price, latest.q2_price, latest.q3_price, latest.q4_price) if latest else {"direction":"stable", "change_pct":0}
    alerts = PriceAlert.query.filter_by(user_id=user.id).order_by(PriceAlert.created_at.desc()).all()
    alert_drugs = [row[0] for row in db.session.query(HistoricalPrice.drug_name).distinct().order_by(HistoricalPrice.drug_name).all()]
    return render_template("dashboard/dashboard.html", recent=recent, count=count, avg=avg, trend=trend,
                           alerts=[alert_payload(alert) for alert in alerts], drug_options={"drugs":alert_drugs})

@app.route("/predict")
@login_required
def predict_page():
    if current_user().role != "admin":
        flash("Your account has read-only access.", "warning")
        return redirect(url_for("dashboard"))
    return render_template("dashboard/predict.html", options=predictor.options())

@app.route("/results/<int:prediction_id>")
@login_required
def results(prediction_id):
    p = Prediction.query.filter_by(id=prediction_id, user_id=current_user().id).first_or_404()
    return render_template("dashboard/results.html", prediction=p)

@app.route("/history")
@login_required
def history():
    return render_template("dashboard/history.html", admin_view=False)

@app.route("/comparison")
@login_required
def comparison():
    return render_template("dashboard/comparison.html")

@app.route("/trends")
@login_required
def trends():
    return render_template("dashboard/trends.html")

@app.route("/profile")
@login_required
def profile():
    return render_template("dashboard/profile.html")

@app.route("/admin/login", methods=["GET","POST"])
def admin_login():
    active_redirect = active_account_redirect()
    if active_redirect:
        return active_redirect
    if request.method == "POST":
        email=request.form.get("email","").strip().lower()
        password=request.form.get("password","")
        user=User.query.filter_by(email=email, role="admin").first()
        if user and check_password_hash(user.password_hash,password):
            session.clear(); session["user_id"]=user.id
            return redirect(url_for("admin_dashboard"))
        flash("Invalid administrator credentials.", "danger")
    return render_template("admin/login.html")

@app.route("/admin")
@admin_required
def admin_dashboard():
    metrics = predictor.metrics()
    return render_template("admin/dashboard.html", metrics=metrics)

@app.route("/admin/history")
@admin_required
def admin_history():
    return render_template("dashboard/history.html", admin_view=True)

@app.route("/admin/results/<int:prediction_id>")
@admin_required
def admin_results(prediction_id):
    prediction = db.session.get(Prediction, prediction_id)
    if not prediction:
        abort(404)
    return render_template("dashboard/results.html", prediction=prediction, admin_view=True)

@app.route("/admin/dataset")
@admin_required
def admin_dataset():
    return render_template("admin/dataset.html")

@app.route("/admin/model")
@admin_required
def admin_model():
    return render_template("admin/model.html", metrics=predictor.metrics())

@app.get("/api/health")
def api_health():
    return jsonify({"status":"ok","service":"refill-price-predictor"})

@app.get("/api/options")
def api_options():
    return jsonify(predictor.options())

@app.post("/api/predict")
@login_required
@admin_write_required
def api_predict():
    payload = request.get_json(silent=True) or request.form.to_dict()
    data, error = validate_prediction_input(payload)
    if error:
        return api_error(error)
    try:
        result = predictor.predict(data)
        p = Prediction(user_id=current_user().id, **data, **result)
        db.session.add(p); db.session.commit()
    except Exception:
        db.session.rollback()
        return api_error("The prediction service is temporarily unavailable.", "PREDICTION_ERROR", 503)
    return jsonify({
        "success": True, "id": p.id, "prediction": p.predicted_cost, "range":{"low":p.low_cost,"high":p.high_cost},
        "confidence_pct": max(50, min(95, round(100 - ((p.high_cost - p.low_cost) / max(p.predicted_cost, 0.01)) * 100))),
        "model":p.model_name, "currency":"USD",
        "trend": predictor.trend_for(data["q1_price"],data["q2_price"],data["q3_price"],data["q4_price"])
    })

@app.get("/api/history")
@login_required
def api_history():
    limit=parse_limit()
    search=request.args.get("search", "").strip()[:120]
    query=Prediction.query.filter_by(user_id=current_user().id)
    if search:
        query=query.filter(Prediction.drug_name.ilike(f"%{search}%"))
    rows=query.order_by(Prediction.prediction_date.desc()).limit(limit).all()
    return jsonify({"success": True, "data": [{
        "id":p.id,"drug_name":p.drug_name,"dosage":p.dosage_strength,"brand_status":p.brand_status,
        "predicted_cost":p.predicted_cost,"date":p.prediction_date.strftime("%Y-%m-%d")
    } for p in rows], "count": len(rows)})

@app.delete("/api/history/<int:prediction_id>")
@login_required
@admin_write_required
def api_delete_history(prediction_id):
    p=Prediction.query.filter_by(id=prediction_id,user_id=current_user().id).first()
    if not p: return api_error("Prediction not found.", "NOT_FOUND", 404)
    db.session.delete(p); db.session.commit()
    return jsonify({"success": True, "ok":True})

@app.get("/api/admin/history")
@admin_required
def api_admin_history():
    search = request.args.get("search", "").strip()[:120]
    query = Prediction.query.join(User, User.id == Prediction.user_id)
    if search:
        pattern = f"%{search}%"
        query = query.filter(db.or_(
            Prediction.drug_name.ilike(pattern),
            User.name.ilike(pattern),
            User.email.ilike(pattern),
        ))
    rows = query.order_by(Prediction.prediction_date.desc()).all()
    return jsonify({"success": True, "data": [{
        "id": prediction.id,
        "user_name": db.session.get(User, prediction.user_id).name,
        "user_email": db.session.get(User, prediction.user_id).email,
        "drug_name": prediction.drug_name,
        "dosage": prediction.dosage_strength,
        "brand_status": prediction.brand_status,
        "predicted_cost": prediction.predicted_cost,
        "date": prediction.prediction_date.strftime("%Y-%m-%d"),
    } for prediction in rows], "count": len(rows)})

@app.get("/api/trends")
@login_required
def api_trends():
    query=HistoricalPrice.query
    drug=request.args.get("drug", "").strip()[:120]
    status=request.args.get("brand_status", "Generic").strip()
    months=request.args.get("months", "12")
    if drug:
        query=query.filter_by(drug_name=drug, brand_status=status)
    rows=query.order_by(HistoricalPrice.year,HistoricalPrice.quarter,HistoricalPrice.id).all()
    data=[{"drug":r.drug_name,"quarter":r.quarter,"year":r.year,"price":r.price,"brand_status":r.brand_status} for r in rows]
    if not drug:
        return jsonify({"success": True, "data": data})
    period_count={"3":1,"6":2,"12":4}.get(months, 4)
    selected=data[-period_count:]
    prices=[row["price"] for row in selected]
    latest_prediction=Prediction.query.filter_by(user_id=current_user().id, drug_name=drug, brand_status=status).order_by(Prediction.prediction_date.desc()).first()
    summary={"average":round(sum(prices)/len(prices),2) if prices else None,
             "lowest":min(prices) if prices else None,"highest":max(prices) if prices else None,
             "change_pct":round((prices[-1]-prices[0])/prices[0]*100,1) if len(prices)>1 and prices[0] else 0,
             "observations":len(prices)}
    predicted={"price":latest_prediction.predicted_cost,"low":latest_prediction.low_cost,"high":latest_prediction.high_cost} if latest_prediction else None
    return jsonify({"success": True, "data": selected, "summary": summary, "prediction": predicted})

@app.get("/api/insights")
@login_required
def api_insights():
    rows=HistoricalPrice.query.all()
    generic=[r.price for r in rows if r.brand_status=="Generic"]
    brand=[r.price for r in rows if r.brand_status=="Brand"]
    return jsonify({"success": True, "data": {
        "records":len(rows),
        "average_generic":round(sum(generic)/len(generic),2) if generic else 0,
        "average_brand":round(sum(brand)/len(brand),2) if brand else 0,
        "model":predictor.metrics()
    }})


@app.get("/api/dashboard")
@login_required
def api_dashboard():
    user_id=current_user().id
    predictions=Prediction.query.filter_by(user_id=user_id).order_by(Prediction.prediction_date.desc()).limit(5).all()
    total=Prediction.query.filter_by(user_id=user_id).count()
    average=db.session.query(db.func.avg(Prediction.predicted_cost)).filter(Prediction.user_id==user_id).scalar() or 0
    latest=predictions[0] if predictions else None
    trend=predictor.trend_for(latest.q1_price, latest.q2_price, latest.q3_price, latest.q4_price) if latest else {"direction":"stable","change_pct":0}
    return jsonify({"success": True, "data": {
        "recent_predictions":[{"id":p.id,"drug_name":p.drug_name,"predicted_cost":p.predicted_cost,"date":p.prediction_date.strftime("%Y-%m-%d")} for p in predictions],
        "monthly_statistics":{"prediction_count":total,"average_predicted_cost":round(float(average),2)},
        "cost_insights":{"currency":"USD","estimate_notice":"Predictions are planning estimates, not pharmacy quotes."},
        "trend_snapshot":trend
    }})


@app.get("/api/comparison")
@login_required
def api_comparison():
    grouped={}
    for row in HistoricalPrice.query.all():
        grouped.setdefault(row.drug_name, {"Generic": [], "Brand": []})[row.brand_status].append(row.price)
    data=[]
    for drug, values in grouped.items():
        generic=sum(values["Generic"])/len(values["Generic"]) if values["Generic"] else None
        brand=sum(values["Brand"])/len(values["Brand"]) if values["Brand"] else None
        data.append({"drug":drug,"generic_average":round(generic,2) if generic is not None else None,"brand_average":round(brand,2) if brand is not None else None,"difference_pct":round((brand-generic)/generic*100,1) if generic and brand else None})
    return jsonify({"success": True, "data": data})

@app.get("/api/drugs/search")
@login_required
def api_drug_search():
    search=request.args.get("q", "").strip()[:120].casefold()
    names=sorted({r.drug_name for r in HistoricalPrice.query.with_entities(HistoricalPrice.drug_name).distinct()})
    if search:
        names=[name for name in names if search in name.casefold()]
    results=[]
    for name in names[:10]:
        rows=HistoricalPrice.query.filter_by(drug_name=name).order_by(HistoricalPrice.year.desc(),HistoricalPrice.quarter.desc()).all()
        status_info={}
        for status in ("Generic", "Brand"):
            matching=[row for row in rows if row.brand_status==status]
            status_info[status]={"records":len(matching),"latest_price":matching[0].price if matching else None,
                                 "history":[{"quarter":row.quarter,"year":row.year,"price":row.price} for row in matching[:4]]}
        results.append({"name":name,"generic":status_info["Generic"],"brand":status_info["Brand"],"historical_records":len(rows)})
    return jsonify({"success":True,"data":results})

@app.get("/api/pharmacies")
@login_required
def api_pharmacies():
    drug=request.args.get("drug", "").strip()[:120]
    status=request.args.get("brand_status", "Generic").strip()
    sort=request.args.get("sort", "lowest")
    if status not in ("Generic", "Brand"):
        return api_error("Choose Generic or Brand pricing.")
    latest=latest_historical_price(drug, status)
    if not drug or not latest:
        return api_error("No historical price records are available for this medicine and type.", "NOT_FOUND", 404)
    pharmacies=[("Community Pharmacy",0.94,True),("HealthPlus",0.98,True),("WellCare",1.0,True),("MediSave",1.04,False),("City Pharmacy",1.08,True)]
    offers=[{"pharmacy":name,"price":round(latest.price*factor,2),"available":available} for name,factor,available in pharmacies]
    offers.sort(key=lambda offer:offer["price"],reverse=sort=="highest")
    lowest=min(offer["price"] for offer in offers)
    for offer in offers:
        offer["difference"] = round(offer["price"]-lowest,2)
    return jsonify({"success":True,"drug":drug,"brand_status":status,"currency":"USD","source_price":latest.price,
                    "notice":"Illustrative estimates based on demonstration history; not live pharmacy prices or availability.","data":offers})

@app.get("/api/alerts")
@login_required
def api_alerts():
    alerts=PriceAlert.query.filter_by(user_id=current_user().id).order_by(PriceAlert.created_at.desc()).all()
    return jsonify({"success":True,"data":[alert_payload(alert) for alert in alerts]})

@app.post("/api/alerts")
@login_required
def api_create_alert():
    payload=request.get_json(silent=True) or request.form.to_dict()
    drug=str(payload.get("drug_name", "")).strip()[:120]
    status=str(payload.get("brand_status", "Generic")).strip()
    try:
        threshold=float(payload.get("threshold_price"))
    except (TypeError, ValueError):
        return api_error("Enter a valid price threshold.")
    if not math.isfinite(threshold) or threshold <= 0:
        return api_error("Price threshold must be greater than zero.")
    if status not in ("Generic", "Brand") or not HistoricalPrice.query.filter_by(drug_name=drug, brand_status=status).first():
        return api_error("Choose a medicine and type with historical price records.")
    alert=PriceAlert(user_id=current_user().id,drug_name=drug,brand_status=status,threshold_price=threshold)
    db.session.add(alert); db.session.commit()
    return jsonify({"success":True,"data":alert_payload(alert)}),201

@app.delete("/api/alerts/<int:alert_id>")
@login_required
def api_delete_alert(alert_id):
    alert=PriceAlert.query.filter_by(id=alert_id,user_id=current_user().id).first()
    if not alert:
        return api_error("Price alert not found.", "NOT_FOUND", 404)
    db.session.delete(alert); db.session.commit()
    return jsonify({"success":True,"ok":True})

@app.post("/api/contact")
def api_contact():
    payload=request.get_json(silent=True) or {}
    name=str(payload.get("name","")).strip()[:120]
    email=str(payload.get("email","")).strip()[:180]
    message=str(payload.get("message","")).strip()[:2000]
    if len(name)<2 or not validate_email(email) or not message:
        return api_error("Invalid contact information.")
    db.session.add(ContactMessage(name=name,email=email,message=message)); db.session.commit()
    return jsonify({"success": True, "ok":True})


@app.patch("/api/profile")
@login_required
@admin_write_required
def api_profile():
    payload=request.get_json(silent=True) or {}
    name=str(payload.get("name", "")).strip()[:120]
    if len(name)<2:
        return api_error("Name must contain at least 2 characters.")
    user=current_user()
    user.name=name
    db.session.commit()
    return jsonify({"success": True, "data":{"name":user.name,"email":user.email,"role":user.role}})


@app.post("/api/admin/historical-prices")
@admin_required
def api_admin_historical_prices():
    payload = request.get_json(silent=True) or request.form.to_dict()
    drug_name = str(payload.get("drug_name", "")).strip()[:120]
    dosage_strength = payload.get("dosage_strength")
    quarter = str(payload.get("quarter", "")).strip().upper()
    year = payload.get("year")
    price = payload.get("price")
    brand_status = str(payload.get("brand_status", "")).strip()

    try:
        dosage = float(dosage_strength)
        price_value = float(price)
        year_value = int(year)
    except (TypeError, ValueError):
        return api_error("Enter valid dosage, year, and price values.")

    if not drug_name:
        return api_error("Drug name is required.")
    if dosage <= 0:
        return api_error("Dosage must be greater than zero.")
    if quarter not in {"Q1", "Q2", "Q3", "Q4"}:
        return api_error("Quarter must be one of Q1, Q2, Q3, or Q4.")
    if year_value < 1900 or year_value > 2100:
        return api_error("Year must be a realistic value.")
    if price_value <= 0:
        return api_error("Price must be greater than zero.")
    if brand_status not in {"Generic", "Brand"}:
        return api_error("Choose Generic or Brand pricing.")

    record = HistoricalPrice(
        drug_name=drug_name,
        dosage_strength=dosage,
        quarter=quarter,
        year=year_value,
        price=price_value,
        brand_status=brand_status,
    )
    db.session.add(record)
    db.session.commit()
    return jsonify({"success": True, "data": {
        "id": record.id,
        "drug_name": record.drug_name,
        "dosage_strength": record.dosage_strength,
        "quarter": record.quarter,
        "year": record.year,
        "price": record.price,
        "brand_status": record.brand_status,
    }}), 201

@app.post("/api/admin/dataset")
@admin_required
def api_dataset_upload():
    upload=request.files.get("dataset")
    if not upload or not upload.filename or not upload.filename.lower().endswith(".csv"):
        return api_error("Upload a CSV file with the required pricing columns.", "DATASET_INVALID")
    try:
        import pandas as pd
        frame=pd.read_csv(upload.stream)
    except Exception:
        return api_error("The uploaded CSV could not be read.", "DATASET_INVALID")
    required={"drug_name","dosage_strength","quarter","year","price","brand_status"}
    missing=sorted(required-set(frame.columns))
    if missing:
        return api_error("Missing required columns: " + ", ".join(missing), "DATASET_INVALID")
    prices=pd.to_numeric(frame["price"], errors="coerce")
    valid=prices.notna() & (prices > 0) & frame["drug_name"].notna()
    return jsonify({"success": True, "data":{"rows":int(len(frame)),"valid_rows":int(valid.sum()),"invalid_rows":int((~valid).sum()),"columns":sorted(frame.columns.tolist())}})

@app.post("/api/admin/model/train")
@admin_required
def api_train():
    metrics=predictor.train()
    return jsonify({"success": True, "data": metrics})

with app.app_context():
    (BASE/"instance").mkdir(exist_ok=True)
    db.create_all()
    seed_database(db, User, HistoricalPrice)
    predictor.ensure_model()

if __name__ == "__main__":
    app.run(debug=True, host="127.0.0.1", port=5000)
