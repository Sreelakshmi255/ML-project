from app import app, db, Prediction, User, HistoricalPrice, ContactMessage


def signed_in_client():
    app.config.update(TESTING=True)
    client = app.test_client()
    response = client.post("/login", data={"email": "demo@example.com", "password": "Demo@12345"})
    assert response.status_code == 302
    return client


def admin_client():
    app.config.update(TESTING=True)
    client = app.test_client()
    response = client.post("/admin/login", data={"email": "admin@example.com", "password": "Admin@12345"})
    assert response.status_code == 302
    return client


def test_drug_search_returns_generic_brand_and_history():
    response = signed_in_client().get("/api/drugs/search?q=met")
    assert response.status_code == 200
    matches = response.get_json()["data"]
    metformin = next(item for item in matches if item["name"] == "Metformin")
    assert metformin["generic"]["records"] > 0
    assert metformin["brand"]["records"] > 0
    assert metformin["historical_records"] > 0


def test_pharmacy_estimates_can_be_sorted():
    client = signed_in_client()
    response = client.get("/api/pharmacies?drug=Metformin&brand_status=Generic&sort=lowest")
    assert response.status_code == 200
    payload = response.get_json()
    prices = [offer["price"] for offer in payload["data"]]
    assert prices == sorted(prices)
    assert payload["data"][0]["difference"] == 0
    assert "not live" in payload["notice"]

    response = client.get("/api/pharmacies?drug=Metformin&brand_status=Generic&sort=highest")
    assert [offer["price"] for offer in response.get_json()["data"]] == sorted(prices, reverse=True)


def test_price_alert_is_user_owned_and_reports_trigger():
    client = admin_client()
    response = client.post("/api/alerts", json={
        "drug_name": "Metformin", "brand_status": "Generic", "threshold_price": 9999
    })
    assert response.status_code == 201
    alert = response.get_json()["data"]
    assert alert["triggered"] is True
    assert alert["current_price"] <= alert["threshold_price"]

    response = client.delete(f"/api/alerts/{alert['id']}")
    assert response.status_code == 200
    assert client.delete(f"/api/alerts/{alert['id']}").status_code == 404


def test_regular_user_can_create_and_delete_own_alert_only():
    client = signed_in_client()
    dashboard = client.get("/dashboard")
    assert dashboard.status_code == 200
    assert b'id="alert-form"' in dashboard.data
    assert b'name="threshold_price"' in dashboard.data

    response = client.post("/api/alerts", json={
        "drug_name": "Metformin", "brand_status": "Generic", "threshold_price": 10.25
    })
    assert response.status_code == 201
    alert_id = response.get_json()["data"]["id"]

    alerts = client.get("/api/alerts").get_json()["data"]
    assert any(alert["id"] == alert_id and alert["threshold_price"] == 10.25 for alert in alerts)

    admin = admin_client()
    assert admin.delete(f"/api/alerts/{alert_id}").status_code == 404
    assert client.delete(f"/api/alerts/{alert_id}").status_code == 200


def test_feature_pages_render_for_signed_in_user():
    client = signed_in_client()
    for path in ("/dashboard", "/history", "/comparison", "/trends", "/profile"):
        response = client.get(path)
        assert response.status_code == 200
    assert client.get("/predict").status_code == 302


def test_profile_shows_account_and_project_contact_details():
    response = signed_in_client().get("/profile")
    assert response.status_code == 200
    assert b"demo@example.com" in response.data
    assert b"Account type" in response.data
    assert b"Member since" in response.data
    assert b"hello@refillpredict.example" in response.data
    assert b"Bengaluru, India" in response.data
    assert b"Monday-Friday" in response.data


def test_prediction_includes_range_and_indicative_confidence():
    client = admin_client()
    response = client.post("/api/predict", json={
        "drug_name": "Metformin", "dosage_mg": 20, "brand_status": "Generic",
        "q1_price": 12.5, "q2_price": 12.8, "q3_price": 13.1, "q4_price": 13.4
    })
    assert response.status_code == 200
    payload = response.get_json()
    assert payload["range"]["low"] < payload["prediction"] < payload["range"]["high"]
    assert 50 <= payload["confidence_pct"] <= 95
    assert client.delete(f"/api/history/{payload['id']}").status_code == 200


