from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
import datetime

Base = declarative_base()

class Document(Base):
    __tablename__ = 'documents'
    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, nullable=False)
    filetype = Column(String, nullable=False)
    status = Column(String, default='pending')
    content = Column(Text)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

class VideoFrame(Base):
    __tablename__ = 'video_frames'
    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey('documents.id'))
    frame_index = Column(Integer)
    image_data = Column(Text)  # Store as base64 or path to file
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    document = relationship('Document', backref='frames') 