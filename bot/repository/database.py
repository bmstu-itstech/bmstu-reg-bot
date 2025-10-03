import asyncio

from abc import ABC, abstractmethod 
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy import select, delete
from typing import List

import config
from bot.domain.models import ParticipantEntity, TeamEntity
from bot.repository.mappers import participant_orm_to_entity, team_orm_to_entity
from bot.repository.models import Base, Participant, Team, PDAgreement


class DatabaseBase(ABC):
    @abstractmethod
    async def create_participant(self, **kwargs) -> ParticipantEntity:
        pass
    
    @abstractmethod
    async def get_participant_by_id(self, user_id: int) -> ParticipantEntity:
        pass

    @abstractmethod
    async def get_participants(self) -> List[ParticipantEntity]:
        pass

    @abstractmethod
    async def get_participants_by_team_id(self, team_id: int) -> List[ParticipantEntity]:
        pass
    
    @abstractmethod
    async def update_participant(self, participant_id: int, **kwargs):
        pass
    
    @abstractmethod
    async def delete_participant(self, participant_id: int):
        pass

    # --- Team ---
    @abstractmethod
    async def create_team(self, **kwargs) -> TeamEntity:
        pass
    
    @abstractmethod
    async def get_team_by_id(self, id: int) -> TeamEntity:
        pass

    @abstractmethod
    async def get_team_by_name(self, name: str) -> TeamEntity:
        pass

    @abstractmethod
    async def get_teams(self) -> List[TeamEntity]:
        pass
    
    @abstractmethod
    async def update_team(self, team_id: int, **kwargs):
        pass
    
    @abstractmethod
    async def delete_team(self, team_id: int):
        pass

    @abstractmethod
    async def save_agreement(self, user_id: int):
        pass

    @abstractmethod
    async def get_agreement(self, user_id: int) -> PDAgreement:
        pass


class PostgresDatabase(DatabaseBase):
    def __init__(self, uri: str):
        self._db_name = uri
        self._engine = create_async_engine(self._db_name, echo=False)
        self._SessionLocal = async_sessionmaker(bind=self._engine, expire_on_commit=False)

    async def init_db(self):
        async with self._engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        await self._engine.dispose()

    async def create_participant(self, **kwargs) -> ParticipantEntity:
        async with self._SessionLocal() as session:
            participant = Participant(**kwargs)
            session.add(participant)
            await session.commit()
            await session.refresh(participant)
            return participant_orm_to_entity(participant)

    async def get_participant_by_id(self, user_id: int) -> ParticipantEntity:
        async with self._SessionLocal() as session:
            stmt = select(Participant).where(Participant.user_id == user_id)
            result = await session.execute(stmt)
            orm_obj = result.scalars().first()
            return participant_orm_to_entity(orm_obj) if orm_obj else None

    async def get_participants(self) -> List[ParticipantEntity]:
        async with self._SessionLocal() as session:
            stmt = select(Participant)
            result = await session.execute(stmt)
            orm_objs = result.scalars().all()
            return [participant_orm_to_entity(o) for o in orm_objs]

    async def get_participants_by_team_id(self, team_id: int) -> List[ParticipantEntity]:
        async with self._SessionLocal() as session:
            stmt = select(Participant).where(Participant.team_id == team_id)
            result = await session.execute(stmt)
            orm_objs = result.scalars().all()
            return [participant_orm_to_entity(o) for o in orm_objs]
        
    async def update_participant(self, participant_id: int, **kwargs):
        async with self._SessionLocal() as session:
            participant_orm = await session.get(Participant, participant_id)
            if participant_orm is None:
                raise ValueError(f"Team not found (ID: {participant_id})")

            for key, value in kwargs.items():
                if hasattr(participant_orm, key):
                    setattr(participant_orm, key, value)

            await session.commit()
            await session.refresh(participant_orm)
            
    async def delete_participant(self, participant_id: int):
        async with self._SessionLocal() as session:
            stmt = delete(Participant).where(Participant.id == participant_id)
            await session.execute(stmt)
            await session.commit()

    # --- Team ---
    async def create_team(self, **kwargs) -> TeamEntity:
        async with self._SessionLocal() as session:
            team = Team(**kwargs)
            session.add(team)
            await session.commit()
            return team_orm_to_entity(team)

    async def get_team_by_id(self, id: int) -> TeamEntity:
        async with self._SessionLocal() as session:
            stmt = select(Team).where(Team.id == id)
            result = await session.execute(stmt)
            orm_obj = result.scalars().first()
            return team_orm_to_entity(
                orm_obj, await self.get_participants_by_team_id(orm_obj.id)
            ) if orm_obj else None

    async def get_team_by_name(self, name: str) -> TeamEntity:
        async with self._SessionLocal() as session:
            stmt = select(Team).where(Team.name == name)
            result = await session.execute(stmt)
            orm_obj = result.scalars().first()
            return team_orm_to_entity(
                orm_obj, await self.get_participants_by_team_id(orm_obj.id)
            ) if orm_obj else None

    async def get_teams(self) -> List[TeamEntity]:
        async with self._SessionLocal() as session:
            stmt = select(Team)
            result = await session.execute(stmt)
            orm_objs = result.scalars().all()
            return [team_orm_to_entity(
                o, await self.get_participants_by_team_id(o.id)
            ) for o in orm_objs]

    async def update_team(self, team_id: int, **kwargs):
        async with self._SessionLocal() as session:
            team_orm = await session.get(Team, team_id)
            if team_orm is None:
                raise ValueError(f"Team not found (ID: {team_id})")

            for key, value in kwargs.items():
                if hasattr(team_orm, key):
                    setattr(team_orm, key, value)

            await session.commit()
            await session.refresh(team_orm)

    async def delete_team(self, team_id: int):
        async with self._SessionLocal() as session:
            stmt = delete(Team).where(Team.id == team_id)
            await session.execute(stmt)
            await session.commit()

    #---PD Agreement---
    async def save_agreement(self, user_id: int):
        async with self._SessionLocal() as session:
            agreement = PDAgreement(user_id)
            await session.add(agreement)
            await session.commit()

    async def get_agreement(self, user_id: int) -> PDAgreement:
        async with self._SessionLocal() as session:
            stmt = select(PDAgreement).where(PDAgreement.user_id == user_id)
            result = await session.execute(stmt)
            return result.scalar()


db = PostgresDatabase(config.DATABASE_URI)
asyncio.run(db.init_db())
