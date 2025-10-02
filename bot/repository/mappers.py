from domain.models import ParticipantEntity, TeamEntity
from .models import Participant, Team
from typing import List


def participant_orm_to_entity(orm_obj: Participant) -> ParticipantEntity:
    return ParticipantEntity(
        user_id=orm_obj.user_id,
        username=orm_obj.username,
        last_name=orm_obj.last_name,
        first_name=orm_obj.first_name,
        middle_name=orm_obj.middle_name,
        university=orm_obj.university,
        group=orm_obj.group,
        passport=orm_obj.passport,
        team_id=orm_obj.team_id,
    )


def team_orm_to_entity(orm_obj: Team, participants: List[ParticipantEntity] = []) -> TeamEntity:
    return TeamEntity(
        id=orm_obj.id,
        name=orm_obj.name,
        participant_ids=[p.user_id for p in participants]
    )