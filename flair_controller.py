import json
from datetime import datetime, time
from typing import Dict, List, Optional
import logging
from flair_api import make_client

class FlairController:
    def __init__(self, config_file: str = "flair_config.json"):
        self.config = self._load_config(config_file)
        self.api_base_url = self.config.get("api_base_url", "https://api.flair.co/")
        self.client_id = self.config.get("client_id")
        self.client_secret = self.config.get("client_secret")
        self.rooms = self.config.get("rooms", {})
        self.schedule = self.config.get("schedule", [])

        self.client = None
        if self.client_id and self.client_secret:
            # print(self.client_id, self.client_secret, self.api_base_url)
            self.client = make_client(self.client_id, self.client_secret, self.api_base_url)

        logging.basicConfig(level=logging.INFO)
        # print(self.client.get('rooms'))
        self.logger = logging.getLogger(__name__)

    def _load_config(self, config_file: str) -> Dict:
        try:
            with open(config_file, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            self.logger.error(f"Config file {config_file} not found")
            return {}
        except json.JSONDecodeError:
            self.logger.error(f"Invalid JSON in config file {config_file}")
            return {}

    def _ensure_client(self) -> bool:
        if not self.client:
            self.logger.error("Flair API client not configured. Check client_id and client_secret.")
            return False
        return True

    def set_room_state(self, room_name: str, active: bool) -> bool:
        if not self._ensure_client():
            return False

        if room_name not in self.rooms:
            self.logger.error(f"Room '{room_name}' not found in configuration")
            return False

        room_id = self.rooms[room_name]["id"]

        try:
            room = self.client.get('rooms', id=room_id)
            if not room:
                self.logger.error(f"Room with ID '{room_id}' not found")
                return False

            # Update room attributes with active state
            room.update({'active': active})

            state = "active" if active else "inactive"
            self.logger.info(f"Successfully set room '{room_name}' to {state}")
            return True

        except Exception as e:
            self.logger.error(f"Failed to set room '{room_name}' state: {e}")
            return False

    def activate_room(self, room_name: str) -> bool:
        return self.set_room_state(room_name, True)

    def deactivate_room(self, room_name: str) -> bool:
        return self.set_room_state(room_name, False)

    def get_room_state(self, room_name: str) -> Optional[Dict]:
        if not self._ensure_client():
            return None

        if room_name not in self.rooms:
            self.logger.error(f"Room '{room_name}' not found in configuration")
            return None

        room_id = self.rooms[room_name]["id"]

        try:
            room = self.client.get('rooms', id=room_id)
            if not room:
                self.logger.error(f"Room with ID '{room_id}' not found")
                return None

            return {
                'active': room.attributes['active'],
                'id': room_id,
                'name': room_name
            }

        except Exception as e:
            self.logger.error(f"Failed to get room '{room_name}' state: {e}")
            return None

    def get_all_rooms(self) -> List[str]:
        return list(self.rooms.keys())

    def list_api_rooms(self) -> Optional[List[Dict]]:
        """Query Flair API for all rooms in the structure."""
        if not self._ensure_client():
            return None

        try:
            rooms = self.client.get('rooms')
            print(rooms)
            if not rooms:
                return []

            room_list = []
            for room in rooms:
                #print('room - id', room.id_)
                #print('room - attributes', room.attributes)
                room_list.append({
                    'id': room.id_,
                    'name': room.attributes['name'],
                    'active': room.attributes['active'],
                    'room': room, 
                })

            return room_list

        except Exception as e:
            self.logger.error(f"Failed to list rooms from API: {e}")
            return None

    def _parse_time(self, time_str: str) -> time:
        """Parse time string in HH:MM format."""
        hours, minutes = map(int, time_str.split(':'))
        return time(hours, minutes)

    def _is_time_in_range(self, current: time, start: time, end: time) -> bool:
        """Check if current time is within the range, handling overnight periods."""
        if start <= end:
            return start <= current <= end
        else:  # Overnight period (e.g., 22:00 to 07:00)
            return current >= start or current <= end

    def apply_schedule(self) -> Dict[str, Dict]:
        """Apply the schedule defined in config, updating rooms as needed."""
        if not self._ensure_client():
            return {}

        if not self.schedule:
            self.logger.warning("No schedule defined in configuration")
            return {}

        current_time = datetime.now().time()
        results = {}

        # Find active schedule segment
        active_segment = None
        for segment in self.schedule:
            start_time = self._parse_time(segment['from'])
            end_time = self._parse_time(segment['to'])

            if self._is_time_in_range(current_time, start_time, end_time):
                active_segment = segment
                break

        if not active_segment:
            self.logger.info("No active schedule segment found for current time")
            return {}

        self.logger.info(f"Applying schedule segment: {active_segment.get('segmentName', 'unnamed')}")

        # Process each room in the segment
        room_states = active_segment.get('roomState', {})
        for room_name, desired_state in room_states.items():
            if room_name not in self.rooms:
                self.logger.warning(f"Room '{room_name}' in schedule not found in configuration")
                results[room_name] = {
                    'success': False,
                    'reason': 'not_configured',
                    'desired': desired_state
                }
                continue

            # Get current room state
            current_state = self.get_room_state(room_name)
            if not current_state:
                results[room_name] = {
                    'success': False,
                    'reason': 'failed_to_get_state',
                    'desired': desired_state
                }
                continue

            desired_active = desired_state == 'active'
            current_active = current_state.get('active')

            # Only update if state is different
            if current_active == desired_active:
                results[room_name] = {
                    'success': True,
                    'reason': 'already_correct',
                    'desired': desired_state,
                    'current': 'active' if current_active else 'inactive'
                }
            else:
                # Update room state
                success = self.set_room_state(room_name, desired_active)
                results[room_name] = {
                    'success': success,
                    'reason': 'updated' if success else 'update_failed',
                    'desired': desired_state,
                    'previous': 'active' if current_active else 'inactive'
                }

        return results