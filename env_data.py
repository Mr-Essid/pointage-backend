from dotenv import load_dotenv
import os

load_dotenv()

# DB INFO
USERNAME_ = os.getenv("USERNAME_")
PASSWORD_ = os.getenv("PASSWORD_")
DBNAME = os.getenv("DBNAME")
HOSTNAME = os.getenv("HOSTNAME_")

# MQTT INFO
USERNAME_BROKER = os.getenv("USERNAME_BROKER")
PASSWORD_BROKER = os.getenv("PASSWORD_BROKER")
BROKER = os.getenv("BROKER")
