import logging
import os
from logging.handlers import TimedRotatingFileHandler
from datetime import datetime
import pytz
from dotenv import load_dotenv

# Determine the paths to the .env and .secret-env files
dot_env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config', '.env')
load_dotenv(dot_env_path)

class Logger:
    def __init__(self):
        self.logger = None

    def initialize_logger(self):
        try:
            base_path = os.getenv("PROJECT_PATH")

            # Create logger
            self.logger = logging.getLogger(__name__)
            self.logger.setLevel(logging.DEBUG)

            # Create log directory if not exists
            log_dir = os.path.join(base_path, 'logger', datetime.now().strftime('%Y/%m'))
            os.makedirs(log_dir, exist_ok=True)

            # Create log file name based on the day of the month
            day_of_month = datetime.now().day
            log_file = os.path.join(log_dir, f"{day_of_month}.log")

            # Create a timed rotating file handler
            handler = TimedRotatingFileHandler(log_file, when='midnight', backupCount=30)
            handler.setLevel(logging.DEBUG)

            # Create formatter with timezone information
            tz = pytz.timezone('EST')
            formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s',
                                          datefmt='%Y-%m-%d %H:%M:%S')
            formatter.converter = lambda *args: datetime.now(tz).timetuple()

            # formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

            # Set formatter for handler
            handler.setFormatter(formatter)

            # Add handler to logger
            self.logger.addHandler(handler)

        except Exception as e:
            print(f"Error while initializing logger: {e}")

    def get_logger(self):
        if not self.logger:
            raise ValueError("Logger not initialized. Call initialize_logger first.")
        return self.logger


logger = Logger()
