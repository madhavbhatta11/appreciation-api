from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session


from app.database import Base, engine, get_db
from app.models import Appreciation
from app.schemas import (
    HomeResponse,
    AppreciationResponse,
    AppreciationCountResponse,
    AppreciationStatusResponse,
)


# Create database tables
Base.metadata.create_all(bind=engine)


# ==========================================
# FASTAPI APP
# ==========================================

app = FastAPI(
    title="Appreciation API",
    description="A simple API that allows visitors to appreciate a website once.",
    version="1.0.0"
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:5500",
        "http://localhost:5500",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


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
            "description": "This visitor has already appreciated the website."
        }
    }
)
def appreciate(
    visitor_id: str,
    db: Session = Depends(get_db)
):

    existing_appreciation = (
        db.query(Appreciation)
        .filter(Appreciation.visitor_id == visitor_id)
        .first()
    )

    if existing_appreciation:
        raise HTTPException(
            status_code=409,
            detail="You have already appreciated this website."
        )

    appreciation = Appreciation(
        visitor_id=visitor_id,
        appreciated=True
    )

    db.add(appreciation)

    try:
        db.commit()
        db.refresh(appreciation)

    except IntegrityError:
        db.rollback()

        raise HTTPException(
            status_code=409,
            detail="You have already appreciated this website."
        )

    return {
        "message": "Thank you for the appreciation!",
        "id": appreciation.id
    }


# ==========================================
# GET APPRECIATION STATUS
# ==========================================

@app.get(
    "/appreciation/status",
    response_model=AppreciationStatusResponse
)
def appreciation_status(
    visitor_id: str,
    db: Session = Depends(get_db)
):

    appreciation = (
        db.query(Appreciation)
        .filter(Appreciation.visitor_id == visitor_id)
        .first()
    )

    return {
        "appreciated": appreciation is not None
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

    count = (
        db.query(Appreciation)
        .filter(Appreciation.appreciated.is_(True))
        .count()
    )

    return {
        "count": count
    }