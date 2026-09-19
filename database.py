"""
Database Models & ORM Schema using SQLAlchemy
"""
import os
import datetime
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, ForeignKey, Text
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
import config

Base = declarative_base()

class Business(Base):
    __tablename__ = 'businesses'

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    owner_name = Column(String(100))
    phone = Column(String(20))
    category = Column(String(50))
    upi_vpa = Column(String(50), nullable=False)
    gstin = Column(String(30))
    address = Column(String(200))
    currency = Column(String(10), default="₹")

class ProductCatalog(Base):
    __tablename__ = 'product_catalog'

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    price = Column(Float, nullable=False)
    category = Column(String(50))
    keywords = Column(String(200)) # Comma separated search keywords

class CustomerLead(Base):
    __tablename__ = 'customer_leads'

    id = Column(Integer, primary_key=True)
    phone = Column(String(20), unique=True, nullable=False)
    name = Column(String(100), default="Valued Customer")
    status = Column(String(30), default="NEW") # NEW, INQUIRING, INVOICED, CONVERTED
    total_spend = Column(Float, default=0.0)
    last_interaction = Column(DateTime, default=datetime.datetime.utcnow)

class ChatMessage(Base):
    __tablename__ = 'chat_messages'

    id = Column(Integer, primary_key=True)
    phone = Column(String(20), nullable=False)
    direction = Column(String(10), nullable=False) # INBOUND or OUTBOUND
    message_text = Column(Text, nullable=False)
    intent = Column(String(50))
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)

class Invoice(Base):
    __tablename__ = 'invoices'

    id = Column(String(30), primary_key=True)
    customer_phone = Column(String(20), nullable=False)
    customer_name = Column(String(100))
    item_summary = Column(Text, nullable=False)
    amount = Column(Float, nullable=False)
    tax_amount = Column(Float, default=0.0)
    total_amount = Column(Float, nullable=False)
    status = Column(String(20), default="PENDING") # PENDING, PAID, CANCELLED
    upi_qr_path = Column(String(200))
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

# Database Connection Setup
engine = create_engine(config.DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    """Initializes tables and seeds default business & product catalog."""
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    # Seed Default Business if not exists
    if not db.query(Business).first():
        biz = Business(
            name=config.DEFAULT_BUSINESS["name"],
            owner_name=config.DEFAULT_BUSINESS["owner_name"],
            phone=config.DEFAULT_BUSINESS["phone"],
            category=config.DEFAULT_BUSINESS["category"],
            upi_vpa=config.DEFAULT_BUSINESS["upi_vpa"],
            gstin=config.DEFAULT_BUSINESS["gstin"],
            address=config.DEFAULT_BUSINESS["address"],
            currency=config.DEFAULT_BUSINESS["currency"]
        )
        db.add(biz)

    # Seed Sample Product Catalog if empty
    if not db.query(ProductCatalog).first():
        samples = [
            ProductCatalog(
                name="Class 10 CBSE Math & Science Masterclass",
                description="Comprehensive 1-year live online course with study material and test series.",
                price=4999.0,
                category="Coaching",
                keywords="class 10, math, science, cbse, board exam"
            ),
            ProductCatalog(
                name="Class 12 Physics & Chemistry Target Batch",
                description="Intensive preparation for Board & Competitive exams with 24/7 doubt support.",
                price=7999.0,
                category="Coaching",
                keywords="class 12, physics, chemistry, neet, jee"
            ),
            ProductCatalog(
                name="Spoken English & Communication Bootcamp",
                description="30-day interactive practical spoken English & confidence building program.",
                price=1999.0,
                category="Skill Development",
                keywords="english, spoken, communication, grammar, confidence"
            )
        ]
        db.add_all(samples)

    db.commit()
    db.close()
