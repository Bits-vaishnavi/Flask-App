"""
test_app.py — Pytest suite for ACEest Fitness & Gym API
Run with: pytest test_app.py -v
"""

import pytest
import json
import sys
import os

# Make sure app.py is importable from the same directory
sys.path.insert(0, os.path.dirname(__file__))

import app as app_module
from app import app


# ============================================================
# FIXTURES
# ============================================================

@pytest.fixture
def client(tmp_path, monkeypatch):
    """
    Creates a fresh isolated test client for every test.
    - Uses a temp DB so tests never touch the real aceest_fitness.db
    - app.testing=True turns off Flask error catching so real errors surface
    """
    test_db = str(tmp_path / "test_aceest.db")
    monkeypatch.setattr(app_module, "DB_NAME", test_db)

    app.config["TESTING"] = True
    with app.test_client() as c:
        with app.app_context():
            app_module.init_db()
        yield c


def add_client_helper(client, name="Arjun", **kwargs):
    """Shortcut to POST a client and return the response."""
    payload = {"name": name, "age": 25, "weight": 75.0,
               "program": "Fat Loss", "membership_status": "Active"}
    payload.update(kwargs)
    return client.post("/clients", json=payload)


# ============================================================
# HEALTH CHECK
# ============================================================

class TestHealthCheck:
    def test_health_returns_200(self, client):
        r = client.get("/")
        assert r.status_code == 200

    def test_health_returns_correct_fields(self, client):
        r = client.get("/")
        body = json.loads(r.data)
        assert body["status"] == "running"
        assert body["app"] == "ACEest Fitness and Gym API V2"
        assert "version" in body


# ============================================================
# PROGRAMS
# ============================================================

class TestPrograms:
    def test_get_all_programs_200(self, client):
        r = client.get("/programs")
        assert r.status_code == 200

    def test_get_all_programs_has_three_entries(self, client):
        body = json.loads(client.get("/programs").data)
        assert len(body["programs"]) == 3

    def test_get_all_programs_contains_expected_keys(self, client):
        body = json.loads(client.get("/programs").data)
        assert "Fat Loss" in body["programs"]
        assert "Muscle Gain" in body["programs"]
        assert "Beginner" in body["programs"]

    def test_each_program_has_workout_diet_calories(self, client):
        body = json.loads(client.get("/programs").data)
        for prog in body["programs"].values():
            assert "workout" in prog
            assert "diet" in prog
            assert "target_calories" in prog

    def test_get_single_program_fat_loss(self, client):
        r = client.get("/programs/Fat Loss")
        assert r.status_code == 200
        body = json.loads(r.data)
        assert body["program"] == "Fat Loss"
        assert "details" in body

    def test_get_single_program_muscle_gain(self, client):
        r = client.get("/programs/Muscle Gain")
        assert r.status_code == 200

    def test_get_single_program_beginner(self, client):
        r = client.get("/programs/Beginner")
        assert r.status_code == 200

    def test_get_nonexistent_program_returns_404(self, client):
        r = client.get("/programs/Yoga")
        assert r.status_code == 404

    def test_get_nonexistent_program_error_message(self, client):
        r = client.get("/programs/Yoga")
        body = json.loads(r.data)
        assert "error" in body


# ============================================================
# CLIENTS — CREATE
# ============================================================

class TestClientsCreate:
    def test_add_client_returns_201(self, client):
        r = add_client_helper(client)
        assert r.status_code == 201

    def test_add_client_success_message(self, client):
        r = add_client_helper(client)
        body = json.loads(r.data)
        assert "added successfully" in body["message"]

    def test_add_client_without_name_returns_400(self, client):
        r = client.post("/clients", json={"age": 25})
        assert r.status_code == 400

    def test_add_client_with_empty_body_returns_400(self, client):
        r = client.post("/clients", json={})
        assert r.status_code == 400

    def test_add_duplicate_client_returns_409(self, client):
        add_client_helper(client, name="Arjun")
        r = add_client_helper(client, name="Arjun")
        assert r.status_code == 409

    def test_add_duplicate_client_error_message(self, client):
        add_client_helper(client, name="Arjun")
        r = add_client_helper(client, name="Arjun")
        body = json.loads(r.data)
        assert "already exists" in body["error"]

    def test_add_client_stores_all_fields(self, client):
        add_client_helper(client, name="Priya", age=30, weight=60.0,
                          height=165.0, program="Muscle Gain")
        r = client.get("/clients/Priya")
        body = json.loads(r.data)["client"]
        assert body["age"] == 30
        assert body["weight"] == 60.0
        assert body["program"] == "Muscle Gain"

    def test_add_client_default_membership_active(self, client):
        client.post("/clients", json={"name": "Ravi"})
        body = json.loads(client.get("/clients/Ravi").data)["client"]
        assert body["membership_status"] == "Active"


