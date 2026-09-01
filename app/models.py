from sqlalchemy import Column, Integer, String, Boolean

from app.database import Base


class Appreciation(Base):
    __tablename__ = "appreciations"

    id = Column(Integer, primary_key=True, index=True)

    visitor_id = Column(
        String(36),
        unique=True,
        nullable=False,
        index=True
    )

    appreciated = Column(
        Boolean,
        default=True,
        nullable=False
    )