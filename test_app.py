from ai_service import fallback_analysis


def test_high_intent_scoring():
    result = fallback_analysis("Acil fiyat teklifi almak istiyorum, demo ve CRM entegrasyonu lazım.", "Acme")
    assert result["score"] >= 75
    assert result["priority"] == "high"


def test_low_intent_scoring():
    result = fallback_analysis("Merhaba, genel bilgi almak istiyorum.")
    assert 0 <= result["score"] <= 100
    assert result["priority"] in {"low", "medium", "high"}
