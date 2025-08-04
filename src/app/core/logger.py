# import logging
# import os
# from logging.handlers import RotatingFileHandler

# from app.core.config import settings

# LOG_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "logs")
# # LOG_DIR = settings.logging_config.LOG_DIR
# if not os.path.exists(LOG_DIR):
#     os.makedirs(LOG_DIR)

# LOG_FILE_PATH = os.path.join(LOG_DIR, "app.log")

# LOGGING_LEVEL = settings.logging_config.LOG_LEVEL
# LOGGING_FORMAT = settings.logging_config.LOG_FORMAT

# logging.basicConfig(
#     level=LOGGING_LEVEL,
#     format=LOGGING_FORMAT,
# )

# file_handler = RotatingFileHandler(
#     LOG_FILE_PATH,
#     maxBytes=10485760,
#     backupCount=5,
# )
# file_handler.setLevel(LOGGING_LEVEL)
# file_handler.setFormatter(logging.Formatter(LOGGING_FORMAT))

# logging.getLogger("").addHandler(file_handler)
