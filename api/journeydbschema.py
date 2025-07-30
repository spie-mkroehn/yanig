from sqlalchemy import Column, Integer, String, Index
from sqlalchemy.ext.declarative import declarative_base, DeclarativeMeta
from pydantic import BaseModel


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

    class Quests(_base):
        __tablename__ = 'quests'
        id = Column(Integer, primary_key=True)
        question = Column(String(500))
        answers = Column(String(200))
        correct_answer = Column(Integer)
