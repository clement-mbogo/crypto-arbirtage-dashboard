import os
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
from datetime import datetime

# Load environment variables
load_dotenv()

# Use SQLite by default
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///arbitrage.db")

engine = create_engine(DATABASE_URL, echo=False)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

# --- Trade Model ---
class Trade(Base):
    __tablename__ = "trades"
    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    symbol = Column(String, nullable=False)
    buy_exchange = Column(String, nullable=False)
    sell_exchange = Column(String, nullable=False)
    buy_price = Column(Float, nullable=False)
    sell_price = Column(Float, nullable=False)
    profit_percent = Column(Float, nullable=False)
    volume = Column(Float, nullable=False)
    trade_type = Column(String, default="real")  # or "paper"

# --- Performance Model ---
class Performance(Base):
    __tablename__ = "performance"
    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    capital = Column(Float, nullable=False)
    profit_percent = Column(Float, nullable=False)
    trade_count = Column(Integer, default=0)

# --- Alert Model ---
class Alert(Base):
    __tablename__ = "alerts"
    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    symbol = Column(String, nullable=False)
    buy_exchange = Column(String, nullable=False)
    sell_exchange = Column(String, nullable=False)
    profit_percent = Column(Float, nullable=False)
    volume = Column(Float, nullable=False)

# --- Init DB ---
def init_db():
    Base.metadata.create_all(bind=engine)
