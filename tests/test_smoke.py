def test_project_files_exist():
    from pathlib import Path
    root=Path(__file__).resolve().parents[1]
    assert (root/"app.py").exists()
    assert (root/"templates/base.html").exists()
    assert (root/"static/css/style.css").exists()


def test_health_contract():
    from app import app
    app.config.update(TESTING=True)
    response = app.test_client().get("/api/health")
    assert response.status_code == 200
    assert response.get_json()["status"] == "ok"


def test_prediction_requires_authentication():
    from app import app
    app.config.update(TESTING=True)
    response = app.test_client().post("/api/predict", json={})
    assert response.status_code == 302
    assert "/login" in response.headers["Location"]


def test_invalid_prediction_returns_stable_error():
    from app import app
    app.config.update(TESTING=True)
    client = app.test_client()
    client.post("/admin/login", data={"email":"admin@example.com", "password":"Admin@12345"})
    response = client.post("/api/predict", json={"drug_name":"Metformin", "dosage_mg":"nan", "brand_status":"Generic"})
    assert response.status_code == 400
    body = response.get_json()
    assert body["success"] is False
    assert body["error"]["code"] == "VALIDATION_ERROR"


def test_user_analytics_contracts():
    from app import app
    app.config.update(TESTING=True)
    client = app.test_client()
    client.post("/login", data={"email":"demo@example.com", "password":"Demo@12345"})
    dashboard = client.get("/api/dashboard")
    comparison = client.get("/api/comparison")
    assert dashboard.status_code == 200
    assert comparison.status_code == 200
    assert "monthly_statistics" in dashboard.get_json()["data"]
    assert isinstance(comparison.get_json()["data"], list)


def test_admin_dataset_validation_rejects_missing_columns():
    from io import BytesIO
    from app import app
    app.config.update(TESTING=True)
    client = app.test_client()
    client.post("/admin/login", data={"email":"admin@example.com", "password":"Admin@12345"})
    response = client.post("/api/admin/dataset", data={"dataset": (BytesIO(b"drug_name,price\nMetformin,10\n"), "prices.csv")}, content_type="multipart/form-data")
    assert response.status_code == 400
    assert response.get_json()["error"]["code"] == "DATASET_INVALID"
