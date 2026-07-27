# frameworks/sqlalchemy_orm/database.py
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.ext.declarative import declarative_base

# Base para los modelos (necesario para SQLAlchemy)
Base = declarative_base()

# Instancia de SQLAlchemy para Flask
db = SQLAlchemy(model_class=Base)