from dotenv import load_dotenv
import os

load_dotenv()

app_name = os.getenv("APP_NAME")
chapa_secret_key = os.getenv("CHAPA_SECRET_KEY")
chapa_base_url = os.getenv("CHAPA_BASE_URL")
callback_url = os.getenv("CALLBACK_URL")
