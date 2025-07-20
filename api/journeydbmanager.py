from sqlalchemy import create_engine, Engine, func
from sqlalchemy.orm import sessionmaker, Session
from pydantic import BaseModel
from api.journeydbschema import JourneyDBSchema
from typing import Any, Dict


class JourneyDBManager(BaseModel):
    _engine: Engine = create_engine("sqlite:///journey.db")
    _Session = sessionmaker(bind=_engine)

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
        character = JourneyDBSchema.Character(
            name=data["name"],
            desc=data["desc"],
            xp=data["xp"],
            hp=data["hp"],
            str=data["str"],
            int=data["int"],
            dex=data["dex"]
        )
        session.add(character)
        session.commit()
        return character
    
    def create_item(self, data: Dict[str, Any]) -> JourneyDBSchema.Item:
        session = self.get_session()
        item = JourneyDBSchema.Item(
            name=data["name"],
            desc=data["desc"],
            owner_id=data.get("owner_id"),
            str=data["str"],
            int=data["int"],
            dex=data["dex"]
        )
        session.add(item)
        session.commit()
        return item
    
    def create_diary_entry(self, data: Dict[str, Any]) -> JourneyDBSchema.DairyEntries:
        session = self.get_session()
        diary_entry = JourneyDBSchema.DairyEntries(
            title=data["title"],
            desc=data["desc"],
            keywords=data["keywords"]
        )
        session.add(diary_entry)
        session.commit()
        return diary_entry
    
    def create_quest(self, data: Dict[str, Any]) -> JourneyDBSchema.Quests:
        session = self.get_session()
        quest = JourneyDBSchema.Quests(
            question=data["question"],
            answers=data["answers"],
            correct_answer=data["correct_answer"]
        )
        session.add(quest)
        session.commit()
        return quest
    
    def get_character(self, character_name: str) -> JourneyDBSchema.Character:
        session = self.get_session()
        character = session.query(JourneyDBSchema.Character).filter_by(name=character_name).first()
        return character

    def get_item_by_owner(self, owner_name: str) -> list[JourneyDBSchema.Item]:
        session = self.get_session()
        items = session.query(JourneyDBSchema.Item).filter_by(owner_name=owner_name).all()
        return items

    def get_diary_entries_by_keyword(self, keyword: str) -> list[JourneyDBSchema.DairyEntries]:
        session = self.get_session()
        entries = session.query(JourneyDBSchema.DairyEntries).filter(JourneyDBSchema.DairyEntries.keywords.contains(keyword)).all()
        return entries
    
    def get_latest_diary_entries(self, limit: int = 10) -> list[JourneyDBSchema.DairyEntries]:
        session = self.get_session()
        entries = session.query(JourneyDBSchema.DairyEntries).order_by(JourneyDBSchema.DairyEntries.datetime.desc()).limit(limit).all()
        return entries

    def get_random_quest(self, question: str) -> JourneyDBSchema.Quests:
        session = self.get_session()
        quest = session.query(JourneyDBSchema.Quests).filter_by(question=question).order_by(func.random()).first()
        return quest
