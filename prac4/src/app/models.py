from sqlalchemy import String, Column, Boolean, BigInteger
from sqlalchemy.orm import relationship, Mapped

from core.database import Base


class User(Base):
    __tablename__ = "user"

    id = Column(BigInteger, primary_key=True)
    username = Column(String(50), index=True, unique=True, nullable=False)
    email = Column(String(75), index=True, unique=True, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)
