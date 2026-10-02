from app.main import AnalyzeRequest, analyze, health, home


def test_health() -> None:
    assert health()["status"] == "ok"


def test_analyze() -> None:
    response = analyze(AnalyzeRequest(text="Ứng dụng chạy nhanh và dễ dùng"))
    assert response.label_code in {"tich_cuc", "trung_tinh", "tieu_cuc"}


def test_home() -> None:
    html = home()
    assert "Vietnamese Sentiment Mini AI" in html
    assert "/api/analyze" in html