from dataclasses import dataclass
from typing import Optional, List


@dataclass
class ParticipantEntity:
    user_id: Optional[int]
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
    participant_ids: List[int]