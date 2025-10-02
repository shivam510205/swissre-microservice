import logging, os
from dotenv import load_dotenv

load_dotenv(dotenv_path=".env")

TOKEN = os.getenv("TOKEN")
print(TOKEN)
