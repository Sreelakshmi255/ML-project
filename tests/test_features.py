from app import app


def signed_in_client():
    app.config.update(TESTING=True)
    client = app.test_client()
    response = client.post("/login", data={"email": "demo@example.com", "password": "Demo@12345"})
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
    client = signed_in_client()
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


def test_feature_pages_render_for_signed_in_user():
    client = signed_in_client()
    for path in ("/dashboard", "/predict", "/comparison", "/trends"):
        response = client.get(path)
        assert response.status_code == 200


def test_prediction_includes_range_and_indicative_confidence():
    client = signed_in_client()
    response = client.post("/api/predict", json={
        "drug_name": "Metformin", "dosage_mg": 20, "brand_status": "Generic",
        "q1_price": 12.5, "q2_price": 12.8, "q3_price": 13.1, "q4_price": 13.4
    })
    assert response.status_code == 200
    payload = response.get_json()
    assert payload["range"]["low"] < payload["prediction"] < payload["range"]["high"]
    assert 50 <= payload["confidence_pct"] <= 95
    assert client.delete(f"/api/history/{payload['id']}").status_code == 200


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
