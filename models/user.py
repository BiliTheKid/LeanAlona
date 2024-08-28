# from typing import Any, Dict

# ## user state management 
# class UserState:
#     def __init__(self, user_id: str):
#         self.user_id = user_id
#         self.current_stage = 'start'
#         self.data = {}

#     def update_state(self, new_stage: str):
#         self.current_stage = new_stage

#     def update_data(self, key: str, value: Any):
#         self.data[key] = value

#     def get_current_stage(self) -> str:
#         return self.current_stage

#     def get_data(self) -> Dict[str, Any]:
#         return self.data

#     def get_value(self, key: str) -> Any:
#         return self.data.get(key)

#     def reset(self):
#         """Resets the user state and data."""
#         self.state = 'start'
#         self.data = {}

#     def __repr__(self):
#         return f"UserState(user_id={self.user_id!r}, current_stage={self.current_stage!r}, data={self.data!r})"



# import threading
# from datetime import datetime, timedelta

# class ThreadSafeUserStateManager:
#     def __init__(self, timeout_minutes: int = 30):
#         self._lock = threading.Lock()
#         self._user_states: Dict[str, UserState] = {}
#         self._last_activity: Dict[str, datetime] = {}
#         self.timeout = timedelta(minutes=timeout_minutes)

#     def get_user_state(self, user_id: str) -> UserState:
#         with self._lock:
#             self._clean_inactive_states()
#             if user_id not in self._user_states:
#                 self._user_states[user_id] = UserState(user_id)
#             self._last_activity[user_id] = datetime.now()
#             return self._user_states[user_id]

#     def update_user_state(self, user_id: str, new_state: UserState) -> None:
#         with self._lock:
#             self._user_states[user_id] = new_state
#             self._last_activity[user_id] = datetime.now()

#     def _clean_inactive_states(self) -> None:
#         now = datetime.now()
#         inactive_users = [
#             user_id for user_id, last_active in self._last_activity.items()
#             if now - last_active > self.timeout
#         ]
#         for user_id in inactive_users:
#             del self._user_states[user_id]
#             del self._last_activity[user_id]
from typing import Any, Dict
import threading
from datetime import datetime, timedelta
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    filename='user_state_manager.log',
                    filemode='a')
logger = logging.getLogger(__name__)

## User state management 
class UserState:
    def __init__(self, user_id: str):
        self.user_id = user_id
        self.current_stage = 'start'
        self.data = {}

    def update_state(self, new_stage: str):
        logger.info(f"Updating state for user {self.user_id}: {self.current_stage} -> {new_stage}")
        self.current_stage = new_stage

    def update_data(self, key: str, value: Any):
        logger.info(f"Updating data for user {self.user_id}: {key} = {value}")
        self.data[key] = value

    def get_current_stage(self) -> str:
        return self.current_stage

    def get_data(self) -> Dict[str, Any]:
        return self.data

    def get_value(self, key: str) -> Any:
        return self.data.get(key)

    def reset(self):
        """Resets the user state and data."""
        logger.info(f"Resetting state for user {self.user_id}")
        self.current_stage = 'start'
        self.data = {}

    def __repr__(self):
        return f"UserState(user_id={self.user_id!r}, current_stage={self.current_stage!r}, data={self.data!r})"


class ThreadSafeUserStateManager:
    def __init__(self, timeout_minutes: int = 30):
        self._lock = threading.Lock()
        self._user_states: Dict[str, UserState] = {}
        self._last_activity: Dict[str, datetime] = {}
        self.timeout = timedelta(minutes=timeout_minutes)
        logger.info(f"Initialized ThreadSafeUserStateManager with timeout of {timeout_minutes} minutes")

    def get_user_state(self, user_id: str) -> UserState:
        with self._lock:
            self._clean_inactive_states()
            if user_id not in self._user_states:
                self._user_states[user_id] = UserState(user_id)
                logger.info(f"Created new UserState for user {user_id}")
            else:
                logger.info(f"Retrieved existing UserState for user {user_id}")
            self._last_activity[user_id] = datetime.now()
            return self._user_states[user_id]

    def update_user_state(self, user_id: str, new_state: UserState) -> None:
        with self._lock:
            logger.info(f"Updating UserState for user {user_id}")
            self._user_states[user_id] = new_state
            self._last_activity[user_id] = datetime.now()

    def _clean_inactive_states(self) -> None:
        now = datetime.now()
        inactive_users = [
            user_id for user_id, last_active in self._last_activity.items()
            if now - last_active > self.timeout
        ]
        for user_id in inactive_users:
            logger.info(f"Removing inactive UserState for user {user_id}")
            del self._user_states[user_id]
            del self._last_activity[user_id]