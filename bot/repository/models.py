from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import Integer, String, ForeignKey
from typing import List


class Base(DeclarativeBase):
    pass


class PDAgreement():
    __tablename__ = 'pd_agreement'

    user_id: Mapped[int] = mapped_column(Integer, primary_key=True)


class Participant(Base):
    __tablename__ = 'participants'

    user_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    username: Mapped[str] = mapped_column(String, nullable=True)
    last_name: Mapped[str] = mapped_column(String, nullable=False)
    first_name: Mapped[str] = mapped_column(String, nullable=False)
    middle_name: Mapped[str] = mapped_column(String, nullable=True)
    university: Mapped[str] = mapped_column(String, nullable=False)
    group: Mapped[str] = mapped_column(String, nullable=True)
    passport: Mapped[str] = mapped_column(String, nullable=True)
    team_id: Mapped[int] = mapped_column(Integer, ForeignKey("teams.id"), nullable=True)

    team: Mapped['Team'] = relationship(back_populates='participants')


class Team(Base):
    __tablename__ = 'teams'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String, nullable=False)

    participants: Mapped[List['Participant']] = relationship(back_populates='team')