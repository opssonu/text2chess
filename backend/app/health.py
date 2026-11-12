"""Liveness / readiness probes used by Docker, Nginx, CI smoke tests and monitoring."""

import asyncio

from fastapi import APIRouter, Request, Response, status
from sqlalchemy import text

from app import __version__
from app.config import settings
from app.db import engine

router = APIRouter(tags=["health"])

CHECK_TIMEOUT_S = 2.0


async def _check_db() -> bool:
    try:
        async with asyncio.timeout(CHECK_TIMEOUT_S), engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        return True
    except Exception:
        return False


async def _check_redis(request: Request) -> bool:
    try:
        async with asyncio.timeout(CHECK_TIMEOUT_S):
            return bool(await request.app.state.redis.ping())
    except Exception:
        return False


async def dependency_status(request: Request) -> dict[str, bool]:
    db_ok, redis_ok = await asyncio.gather(_check_db(), _check_redis(request))
    return {"database": db_ok, "redis": redis_ok}


@router.get("/health")
async def health() -> dict[str, str]:
    """Liveness: the process is up. Never touches dependencies."""
    return {"status": "ok"}


@router.get("/ready")
async def ready(request: Request, response: Response) -> dict:
    """Readiness: all dependencies reachable. Returns 503 otherwise."""
    checks = await dependency_status(request)
    healthy = all(checks.values())
    if not healthy:
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    return {"status": "ok" if healthy else "degraded", "checks": checks}


@router.get("/api/v1/status")
async def api_status(request: Request) -> dict:
    """Public status info shown in the frontend footer."""
    return {
        "version": __version__,
        "env": settings.env,
        "checks": await dependency_status(request),
    }
