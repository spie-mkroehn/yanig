from sqlalchemy import create_engine, Engine, func
from sqlalchemy.orm import sessionmaker, Session
from api.journeydbschema import JourneyDBSchema
from typing import Any, Dict


class JourneyDBManager:
    def __init__(self):
        self._engine = create_engine("sqlite:///journey.db")
        self._Session = sessionmaker(bind=self._engine)

    def get_session(self) -> Session:
        return self._Session()

    def close_session(self, session: Session) -> None:
        session.close()

    def create_all(self) -> None:
        JourneyDBSchema._base.metadata.create_all(self._engine)

    def drop_all(self) -> None:
        JourneyDBSchema._base.metadata.drop_all(self._engine)

    def create_character(self, data: Dict[str, Any]) -> JourneyDBSchema.Character:
        session = self.get_session()
        try:
            character = JourneyDBSchema.Character(
                name=data["name"],
                desc=data["desc"],
                xp=0,
                hp=10,
                str=10,
                int=10,
                dex=10
            )
            session.add(character)
            session.commit()
            # Refresh the object to make sure all data is loaded
            session.refresh(character)
            return character
        finally:
            self.close_session(session)
    
    def create_quest(self, data: Dict[str, Any]) -> JourneyDBSchema.Quests:
        session = self.get_session()
        try:
            quest = JourneyDBSchema.Quests(
                question=data["question"],
                answers=data["answers"],
                correct_answer=data["correct_answer"]
            )
            session.add(quest)
            session.commit()
            session.refresh(quest)
            return quest
        finally:
            self.close_session(session)
    
    def get_character(self, character_name: str) -> JourneyDBSchema.Character:
        session = self.get_session()
        try:
            character = session.query(JourneyDBSchema.Character).filter_by(name=character_name).first()
            if character:
                session.refresh(character)
            return character
        finally:
            self.close_session(session)

    def get_random_quest(self) -> JourneyDBSchema.Quests:
        session = self.get_session()
        try:
            # Get total count of quests first
            total_quests = session.query(JourneyDBSchema.Quests).count()
            if total_quests == 0:
                return None
            
            # Get a truly random quest using SQLAlchemy's random function
            quest = session.query(JourneyDBSchema.Quests).order_by(func.random()).first()
            if quest:
                session.refresh(quest)
            return quest
        finally:
            self.close_session(session)

    def modify_character(self, character_name: str, data: Dict[str, Any]) -> JourneyDBSchema.Character:
        session = self.get_session()
        try:
            character = session.query(JourneyDBSchema.Character).filter_by(name=character_name).first()
            if character:
                for key, value in data.items():
                    setattr(character, key, value)
                session.commit()
                session.refresh(character)
            return character
        finally:
            self.close_session(session)
    