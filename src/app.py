import os
import json
import logging
import time
from datetime import datetime, timedelta
from zoomus import ZoomClient
from light_controller import LightController


class OnAirLight():
    """Class for representing the on-air light"""

    def __init__(self):
        """Instantiate the class"""
        self.zoom = None
        self.user = None
        self.in_meeting = False
        self.refresh_delay = 10
        self._setup_zoom_client()
        self._setup_lighting_controller()
        self._set_current_user()
    
    def _setup_lighting_controller(self):
        """Setup lighting controller"""
        self.lc = LightController()

    def _setup_zoom_client(self):
        """Setup the zoom client"""
        self.zoom = ZoomClient(os.environ['ZOOM_API_KEY'], os.environ['ZOOM_API_SECRET'])

    def _set_current_user(self):
        """Sets the current user from the client"""
        zoom_user_email = os.environ['ZOOM_USER_EMAIL']
        user_list = json.loads(self.zoom.user.list().content)
        for user in user_list['users']:
            if zoom_user_email == user['email']:
                self.user = user
                logging.info(f'Current user found: {user["email"]}')
                return
        raise Exception('User email not found')

    def _get_zoom_time_format(self):
        """Returns the time format for the zoom api"""
        return "%Y-%m-%dT%H:%M:%SZ"

    def _is_meeting_supposed_to_be_in_progress(self, meeting):
        """Checks a meeting to determine if it is supposed to be in progress"""
        start_time = datetime.strptime(meeting['start_time'], self._get_zoom_time_format())
        end_time = start_time + timedelta(minutes=int(meeting['duration']))
        return start_time <= datetime.now() <= end_time

    def _get_all_meetings(self):
        """Returns all meetings for the user"""
        return json.loads(self.zoom.meeting.list(user_id=self.user['id']).content)

    def _get_live_meeting(self):
        """Returns the first currently live meeting or none"""
        logging.debug('Requesting live meetings from zoom API')
        results = self.zoom.meeting.list(user_id=self.user['id'], type='live')
        meetings = json.loads(results.content)['meetings']
        if meetings:
            logging.info(f'Meeting found: {meetings[0]["topic"]}')
            return meetings[0]
        return None

    def _check_for_meetings(self):
        """Checks continuously for meetings"""
        logging.info('Starting to check for meetings')
        while True:
            meeting = self._get_live_meeting()
            if meeting:
                if not self.in_meeting:
                    self.in_meeting = True
                    self.activate_light()
            else:
                if self.in_meeting:
                    self.deactivate_light()
                self.in_meeting = False
            time.sleep(self.refresh_delay)

    def _test_light(self):
        """Test the light"""
        logging.info('Testing light')
        self.activate_light()
        time.sleep(2)
        self.deactivate_light()
        logging.info('Light test complete')

    def activate_light(self):
        """Turn the on-air light on"""
        logging.info('Activating light')
        self.lc.turn_leds_on()

    def deactivate_light(self):
        """Turn the on-air light off"""
        logging.info('Deactivating light')
        self.lc.turn_leds_off()

    def run(self):
        """Run the application for the on-air light"""
        self._test_light()
        try:
            self._check_for_meetings()
        except KeyboardInterrupt:
            logging.info('Exiting')


if __name__ == '__main__':
    logging.getLogger().setLevel(logging.INFO)
    oal = OnAirLight()
    oal.run()
