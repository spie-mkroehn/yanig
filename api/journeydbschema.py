from sqlalchemy import DateTime, Column, Integer, String, ForeignKey, Index
from sqlalchemy.ext.declarative import declarative_base, DeclarativeMeta
from sqlalchemy.orm import relationship
from pydantic import BaseModel
from datetime import datetime


class JourneyDBSchema(BaseModel):
    _base: DeclarativeMeta = declarative_base()

    class Character(_base):
        __tablename__ = 'characters'
        id = Column(Integer, primary_key=True)
        name = Column(String(50))
        desc = Column(String(200))
        xp = Column(Integer)
        hp = Column(Integer)
        str = Column(Integer)
        int = Column(Integer)
        dex = Column(Integer)

    _character_index: Index = Index('idx_character_name', Character.name)

    class Item(_base):
        __tablename__ = 'items'
        id = Column(Integer, primary_key=True)
        name = Column(String(50))
        desc = Column(String(200))
        owner_id = Column(Integer, ForeignKey('characters.id'), nullable=True)
        owner = relationship('Character', back_populates='items')
        str = Column(Integer)
        int = Column(Integer)
        dex = Column(Integer)

    _items_index: Index = Index('idx_item_owner', Item.owner)

    class DairyEntries(_base):
        __tablename__ = 'diary_entries'
        id = Column(Integer, primary_key=True)
        title = Column(String(50))
        datetime = Column(DateTime, default=datetime.now(datetime.timezone.utc))
        desc = Column(String(500))
        keywords = Column(String(200))

    _diary_index: Index = Index('idx_diary_keywords', DairyEntries.keywords)

    class Quests(_base):
        __tablename__ = 'quests'
        id = Column(Integer, primary_key=True)
        question = Column(String(500))
        answers = Column(String(200))
        correct_answer = Column(Integer)
