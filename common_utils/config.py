import os
from dotenv import load_dotenv

def load_config():
    load_dotenv()
    config = {k: v for k, v in os.environ.items()}
    return config 