
from fastapi import FastAPI, Depends, Request, HTTPException
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import declarative_base, sessionmaker, Session


# ==========================================
# DATABASE CONFIGURATION
# ==========================================

DATABASE_URL = "sqlite:///./appreciation.db"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base = declarative_base()


# ==========================================
# DATABASE MODEL
# ==========================================

class Appreciation(Base):
    __tablename__ = "appreciations"

    id = Column(Integer, primary_key=True, index=True)
    ip_address = Column(
        String,
        unique=True,
        nullable=False,
        index=True
    )


# Create database tables
Base.metadata.create_all(bind=engine)


# ==========================================
# PYDANTIC RESPONSE MODELS
# ==========================================

class HomeResponse(BaseModel):
    message: str


class AppreciationResponse(BaseModel):
    message: str
    id: int


class AppreciationCountResponse(BaseModel):
    count: int


# ==========================================
# FASTAPI APP
# ==========================================

app = FastAPI(
    title="Appreciation API",
    description="A simple API that allows visitors to appreciate a website once.",
    version="1.0.0"
)


# ==========================================
# DATABASE DEPENDENCY
# ==========================================

def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()


# ==========================================
# HOME
# ==========================================

@app.get(
    "/",
    response_model=HomeResponse
)
def home():
    return {
        "message": "Appreciation API is running"
    }


# ==========================================
# ADD APPRECIATION
# ==========================================

@app.post(
    "/appreciate",
    response_model=AppreciationResponse,
    status_code=201,
    responses={
        409: {
            "description": "This IP address has already appreciated the website."
        }
    }
)
def appreciate(
    request: Request,
    db: Session = Depends(get_db)
):

    ip_address = request.client.host

    existing_appreciation = (
        db.query(Appreciation)
        .filter(Appreciation.ip_address == ip_address)
        .first()
    )

    if existing_appreciation:
        raise HTTPException(
            status_code=409,
            detail="You have already appreciated this website."
        )

    appreciation = Appreciation(
        ip_address=ip_address
    )

    db.add(appreciation)
    db.commit()
    db.refresh(appreciation)

    return {
        "message": "Thank you for the appreciation!",
        "id": appreciation.id
    }


# ==========================================
# GET APPRECIATION COUNT
# ==========================================

@app.get(
    "/appreciations",
    response_model=AppreciationCountResponse
)
def get_appreciations(
    db: Session = Depends(get_db)
):

    count = db.query(Appreciation).count()

    return {
        "count": count
    }

