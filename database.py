# database.py

import os
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
from datetime import datetime

# Load environment variables
load_dotenv()

# Default to SQLite if DATABASE_URL is not set
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///arbitrage.db")

engine = create_engine(DATABASE_URL, echo=False)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

# ---- Define your tables below ----

class Trade(Base):
    __tablename__ = "trades"
    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    pair = Column(String, nullable=False)
    action = Column(String, nullable=False)  # "buy" or "sell"
    price = Column(Float, nullable=False)
    quantity = Column(Float, nullable=False)
    profit = Column(Float, default=0.0)

class Performance(Base):
    __tablename__ = "performance"
    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    capital = Column(Float, nullable=False)
    profit = Column(Float, nullable=False)
    trade_count = Column(Integer, default=0)

# ---- Init function to create tables ----

def init_db():
    Base.metadata.create_all(bind=engine)
