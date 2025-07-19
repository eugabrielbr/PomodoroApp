from ttkbootstrap import ttk,Window
from ttkbootstrap.constants import *
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

class PomodoroApp:
    
    def __init__(self, root,initial_timer_user):
        self.initial_timer_user = initial_timer_user
        self.root = root
        self.root.title("Pomodoro Timer")
        self.label_timer = ttk.Label(root, text=format_time(self.initial_timer_user), font=("Arial", 50))
        self.label_timer.pack(pady=20)

        self.start_button = ttk.Button(root, text="Start", command=lambda: self.start_timer(self.initial_timer_user))
        self.start_button.pack(pady=5)

        self.reset_button = ttk.Button(root, text="Reset", command=self.reset_timer)
        self.reset_button.pack(pady=5)
    
        self.timer_thread = None

        self.actual = True #gambiarra 

    def update_ui(self, remaining_seconds):
        self.label_timer.config(text=format_time(remaining_seconds))
        if remaining_seconds == 0:
            self.label_timer.config(text="Acabou!")

    def start_timer(self,initial_timer):
        self.actual = True
        if self.timer_thread and self.timer_thread.is_alive():
            return  # Já está rodando
        self.timer_thread = TimerThread(initial_timer, self.thread_safe_update)
        self.timer_thread.start()

    def reset_timer(self):
        if self.timer_thread:
            self.timer_thread.stop()
            self.actual = False 
            self.root.after(0, lambda: self.update_ui(self.initial_timer_user))
            

    def thread_safe_update(self, remaining_seconds):
        if self.actual:

            # Garante que a atualização da UI ocorra na thread principal
            self.root.after(0, lambda: self.update_ui(remaining_seconds))


def format_time(seconds):
    minutes = seconds // 60
    seconds = seconds % 60
    return f"{minutes:02}:{seconds:02}"

def main():
    minutes = 1
    seconds = minutes * 60
    root = Window(themename="darkly")
    root.geometry("400x350")
    app = PomodoroApp(root,seconds)
    root.mainloop()
    
if __name__ == "__main__":
    
    main()