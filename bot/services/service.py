from repository.database import DatabaseBase, db
from domain.models import TeamEntity, ParticipantEntity
from .exc import AlreadyExists, NotRegistered, TooManyTeammates, NotTeammate
from .config import MAX_TEAMMATES

class Service:
    def __init__(self, db: DatabaseBase):
        self._db = db


    async def get_username_by_id(self, user_id: int) -> str:
        participant = await self._db.get_participant_by_id(user_id)
        return participant.username


    async def check_agreement(self, user_id: int) -> bool:
        user = await self._db.get_agreement(user_id)
        return user != None
    
    
    async def save_agreement(self, user_id: int):
        await self._db.save_agreement(user_id)


    async def register_participant(self, user_id: int, **kwargs) -> ParticipantEntity:
        participant = await self._db.get_participant_by_id(user_id)
        if participant:
            raise AlreadyExists('Username is already registered')
        
        participant_entity = await self._db.create_participant(user_id=user_id, **kwargs)
        return participant_entity


    async def get_profile(self, user_id: int) -> ParticipantEntity:
        return await self._db.get_participant_by_id(user_id)
    

    async def get_participant_team(self, user_id: int) -> TeamEntity:
        participant = await self._db.get_participant_by_id(user_id)
        if not participant:
            raise NotRegistered('Username is not registered')

        team_id = participant.team_id
        if not team_id:
            return None
        
        team = await self._db.get_team_by_id(team_id)
        return team
    

    async def create_team(self, name: str) -> TeamEntity:
        team = await self._db.get_team_by_name(name)
        if team:
            raise AlreadyExists('Team with such name already registered')
        
        return await self._db.create_team(name=name)
    

    async def add_teammate(self, team_name: str, user_id: int):
        team = await self._db.get_team_by_name(team_name)
        if not team:
            raise NotRegistered('Team is not registered')
        
        teammate = await self._db.get_participant_by_id(user_id)
        if not teammate:
            raise NotRegistered('Username is not registered')
        
        participants = await self._db.get_participants_by_team_id(team.id)
        if len(participants) >= MAX_TEAMMATES:
            raise TooManyTeammates("Too many teammates in the team")

        await self._db.update_participant(teammate.user_id, team_id=team.id)

    
    async def remove_teammate(self, team_name: str, user_id: int):
        team = await self._db.get_team_by_name(team_name)
        if not team:
            raise NotRegistered('Team is not registered')
        
        teammate = await self._db.get_participant_by_id(user_id)
        if not teammate:
            raise NotRegistered('Username is not registered')
        
        if teammate.team_id != team.id:
            raise NotTeammate(f'{teammate.telegram_username} is not in team')
        
        return self._db.update_participant(teammate.user_id, team_id=None)
        


service = Service(db)