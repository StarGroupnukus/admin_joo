from typing import ClassVar

from arq import cron
from arq.connections import RedisSettings

from app.core.config import settings

from .functions import (
    sample_background_task,
    send_sms_task,
    shutdown,
    startup,
    create_zip,
)


class WorkerSettings:
    functions: ClassVar[list] = [
        sample_background_task,
        send_sms_task,
        create_zip,
    ]
    # Настройка периодических задач
    cron_jobs = [  # noqa
        # cron(
        #     sample_background_task,
        #     minute=list(range(0, 60)),
        #     hour=list(range(0, 24)),
        #     day=None,
        #     month=None,
        #     run_at_startup=True,
        # ),
    ]
    redis_settings = RedisSettings(
        host=settings.redis_client.HOST,
        port=settings.redis_client.PORT,
    )
    on_startup = startup
    on_shutdown = shutdown
    handle_signals = False
