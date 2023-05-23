import os
from dotenv import load_dotenv

load_dotenv()


SMTP_SERVER_ADDRESS = os.environ["SMTP_SERVER_ADDRESS"]
SENDER_ADDRESS = os.environ["SENDER_ADDRESS"]
SENDER_PASSWORD = os.environ["SENDER_PASSWORD"]
PORT = os.environ["PORT"]
