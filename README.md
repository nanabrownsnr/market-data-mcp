# Market Data MCP

Market metadata, historical prices, and ETF composition through Yahoo Finance via `yfinance`.

## Tools

- `get_asset_info(ticker)` returns name, sector, security type, dividend yield, beta, expense ratio, currency, and price when available.
- `get_historical_returns(tickers, period="1y")` returns daily prices and decimal daily returns. Periods include `1mo`, `6mo`, `1y`, `5y`, and `max`.
- `get_etf_holdings(ticker)` returns sector distribution and top holdings when Yahoo provides them.

Example calls:

```text
get_asset_info("VTI")
get_historical_returns(["VTI", "BND"], period="5y")
get_etf_holdings("QQQ")
```

Yahoo Finance does not require an API key. Data may be delayed, rate-limited, or unavailable for some securities.

## Run

```bash
uv sync
uv run uvicorn app.main:app --host 0.0.0.0 --port 8000
```

MCP endpoint: `http://localhost:8000/mcp`
Health endpoint: `http://localhost:8000/api/v1/health`

## Docker

```bash
docker build -t market-data-mcp:local .
docker run --rm -p 8001:8000 market-data-mcp:local
```
