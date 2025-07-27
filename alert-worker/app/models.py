from sqlalchemy import Column, Integer, String, Text, TIMESTAMP, func
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class Video(Base):
    __tablename__ = "videos"

    id = Column(Integer, primary_key=True, index=True)
    uid = Column(String, nullable=False)
    video = Column(Text, nullable=False)
    width = Column(Integer)
    height = Column(Integer)
    processed_at = Column(TIMESTAMP, server_default=func.now())