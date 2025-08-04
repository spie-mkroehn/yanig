from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from api.crmdbschema import CrmDBSchema
from typing import Any, Dict


class CrmDBManager:
    def __init__(self):
        self._engine = create_engine("sqlite:///crm.db")
        self._Session = sessionmaker(bind=self._engine)

    def get_session(self) -> Session:
        return self._Session()

    def close_session(self, session: Session) -> None:
        session.close()

    def create_all(self) -> None:
        CrmDBSchema._base.metadata.create_all(self._engine)

    def drop_all(self) -> None:
        CrmDBSchema._base.metadata.drop_all(self._engine)

    def create_character(self, data: Dict[str, Any]) -> CrmDBSchema.Entry:
        session = self.get_session()
        try:
            character = CrmDBSchema.Entry(
                company=data["company"],
                name=data["name"],
                occasion=data["occasion"],
                date=data["date"],
                content=data["content"],
                desc=data["desc"]
            )
            session.add(character)
            session.commit()
            # Refresh the object to make sure all data is loaded
            session.refresh(character)
            return character
        finally:
            self.close_session(session)
