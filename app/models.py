from sqlalchemy import Column, Integer, String

from app.database import Base


class Appreciation(Base):
    __tablename__ = "appreciations"

    id = Column(Integer, primary_key=True, index=True)

    ip_address = Column(
        String(45),
        unique=True,
        nullable=False,
        index=True
    )