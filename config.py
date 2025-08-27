import os
from dotenv import load_dotenv
from dataclasses import dataclass

load_dotenv()

@dataclass
class Config:
    bot_token: str
    superadmin_id: str

def load_config() -> Config:
    return Config(
        bot_token=os.getenv("BOT_TOKEN"),
        superadmin_id=os.getenv("SUPERADMIN_ID")
    )
