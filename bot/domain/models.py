from dataclasses import dataclass
from typing import Optional


@dataclass
class ParticipantEntity:
    id: Optional[int]
    telegram_username: str
    last_name: str
    first_name: str
    middle_name: str
    university: str
    group: Optional[str]
    passport: str
    team_id: Optional[int]


@dataclass
class TeamEntity:
    id: Optional[int]
    name: str
    participant_count: int