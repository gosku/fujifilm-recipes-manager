import django.conf
import pytest
import structlog


def pytest_configure(config):
    settings = django.conf.settings
    settings.CELERY_TASK_ALWAYS_EAGER = True
    settings.CELERY_TASK_EAGER_PROPAGATES = True


@pytest.fixture()
def captured_logs():
    """Capture structlog events emitted during a test."""
    output = []

    def capture_processor(logger, method_name, event_dict):
        output.append(event_dict.copy())
        raise structlog.DropEvent

    old_config = structlog.get_config()
    structlog.configure(
        processors=[
            structlog.stdlib.add_log_level,
            structlog.processors.TimeStamper(fmt="iso"),
            capture_processor,
        ],
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
    )
    yield output
    structlog.configure(**old_config)
