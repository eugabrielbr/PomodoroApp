# Este software utiliza a biblioteca ttkbootstrap, licenciada sob a Licença MIT:
# 
# Copyright (c) 2021-2024 Israel Dryer
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the “Software”), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

#----------------------------------------------------------------------------------------#

from ttkbootstrap import ttk,Window
import ttkbootstrap as tb
from ttkbootstrap.constants import *
import threading
import time
from timerThread import TimerThread
from auxFunctions import format_time


class PomodoroApp:
    
    def __init__(self,root,initial_timer_user):
        
        self.initial_timer_user = initial_timer_user # tempo que vai contar no timer 
        
        # elementos do app 
        self.root = root
        self.root.title("Pomodoro Timer")

        #frames 
        
        frame_combos = ttk.Frame(root)
        frame_combos.pack(pady=10)

        self.combo_hour = ttk.Combobox(frame_combos, values=[f"{i:01d} min" for i in range(1, 61)], width=23, state="readonly")
        self.combo_hour.set("Tempo de concentração")
        self.combo_hour.configure(foreground="gray")
        self.combo_hour.pack(pady=5,padx= 5,side ="left")

        self.combo_hour2 = ttk.Combobox(frame_combos, values=[f"{i:01d}" for i in range(1, 11)], width=23, state="readonly")
        self.combo_hour2.set("Número de sessões")
        self.combo_hour2.configure(foreground="gray")
        self.combo_hour2.pack(pady=5,padx= 5,side ="left")

        self.label_timer = ttk.Label(root, text=format_time(self.initial_timer_user), font=("Arial", 50))
        self.label_timer.pack(pady=20)

        self.start_button = ttk.Button(root, text="Start", command=lambda: self.start_timer(self.initial_timer_user),bootstyle=(SUCCESS, OUTLINE))
        self.start_button.pack(pady=5)

        self.reset_button = ttk.Button(root, text="Reset", command=self.reset_timer,bootstyle=(DANGER, OUTLINE))
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
        if self.actual: # só atualiza se o o botao reset nao for pressionado
            # Garante que a atualização da UI ocorra na thread principal
            self.root.after(0, lambda: self.update_ui(remaining_seconds))

    
    


def main():
    
    minutes = 1
    seconds = 2
    root = Window(themename="superhero")
    root.geometry("400x350")
    app = PomodoroApp(root,seconds)
    root.mainloop()
    
if __name__ == "__main__":
    
    main()