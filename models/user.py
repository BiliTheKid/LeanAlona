from typing import Any, Dict

## user state management 
class UserState:
    def __init__(self, user_id: str):
        self.user_id = user_id
        self.current_stage = 'start'
        self.data = {}

    def update_state(self, new_stage: str):
        self.current_stage = new_stage

    def update_data(self, key: str, value: Any):
        self.data[key] = value

    def get_current_stage(self) -> str:
        return self.current_stage

    def get_data(self) -> Dict[str, Any]:
        return self.data

    def get_value(self, key: str) -> Any:
        return self.data.get(key)

    def reset(self):
        """Resets the user state and data."""
        self.state = 'start'
        self.data = {}

    def __repr__(self):
        return f"UserState(user_id={self.user_id!r}, current_stage={self.current_stage!r}, data={self.data!r})"
