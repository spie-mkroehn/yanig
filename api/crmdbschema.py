from sqlalchemy import Column, Integer, String, Index
from sqlalchemy.ext.declarative import declarative_base, DeclarativeMeta


class CrmDBSchema:
    _base: DeclarativeMeta = declarative_base()

    class Entry(_base):
        __tablename__ = 'entries'
        id = Column(Integer, primary_key=True)
        company = Column(String(50))
        name = Column(String(50))
        occasion = Column(String(50))
        date = Column(String(50))
        content = Column(String(500))

    # Indizes
    _company_index: Index = Index('idx_company', Entry.company)
