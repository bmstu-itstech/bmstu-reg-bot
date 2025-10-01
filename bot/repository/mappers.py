from domain.models import ParticipantEntity, TeamEntity
from .models import Participant, Team


def participant_orm_to_entity(orm_obj: Participant) -> ParticipantEntity:
    return ParticipantEntity(
        id=orm_obj.id,
        telegram_username=orm_obj.telegram_username,
        last_name=orm_obj.last_name,
        first_name=orm_obj.first_name,
        middle_name=orm_obj.middle_name,
        university=orm_obj.university,
        group=orm_obj.group,
        passport=orm_obj.passport,
        team_id=orm_obj.team_id,
    )


def team_orm_to_entity(orm_obj: Team) -> TeamEntity:
    return TeamEntity(
        id=orm_obj.id,
        name=orm_obj.name,
        participant_count=orm_obj.participant_count
    )