import threading
from libs import macro_tools, move_lib
from typing import Optional
import time
from datetime import datetime, timedelta
import loguru

class SpeedTracker(threading.Thread):

    """
    This class is responsible for tracking the player's speed and haste stacks.
    The parameters ``is_paused`` and ``tracker_running`` are used to pause/stop the thread, and they are managed by the main thread, which can edit these parameters at runtime.
    """

    def __init__(self, logger: loguru.logger, delay: Optional[float] = 0.1) -> None:
        super().__init__()

        self._delay = delay

        self.is_paused = False
        self.tracker_running = False
        self._roblox_window = macro_tools.get_roblox_window()

        self.current_haste_stack = 0
        self.previous_haste_stack = 0
        self.current_haste_time = 0
        self.has_bear = 0
        self.current_player_speed = 0

        self.logger = logger

    def change_pause_status(self) -> None:
        self.is_paused = not self.is_paused
        self.logger.debug(f"SpeedTracker thread is now {'paused' if self.is_paused else 'unpaused'}")

    def get_current_movespeed(self):

        """
        Calculates the current player speed by applying any haste and bear form modifiers.
        """

        BUFFS_REGION = (0, 35, 600, 40)
        CANONICAL_SPEED = 18
        screenshot = macro_tools.screenshot(region=BUFFS_REGION)
        player_speed = macro_tools.read_config().getint("PLAYER", "player_speed")

        # our function only detect haste stacks in the first 3 seconds of the buff. After that, it will return 0
        # So, we will only update the haste stack in this function only if this is different from 0.
        stack_on_screen = move_lib.get_current_haste_stack(screenshot)
        if stack_on_screen != 0:
            self.current_haste_stack = stack_on_screen 

        self.update_haste_time()

        self.bear_form = 1 if move_lib.check_if_bear(screenshot) else 0

        self.current_player_speed = (
            (CANONICAL_SPEED + 6 * self.bear_form) * player_speed / CANONICAL_SPEED
        ) * (1 + 0.1 * self.current_haste_stack)
            

    def update_haste_time(self):

        """
        Update the time of the last haste stack and reset the haste stack if necessary.
        """

        if self.current_haste_stack > 0 and self.current_haste_stack != self.previous_haste_stack or self.current_haste_stack == 10:
            self.current_haste_time = datetime.now()
            self.previous_haste_stack = self.current_haste_stack
        else:
            delta = (
                datetime.now() - self.current_haste_time
                if self.current_haste_time != 0
                else timedelta(seconds=0)
            )

            self.delta = delta
            if delta.seconds >= 19:
                self.previous_haste_stack = self.current_haste_stack
                self.current_haste_stack = 0
                self.current_haste_time = 0

    def run(self):
        self.tracker_running = True
        self.logger.debug("Speed tracker started")
        while self.tracker_running:
            while not self.is_paused and self.tracker_running:
                if macro_tools.get_active_window() == self._roblox_window.title:
                    self.get_current_movespeed()
                time.sleep(self._delay)
            time.sleep(self._delay)
        
        self.exit()
        self.logger.debug("Speed tracker stopped")

    def exit(self) -> None:
        self.tracker_running = False
        self.is_paused = False

