from sqlalchemy import Column, Integer, String, Boolean

from app.common.database import Base


class CeroHumanoModel(Base):
    __tablename__ = "cerohumanos"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    is_active = Column(Boolean, default=True)
