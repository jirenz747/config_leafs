from flask import Flask
from config import Config
import datetime

app = Flask(__name__)
app.permanent_session_lifetime = datetime.timedelta(days=1)
app.config.from_object(Config)

from app import routes

