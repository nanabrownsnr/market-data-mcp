"""Yahoo Finance adapters with stable JSON contracts."""

import yfinance as yf


def _clean(value):
    if value is None:
        return None
    if hasattr(value, "item"):
        value = value.item()
    if isinstance(value, float) and value != value:
        return None
    return value


def asset_info(ticker: str) -> dict:
    symbol = ticker.upper().strip()
    if not symbol:
        raise ValueError("ticker must not be empty")
    info = yf.Ticker(symbol).info
    if not info:
        raise ValueError(f"No market data found for {symbol}")
    return {
        "ticker": symbol,
        "name": _clean(info.get("longName") or info.get("shortName")),
        "sector": _clean(info.get("sector")),
        "industry": _clean(info.get("industry")),
        "security_type": _clean(info.get("quoteType")),
        "currency": _clean(info.get("currency")),
        "dividend_yield": _clean(info.get("dividendYield")),
        "beta": _clean(info.get("beta")),
        "expense_ratio": _clean(info.get("annualReportExpenseRatio")),
        "current_price": _clean(info.get("currentPrice") or info.get("regularMarketPrice")),
    }


def historical_returns(tickers: list[str], period: str = "1y") -> dict:
    symbols = [ticker.upper().strip() for ticker in tickers if ticker.strip()]
    if len(symbols) > 25:
        raise ValueError("tickers cannot contain more than 25 symbols")
    if not symbols:
        raise ValueError("tickers must contain at least one symbol")
    prices = yf.download(symbols, period=period, auto_adjust=False, progress=False)["Close"]
    if hasattr(prices, "to_frame"):
        prices = prices.to_frame(name=symbols[0])
    prices = prices.dropna(how="all")
    returns = prices.pct_change().dropna(how="all")
    return {
        "tickers": symbols,
        "period": period,
        "start_date": str(prices.index[0].date()) if not prices.empty else None,
        "end_date": str(prices.index[-1].date()) if not prices.empty else None,
        "prices": [
            {
                "date": str(index.date()),
                **{key: _clean(value) for key, value in row.items() if value == value},
            }
            for index, row in prices.iterrows()
        ],
        "daily_returns": [
            {
                "date": str(index.date()),
                **{key: _clean(value) for key, value in row.items() if value == value},
            }
            for index, row in returns.iterrows()
        ],
    }


def etf_holdings(ticker: str) -> dict:
    symbol = ticker.upper().strip()
    data = yf.Ticker(symbol).funds_data
    if data is None:
        raise ValueError(f"No ETF holdings found for {symbol}")
    sectors = data.sector_weightings
    holdings = data.top_holdings
    return {
        "ticker": symbol,
        "sector_distribution": {str(key): _clean(value) for key, value in (sectors or {}).items()},
        "top_holdings": [
            {"ticker": str(index), "weight": _clean(row.get("Holding Percent"))}
            for index, row in holdings.iterrows()
        ]
        if holdings is not None
        else [],
    }
