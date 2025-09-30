from abc import ABC, abstractmethod 


class DatabaseBase(ABC):
    @abstractmethod
    def create_participant(self, **kwargs):
        pass
    
    @abstractmethod
    def get_participant(self, participant_id: int):
        pass
    
    @abstractmethod
    def update_participant(self, participant_id: int, **kwargs):
        pass
    
    @abstractmethod
    def delete_participant(self, participant_id: int) -> bool:
        pass

    # --- Team ---
    @abstractmethod
    def create_team(self, **kwargs):
        pass
    
    @abstractmethod
    def get_team(self, team_id: int):
        pass
    
    @abstractmethod
    def update_team(self, team_id: int, **kwargs):
        pass
    
    @abstractmethod
    def delete_team(self, team_id: int) -> bool:
        pass