# ============================================================
# CLIENTS — READ
# ============================================================

class TestClientsRead:
    def test_get_all_clients_empty_list(self, client):
        r = client.get("/clients")
        body = json.loads(r.data)
        assert r.status_code == 200
        assert body["clients"] == []

    def test_get_all_clients_after_adding(self, client):
        add_client_helper(client, name="Arjun")
        add_client_helper(client, name="Priya")
        body = json.loads(client.get("/clients").data)
        assert len(body["clients"]) == 2

    def test_get_all_clients_ordered_by_name(self, client):
        add_client_helper(client, name="Zara")
        add_client_helper(client, name="Arjun")
        body = json.loads(client.get("/clients").data)
        names = [c["name"] for c in body["clients"]]
        assert names == sorted(names)

    def test_get_single_client_200(self, client):
        add_client_helper(client, name="Arjun")
        r = client.get("/clients/Arjun")
        assert r.status_code == 200

    def test_get_single_client_correct_data(self, client):
        add_client_helper(client, name="Arjun")
        body = json.loads(client.get("/clients/Arjun").data)
        assert body["client"]["name"] == "Arjun"

    def test_get_nonexistent_client_returns_404(self, client):
        r = client.get("/clients/Ghost")
        assert r.status_code == 404

    def test_get_nonexistent_client_error_message(self, client):
        r = client.get("/clients/Ghost")
        body = json.loads(r.data)
        assert "error" in body


# ============================================================
# CLIENTS — UPDATE
# ============================================================

class TestClientsUpdate:
    def test_update_client_returns_200(self, client):
        add_client_helper(client, name="Arjun")
        r = client.put("/clients/Arjun", json={"weight": 70.0})
        assert r.status_code == 200

    def test_update_client_persists_change(self, client):
        add_client_helper(client, name="Arjun", weight=75.0)
        client.put("/clients/Arjun", json={"weight": 70.0})
        body = json.loads(client.get("/clients/Arjun").data)["client"]
        assert body["weight"] == 70.0

    def test_update_client_program(self, client):
        add_client_helper(client, name="Arjun", program="Fat Loss")
        client.put("/clients/Arjun", json={"program": "Muscle Gain"})
        body = json.loads(client.get("/clients/Arjun").data)["client"]
        assert body["program"] == "Muscle Gain"

    def test_update_nonexistent_client_returns_404(self, client):
        r = client.put("/clients/Ghost", json={"weight": 70.0})
        assert r.status_code == 404

    def test_update_with_no_body_returns_400(self, client):
        add_client_helper(client, name="Arjun")
        r = client.put("/clients/Arjun", json=None,
                       content_type="application/json")
        assert r.status_code == 400

    def test_update_ignores_disallowed_fields(self, client):
        add_client_helper(client, name="Arjun")
        r = client.put("/clients/Arjun", json={"id": 999, "name": "Hacker"})
        # Should still succeed (200) but not crash
        assert r.status_code == 200


# ============================================================
# CLIENTS — DELETE
# ============================================================

class TestClientsDelete:
    def test_delete_client_returns_200(self, client):
        add_client_helper(client, name="Arjun")
        r = client.delete("/clients/Arjun")
        assert r.status_code == 200

    def test_delete_client_removes_from_db(self, client):
        add_client_helper(client, name="Arjun")
        client.delete("/clients/Arjun")
        r = client.get("/clients/Arjun")
        assert r.status_code == 404

    def test_delete_nonexistent_client_returns_404(self, client):
        r = client.delete("/clients/Ghost")
        assert r.status_code == 404


# ============================================================
# CLIENTS — GENERATE PROGRAM
# ============================================================