def test_users_are_read_only_and_admin_can_review_everyones_history():
    client = signed_in_client()
    prediction_data = {
        "drug_name": "Metformin", "dosage_strength": 20, "brand_status": "Generic",
        "q1_price": 12.5, "q2_price": 12.8, "q3_price": 13.1, "q4_price": 13.4,
        "predicted_cost": 13.0, "low_cost": 11.0, "high_cost": 15.0, "model_name": "test",
    }
    assert client.post("/api/predict", json={
        "drug_name": "Metformin", "dosage_mg": 20, "brand_status": "Generic",
        "q1_price": 12.5, "q2_price": 12.8, "q3_price": 13.1, "q4_price": 13.4,
    }).status_code == 403
    assert client.delete("/api/history/1").status_code == 403
    assert client.patch("/api/profile", json={"name": "Changed Name"}).status_code == 403

    with app.app_context():
        user = User.query.filter_by(email="demo@example.com").first()
        admin = User.query.filter_by(email="admin@example.com").first()
        user_prediction = Prediction(user_id=user.id, **prediction_data)
        admin_prediction = Prediction(user_id=admin.id, **prediction_data)
        db.session.add_all([user_prediction, admin_prediction])
        db.session.commit()
        prediction_ids = [user_prediction.id, admin_prediction.id]

    admin_session = admin_client()
    assert admin_session.get("/admin/history").status_code == 200
    response = admin_session.get("/api/admin/history")
    assert response.status_code == 200
    entries = response.get_json()["data"]
    owners = {entry["user_email"] for entry in entries}
    assert "demo@example.com" in owners
    assert "admin@example.com" in owners
    assert admin_session.get(f"/admin/results/{prediction_ids[0]}").status_code == 200
    assert client.get("/admin/history").status_code == 302

    with app.app_context():
        Prediction.query.filter(Prediction.id.in_(prediction_ids)).delete(synchronize_session=False)
        db.session.commit()


def test_user_and_admin_credentials_are_separate():
    home = app.test_client().get("/")
    assert b"User login" in home.data
    assert b"Admin login" in home.data
    user_client = app.test_client()
    response = user_client.post("/login", data={"email": "admin@example.com", "password": "Admin@12345"})
    assert response.status_code == 200
    assert user_client.get("/dashboard").status_code == 302

    admin_session = app.test_client()
    response = admin_session.post("/admin/login", data={"email": "demo@example.com", "password": "Demo@12345"})
    assert response.status_code == 200
    assert admin_session.get("/admin").status_code == 302


def test_authenticated_account_cannot_switch_until_logout():
    user_client = signed_in_client()
    response = user_client.post("/admin/login", data={
        "email": "admin@example.com", "password": "Admin@12345",
    })
    assert response.status_code == 302
    assert response.location.endswith("/dashboard")
    assert user_client.get("/admin").status_code == 302
    assert user_client.get("/register").status_code == 302

    user_client.get("/logout")
    response = user_client.post("/admin/login", data={
        "email": "admin@example.com", "password": "Admin@12345",
    })
    assert response.status_code == 302
    assert user_client.get("/admin").status_code == 200

    response = user_client.post("/login", data={
        "email": "demo@example.com", "password": "Demo@12345",
    })
    assert response.status_code == 302
    assert response.location.endswith("/admin")
    assert user_client.get("/admin").status_code == 200


def test_contact_form_saves_subject_and_message():
    client = app.test_client()
    response = client.post("/contact", data={
        "name": "Test Contact",
        "email": "contact@example.com",
        "subject": "Test subject",
        "message": "Test message body",
    })
    assert response.status_code == 302

    with app.app_context():
        record = ContactMessage.query.filter_by(name="Test Contact", email="contact@example.com").order_by(ContactMessage.id.desc()).first()
        assert record is not None
        assert record.message == "Subject: Test subject\n\nTest message body"
        db.session.delete(record)
        db.session.commit()


def test_admin_can_add_manual_drug_price_record():
    client = admin_client()
    response = client.post("/api/admin/historical-prices", json={
        "drug_name": "TestDrug",
        "dosage_strength": 50,
        "quarter": "Q1",
        "year": 2026,
        "price": 12.5,
        "brand_status": "Generic"
    })
    assert response.status_code == 201
    payload = response.get_json()
    assert payload["success"] is True
    assert payload["data"]["drug_name"] == "TestDrug"
    assert payload["data"]["brand_status"] == "Generic"

    with app.app_context():
        record = HistoricalPrice.query.filter_by(drug_name="TestDrug", year=2026).first()
        assert record is not None
        db.session.delete(record)
        db.session.commit()


def test_trends_include_period_summary_and_prediction_overlay():
    client = signed_in_client()
    for months, expected_records in (("3", 1), ("6", 2), ("12", 4)):
        response = client.get(f"/api/trends?drug=Metformin&brand_status=Generic&months={months}")
        assert response.status_code == 200
        payload = response.get_json()
        assert len(payload["data"]) == expected_records
        assert payload["summary"]["observations"] == expected_records
        assert payload["summary"]["average"] is not None
    assert payload["summary"]["highest"] >= payload["summary"]["lowest"]
