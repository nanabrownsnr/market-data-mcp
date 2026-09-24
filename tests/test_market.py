from unittest.mock import patch

from app.market import asset_info


def test_asset_info_normalizes_yahoo_fields():
    fake = type("Ticker", (), {"info": {"longName": "Example Corp", "sector": "Technology", "beta": 1.1}})()
    with patch("app.market.yf.Ticker", return_value=fake):
        result = asset_info(" exm ")
    assert result["ticker"] == "EXM"
    assert result["name"] == "Example Corp"
    assert result["beta"] == 1.1