class TestGenerateProgram:
    def test_generate_program_returns_200(self, client):
        add_client_helper(client, name="Arjun")
        r = client.post("/clients/Arjun/generate-program")
        assert r.status_code == 200

    def test_generate_program_response_has_expected_keys(self, client):
        add_client_helper(client, name="Arjun")
        body = json.loads(client.post("/clients/Arjun/generate-program").data)
        assert "program_type" in body
        assert "program" in body
        assert "message" in body

    def test_generate_program_type_is_valid(self, client):
        add_client_helper(client, name="Arjun")
        body = json.loads(client.post("/clients/Arjun/generate-program").data)
        assert body["program_type"] in ["Fat Loss", "Muscle Gain", "Beginner"]

    def test_generate_program_updates_client_record(self, client):
        add_client_helper(client, name="Arjun")
        gen_body = json.loads(client.post("/clients/Arjun/generate-program").data)
        client_body = json.loads(client.get("/clients/Arjun").data)["client"]
        assert client_body["program"] == gen_body["program"]

    def test_generate_program_for_nonexistent_client_returns_404(self, client):
        r = client.post("/clients/Ghost/generate-program")
        assert r.status_code == 404


# ============================================================
# CLIENTS — MEMBERSHIP
# ============================================================

class TestMembership:
    def test_check_membership_returns_200(self, client):
        add_client_helper(client, name="Arjun")
        r = client.get("/clients/Arjun/membership")
        assert r.status_code == 200

    def test_check_membership_has_status_field(self, client):
        add_client_helper(client, name="Arjun")
        body = json.loads(client.get("/clients/Arjun/membership").data)
        assert "membership_status" in body
        assert body["membership_status"] == "Active"

    def test_check_membership_has_end_field(self, client):
        add_client_helper(client, name="Arjun", membership_end="2025-12-31")
        body = json.loads(client.get("/clients/Arjun/membership").data)
        assert body["membership_end"] == "2025-12-31"

    def test_check_membership_nonexistent_client_returns_404(self, client):
        r = client.get("/clients/Ghost/membership")
        assert r.status_code == 404


# ============================================================
# PROGRESS
# ============================================================

class TestProgress:
    def test_get_progress_empty(self, client):
        r = client.get("/progress/Arjun")
        assert r.status_code == 200
        body = json.loads(r.data)
        assert body["progress"] == []

    def test_add_progress_returns_201(self, client):
        r = client.post("/progress/Arjun", json={"week": "Week 1", "adherence": 85})
        assert r.status_code == 201

    def test_add_progress_success_message(self, client):
        r = client.post("/progress/Arjun", json={"week": "Week 1", "adherence": 85})
        body = json.loads(r.data)
        assert "logged successfully" in body["message"]

    def test_add_progress_persists_data(self, client):
        client.post("/progress/Arjun", json={"week": "Week 1", "adherence": 85})
        body = json.loads(client.get("/progress/Arjun").data)
        assert len(body["progress"]) == 1
        assert body["progress"][0]["adherence"] == 85
        assert body["progress"][0]["week"] == "Week 1"

    def test_add_multiple_progress_entries(self, client):
        client.post("/progress/Arjun", json={"week": "Week 1", "adherence": 80})
        client.post("/progress/Arjun", json={"week": "Week 2", "adherence": 90})
        body = json.loads(client.get("/progress/Arjun").data)
        assert len(body["progress"]) == 2

    def test_add_progress_missing_week_returns_400(self, client):
        r = client.post("/progress/Arjun", json={"adherence": 80})
        assert r.status_code == 400

    def test_add_progress_missing_adherence_returns_400(self, client):
        r = client.post("/progress/Arjun", json={"week": "Week 1"})
        assert r.status_code == 400

    def test_add_progress_adherence_over_100_returns_400(self, client):
        r = client.post("/progress/Arjun", json={"week": "Week 1", "adherence": 110})
        assert r.status_code == 400

    def test_add_progress_adherence_below_0_returns_400(self, client):
        r = client.post("/progress/Arjun", json={"week": "Week 1", "adherence": -5})
        assert r.status_code == 400

    def test_add_progress_adherence_boundary_0(self, client):
        r = client.post("/progress/Arjun", json={"week": "Week 1", "adherence": 0})
        assert r.status_code == 201

    def test_add_progress_adherence_boundary_100(self, client):
        r = client.post("/progress/Arjun", json={"week": "Week 1", "adherence": 100})
        assert r.status_code == 201


