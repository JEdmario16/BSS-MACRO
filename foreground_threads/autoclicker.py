import time
import threading
from pynput.mouse import Button, Controller
from pynput.keyboard import Listener, KeyCode

from libs.macro_tools import read_config, get_roblox_window, get_active_window

from typing import Optional
import loguru

class AutoClicker(threading.Thread):

    """
    AutoClicker thread. This thread is responsible for clicking the mouse at a given interval. This is used to auto-attack in-game.
    The parameters ``running`` and ``program_running`` are used to pause/stop the thread, and they are managed by the main thread, which can edit these parameters at runtime.
    """

    def __init__(self, logger: loguru.logger, delay: Optional[float] = 0.1, button: Button = Button.left, release_time: float= 0.1) -> None:

        """
        :param logger: The logger object. It need to be passed from the main thread, to avoid conflicts.
        :param delay: The delay between each click, in seconds.
        :param button: The button to click
        :param release_time: The time to hold the button down for, in seconds.

        :attr running: The running status of the thread. If set to False, the thread will stop.
        :attr is_paused: The pause status of the thread. If set to True, the thread will pause.
        :attr _roblox_window: The roblox window object. It is used to check if the roblox window is active so that the thread can click.
        """


        super().__init__()
        self._delay = delay
        self.button = button
        self.release_time = release_time
        self.running = True
        self.is_paused = False
        self.logger = logger
        self._roblox_window = get_roblox_window()

        self.mouse = Controller()

    def change_pause_status(self) -> None:
        self.is_paused = not self.is_paused
        self.logger.debug(f"AutoClicker thread is now {'paused' if self.is_paused else 'unpaused'}")
    

    def run(self):
        self.logger.debug("AutoClicker thread started")
        

        while self.running:
            while not self.is_paused and self.running:
                if get_active_window() == self._roblox_window.title:
                    self.mouse.press(self.button)
                    time.sleep(self.release_time)
                    self.mouse.release(self.button)
                time.sleep(self._delay)
        time.sleep(self._delay)

        self.exit()
        self.logger.debug("AutoClicker thread exited")

    def exit(self):
        self.is_paused = True
        self.running = False
        