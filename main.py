from foreground_threads.speed_tracker import SpeedTracker
from foreground_threads.autoclicker import AutoClicker
from libs import macro_tools
import threading
import time
import keyboard
import loguru


logger = loguru.logger
log_filename= f"main.log"
logger.add("logs/main.log", format="{time} {level} {message} {name}:{line}", level="INFO")


class Application(threading.Thread):


    def __init__(self):
        super().__init__()

        self.speed_tracker = SpeedTracker(logger=logger, delay=0.5)
        self.autoclicker = AutoClicker(logger=logger, delay=0.7, release_time=0.1)

        self.is_paused = False
        self.running = True
        self.delay = 0.1

    
    def change_pause_status(self) -> None:

        # when we pause the program, we need to pause all foreground threads
        self.is_paused = not self.is_paused
        self.speed_tracker.is_paused = self.is_paused
        self.autoclicker.is_paused = self.is_paused
        logger.info(f"Program paused: {self.is_paused}")
        logger.debug(f"SpeedTracker paused: {self.speed_tracker.is_paused}")
        logger.debug(f"AutoClicker paused: {self.autoclicker.is_paused}")

    def change_program_status(self) -> None:
        self.running = not self.running
        self.speed_tracker.tracker_running = self.running
        self.autoclicker.running = self.running


    def run(self):
        logger.info("Starting main thread.")

        # start all foreground threads
        self.speed_tracker.start()
        self.autoclicker.start()

        while self.running:
            time.sleep(self.delay)
            if keyboard.is_pressed("p"):
                self.change_pause_status()
                
            if keyboard.is_pressed("q"):
                self.exit()
                break

    def verifiy_if_foreground_threads_are_stopped(self) -> None:

        assert self.speed_tracker.is_alive() == False
        assert self.autoclicker.is_alive() == False
        logger.debug("All foreground threads are stopped.")

    def exit(self):
        self.change_program_status()
        

        # wait for some time to make sure that all foreground threads are stopped
        time.sleep(1)
        try:
            self.verifiy_if_foreground_threads_are_stopped()
        except AssertionError:
            logger.warning("The main thread is trying to exit, but some foreground threads are still running after 0.5 seconds.")
            logger.warning("The main thread will exit anyway, but this may cause some problems.")
        logger.info("Exiting main thread.")
    

if __name__ == "__main__":
    app = Application()
    app.start()
    app.join()
    exit()