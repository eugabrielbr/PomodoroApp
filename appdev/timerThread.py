import threading
import time


class TimerThread(threading.Thread):

    def __init__(self, duration_seconds, update_callback):
        super().__init__()
        self.duration = duration_seconds
        self.remaining = duration_seconds
        self.update_callback = update_callback
        self.running = False

    def run(self):
        self.running = True
        while self.running and self.remaining > 0:
            time.sleep(1)
            self.remaining -= 1
            self.update_callback(self.remaining)
        if self.remaining == 0:
            self.update_callback(0)  # Finaliza com 00:00

    def stop(self):
        self.running = False