# ============================================================
# WORKOUTS
# ============================================================

class TestWorkouts:
    def test_get_workouts_empty(self, client):
        r = client.get("/workouts/Arjun")
        assert r.status_code == 200
        assert json.loads(r.data)["workouts"] == []

    def test_add_workout_returns_201(self, client):
        r = client.post("/workouts/Arjun", json={"workout_type": "Strength"})
        assert r.status_code == 201

    def test_add_workout_persists_data(self, client):
        client.post("/workouts/Arjun", json={"workout_type": "Cardio", "duration_min": 45})
        body = json.loads(client.get("/workouts/Arjun").data)
        assert len(body["workouts"]) == 1
        assert body["workouts"][0]["workout_type"] == "Cardio"
        assert body["workouts"][0]["duration_min"] == 45

    def test_add_workout_defaults_duration_to_60(self, client):
        client.post("/workouts/Arjun", json={"workout_type": "Strength"})
        body = json.loads(client.get("/workouts/Arjun").data)
        assert body["workouts"][0]["duration_min"] == 60

    def test_add_workout_defaults_date_to_today(self, client):
        from datetime import date
        client.post("/workouts/Arjun", json={"workout_type": "Strength"})
        body = json.loads(client.get("/workouts/Arjun").data)
        assert body["workouts"][0]["date"] == date.today().isoformat()

    def test_add_workout_missing_type_returns_400(self, client):
        r = client.post("/workouts/Arjun", json={"duration_min": 60})
        assert r.status_code == 400

    def test_add_workout_stores_notes(self, client):
        client.post("/workouts/Arjun", json={"workout_type": "Strength", "notes": "PR day"})
        body = json.loads(client.get("/workouts/Arjun").data)
        assert body["workouts"][0]["notes"] == "PR day"

    def test_add_multiple_workouts_ordered_by_date_desc(self, client):
        client.post("/workouts/Arjun", json={"workout_type": "Cardio", "date": "2025-01-01"})
        client.post("/workouts/Arjun", json={"workout_type": "Strength", "date": "2025-06-01"})
        body = json.loads(client.get("/workouts/Arjun").data)
        dates = [w["date"] for w in body["workouts"]]
        assert dates == sorted(dates, reverse=True)


# ============================================================
# METRICS
# ============================================================

class TestMetrics:
    def test_get_metrics_empty(self, client):
        r = client.get("/metrics/Arjun")
        assert r.status_code == 200
        assert json.loads(r.data)["metrics"] == []

    def test_add_metrics_returns_201(self, client):
        r = client.post("/metrics/Arjun", json={"weight": 74.5, "waist": 82.0, "bodyfat": 18.5})
        assert r.status_code == 201

    def test_add_metrics_persists_data(self, client):
        client.post("/metrics/Arjun", json={"weight": 74.5, "waist": 82.0, "bodyfat": 18.5})
        body = json.loads(client.get("/metrics/Arjun").data)
        assert len(body["metrics"]) == 1
        assert body["metrics"][0]["weight"] == 74.5
        assert body["metrics"][0]["waist"] == 82.0
        assert body["metrics"][0]["bodyfat"] == 18.5

    def test_add_metrics_partial_fields_ok(self, client):
        r = client.post("/metrics/Arjun", json={"weight": 74.5})
        assert r.status_code == 201

    def test_add_metrics_no_body_returns_400(self, client):
        r = client.post("/metrics/Arjun",
                        data="", content_type="application/json")
        assert r.status_code == 400

    def test_add_metrics_defaults_date_to_today(self, client):
        from datetime import date
        client.post("/metrics/Arjun", json={"weight": 74.5})
        body = json.loads(client.get("/metrics/Arjun").data)
        assert body["metrics"][0]["date"] == date.today().isoformat()

    def test_add_multiple_metrics_entries(self, client):
        client.post("/metrics/Arjun", json={"weight": 75.0, "date": "2025-01-01"})
        client.post("/metrics/Arjun", json={"weight": 73.0, "date": "2025-06-01"})
        body = json.loads(client.get("/metrics/Arjun").data)
        assert len(body["metrics"]) == 2
