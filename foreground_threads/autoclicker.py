import time
import threading
from pynput.mouse import Button, Controller
from pynput.keyboard import Listener, KeyCode

from libs.macro_tools import read_config, get_roblox_window, get_active_window

from typing import Optional


class AutoClicker(threading.Thread):

    """
    Esta classe é responsável por clicar automaticamente
    Ela roda em um thread separado para não atrapalhar o funcionamento do programa.

    atualmente, o método de pause consiste em verificar no arquivo de configuração se o programa está pausado ou não.
    O motivo para isso, é que adicionar um key listner é muito complexo, pois deve envolver
    :param delay: Delay entre cada click
    """

    def __init__(self, delay: Optional[float] = 0.1) -> None:
        super().__init__()
        self._delay = delay
        self.running = True
        self.program_running = True
        self.cfg = read_config()
        self._roblox_window = get_roblox_window()
        self.run()

    def start_clicking(self):
        self.running = True

    def stop_clicking(self):
        self.running = False

    def exit(self):
        self.stop_clicking()
        self.program_running = False
        print("AutoClicker thread exited")

    def run(self):
        while self.program_running:
            print("AutoClicker thread running")
            while self.running:
                if get_active_window() == self._roblox_window.title:
                    mouse = Controller()
                    mouse.click(Button.left, 1)
                    time.sleep(self._delay)
                time.sleep(self._delay)
        time.sleep(self._delay)
