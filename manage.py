#!/usr/bin/env python
import os
import sys
import structlog
import builtins
from dotenv import load_dotenv

from utils.msg_publisher import PubSubMessagePublisher

# Load .env file
dot_env_path = os.path.join(os.path.dirname(__file__), 'config', '.env')
load_dotenv(dot_env_path)

builtins.logger = structlog.get_logger(__name__)

if os.getenv('PROJECT_ID'):
    builtins.msg_publisher = PubSubMessagePublisher(os.getenv('PROJECT_ID'))
else:
    logger.error("Failed to create publisher as project id is missing.")

if __name__ == "__main__":
    logger.info("Initializing application.")
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "webapp.settings")
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)
