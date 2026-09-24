"""FastMCP market-data service."""

import asyncio
from contextlib import asynccontextmanager, suppress
from logging import getLogger

from fastmcp import FastMCP
from fastmcp.server.middleware import Middleware as MCPMiddleware
from fastmcp.server.middleware import MiddlewareContext
from starlette.middleware import Middleware
from starlette.middleware.cors import CORSMiddleware

from app.config import settings
from app.license import license_watcher
from app.market import asset_info, etf_holdings, historical_returns
from app.twynity import register_routes
from app.usage import save_usage_report


@asynccontextmanager
async def lifespan(server):
    task = asyncio.create_task(license_watcher())
    try:
        yield
    finally:
        task.cancel()
        with suppress(asyncio.CancelledError):
            await task

mcp = FastMCP(settings.APP_TITLE, lifespan=lifespan)


@mcp.tool
def get_asset_info(ticker: str) -> dict:
    """Look up one Yahoo Finance symbol. Example: get_asset_info("VTI"). Returns name, sector, security type, dividend yield, beta, expense ratio, currency, and current price when available."""
    return asset_info(ticker)


@mcp.tool
def get_historical_returns(tickers: list[str], period: str = "1y") -> dict:
    """Download daily prices and decimal returns. Example: get_historical_returns(["VTI", "BND"], period="5y"). Valid periods include 1mo, 6mo, 1y, 5y, and max. Returns dates, prices, and daily_returns."""
    return historical_returns(tickers, period)


@mcp.tool
def get_etf_holdings(ticker: str) -> dict:
    """Look up fund composition. Example: get_etf_holdings("VTI"). Returns sector_distribution and top_holdings; Yahoo may not provide holdings for every fund."""
    return etf_holdings(ticker)


class UsageTrackingMiddleware(MCPMiddleware):
    async def on_call_tool(self, context: MiddlewareContext, call_next):
        try:
            await save_usage_report("TOOL_CALL", context.message.name, None)
        except Exception:
            getLogger(__name__).exception("Usage tracking failed")
        return await call_next(context)

mcp.add_middleware(UsageTrackingMiddleware())
register_routes(mcp)
origins = [origin.strip() for origin in settings.ALLOWED_ORIGINS.split(",") if origin.strip()] or ["*"]

app = mcp.http_app(
    middleware=[Middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_methods=["*"],
        allow_headers=["*"],
        expose_headers=["mcp-session-id"],
    )],
    transport="streamable-http",
    stateless_http=True,
    json_response=True,
)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
