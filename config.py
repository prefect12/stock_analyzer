import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'hard-to-guess-string'
    BASEDIR = os.path.abspath(os.path.dirname(__file__))
    DATA_CACHE_DIR = os.path.join(BASEDIR, 'data_cache') 