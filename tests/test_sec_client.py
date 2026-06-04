import pytest

from ingestion.sec_client import SECClient


def test_normalize_cik_valid():
    assert SECClient._normalize_cik("320193") == "0000320193"


def test_normalize_cik_invalid():
    with pytest.raises(ValueError):
        SECClient._normalize_cik("ABC123")


def test_get_json_invalid_response(monkeypatch):
    client = SECClient()

    class FakeResponse:
        def raise_for_status(self):
            pass

        def json(self):
            raise ValueError("invalid json")
        
    
    def fake_get(*args, **kwargs):
        return FakeResponse()
    
    monkeypatch.setattr(client.session, "get", fake_get)

    with pytest.raises(ValueError):
        client.get_json("https://example.com")