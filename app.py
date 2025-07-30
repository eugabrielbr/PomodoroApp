from ttkbootstrap import ttk,Window
import ttkbootstrap as tb
from ttkbootstrap.constants import *
import threading
import time
from timerThread import TimerThread
from auxFunctions import format_time,notificationSystem

class PomodoroApp:
    
    def __init__(self,root):
        
        self.initial_timer_user = 0 # tempo que vai contar no timer 

        # elementos do app 
        self.root = root
        self.root.title("Pomodoro Timer")

        #frames 
        frame_label = ttk.Frame(root)
        frame_label.pack(pady=10)
        
        frame_combos = ttk.Frame(root)
        frame_combos.pack(pady=10)

        frame_timer = ttk.Frame(root)
        frame_timer.pack(pady=10)

        frame_buttons = ttk.Frame(root)
        frame_buttons.pack(pady=10)

        self.label_aviso = ttk.Label(frame_label, text="Selecione um tempo de concentração, intervalo e número de sessões", font=("Arial", 8))
        self.label_aviso.pack(pady=1, side = "left")

        self.combo_hour = ttk.Combobox(frame_combos, values=[f"{i:01d} min" for i in range(5, 61,5)], width=13, state="readonly")
        self.combo_hour.set("concentração")
        self.combo_hour.configure(foreground="gray")
        self.combo_hour.pack(pady=1,padx= 5,side ="left")
        self.combo_hour.bind("<<ComboboxSelected>>", lambda e: (self.comboboxcheck(self.combo_hour.get().strip(" min")),self.changeStatusButton("normal")))

        self.combo_hour3 = ttk.Combobox(frame_combos, values=["5 min","10 min","15 min"], width=13, state="readonly")
        self.combo_hour3.set("intervalo")
        self.combo_hour3.configure(foreground="gray")
        self.combo_hour3.pack(pady=1,padx= 5,side ="left")

        self.combo_hour2 = ttk.Combobox(frame_combos, values=[f"{i:01d}" for i in range(1, 11)], width=13, state="readonly")
        self.combo_hour2.set("sessões")
        self.combo_hour2.configure(foreground="gray")
        self.combo_hour2.pack(pady=1,padx= 5,side ="left")

        self.label_timer = ttk.Label(frame_timer, text=format_time(self.initial_timer_user), font=("Terminal", 50),foreground="white")
        self.label_timer.pack(pady=20)

        self.start_button = ttk.Button(frame_buttons, text="Start", command=lambda: self.start_timer(self.initial_timer_user),bootstyle=(SUCCESS),width=8,state="disabled")
        self.start_button.pack(pady=5,padx= 5,side ="left",ipady=5)

        self.reset_button = ttk.Button(frame_buttons, text="Reset", command=self.reset_timer,bootstyle=(DANGER, OUTLINE),width=8)
        self.reset_button.pack(pady=5,padx= 5,side ="left",ipady=5)
    
        self.timer_thread = None

        self.actual = True #gambiarra 

    def update_ui(self, remaining_seconds):
        self.label_timer.config(text=format_time(remaining_seconds))
        if remaining_seconds == 0:
            self.label_timer.config(text="00:00")
            notificationSystem("Timer expirado!", "Hora do intervalo! Nada de celular, hein?!", 3)

    def start_timer(self,initial_timer):
        self.actual = True
        if initial_timer == 0:
            notificationSystem("Selecione um timer!", "Você precisa selecionar um tempo para iniciar",3)
            return 
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

    def comboboxcheck(self,valor):

        if valor.isdigit():
            self.initial_timer_user = int(valor) * 60
            self.update_ui(self.initial_timer_user)
            self.reset_timer()
        else:
            self.initial_timer_user = 0


    def changeStatusButton(self, state):
        
        self.start_button.configure(state=state)
    

def main():

    root = Window(themename="solar")
    root.geometry("400x380")
    app = PomodoroApp(root)
    root.mainloop()
    
if __name__ == "__main__":
    
    main()