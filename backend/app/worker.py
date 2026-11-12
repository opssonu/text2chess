"""Background worker (arq). Later: bot moves, outbound SMS, clock timeouts, inbound SMS queue."""

import logging

from arq.connections import RedisSettings

from app.config import settings

log = logging.getLogger("text2chess.worker")


async def ping(ctx: dict) -> str:
    return "pong"


async def startup(ctx: dict) -> None:
    logging.basicConfig(level=settings.log_level)
    log.info("worker started (env=%s)", settings.env)


class WorkerSettings:
    functions = [ping]
    on_startup = startup
    redis_settings = RedisSettings.from_dsn(settings.redis_url)
