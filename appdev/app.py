from ttkbootstrap import ttk,Window
import ttkbootstrap as tb
from ttkbootstrap.constants import *
import threading
import time
from timerThread import TimerThread
from auxFunctions import format_time,notificationSystem,ao_clicar,notification_with_click

# ta notificando duas vezes

class PomodoroApp:
    
    def __init__(self,root):
        
        self.initial_timer_user = 0# tempo que vai contar no timer 
        self.number_of_sessions = 0
        self.time_interval = 0
        self.interval = False # gerencia a alternancia entre intervalo e sessao 
        self.lock = threading.Lock()
        self.finish = 0 # ignora quando o remaning é 0 duas vezes seguidas // false = nao terminou || true = terminou

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

        self.combo_hour = ttk.Combobox(frame_combos, values=[f"{i:01d} min" for i in range(5, 61,5)], width=13, state="readonly") #5, 61,5
        self.combo_hour.set("concentração")
        self.combo_hour.configure(foreground="gray")
        self.combo_hour.pack(pady=1,padx= 5,side ="left")
        self.combo_hour.bind("<<ComboboxSelected>>", lambda e: (self.timer_change(self.combo_hour.get().strip(" min")),self.changeStatusButton("normal")))

        self.combo_hour3 = ttk.Combobox(frame_combos, values=["5 min","10 min","15 min","30 min"], width=13, state="readonly")
        self.combo_hour3.set("intervalo")
        self.combo_hour3.configure(foreground="gray")
        self.combo_hour3.pack(pady=1,padx= 5,side ="left")
        self.combo_hour3.bind("<<ComboboxSelected>>", lambda e: (self.timer_interval_change(self.combo_hour3.get().strip(" min"))))

        self.combo_hour2 = ttk.Combobox(frame_combos, values=[f"{i:01d}" for i in range(1, 11)], width=13, state="readonly")
        self.combo_hour2.set("sessões")
        self.combo_hour2.configure(foreground="gray")
        self.combo_hour2.pack(pady=1,padx= 5,side ="left")
        self.combo_hour2.bind("<<ComboboxSelected>>", lambda e: (self.timer_sessions_change(self.combo_hour2.get())))

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
        try:

            if remaining_seconds == 0:
                
                self.timer_thread.stop()

                if self.number_of_sessions == 0:

                    self.label_timer.config(text="00:00")
                    self.combo_hour.state(["!disabled"])
                    self.combo_hour2.state(["!disabled"]) #disabled combobox when starting the timer
                    self.combo_hour3.state(["!disabled"])

                    notificationSystem("Timer expirado!", "Sua sessão pomodoro acabou. Espero que tenha sido produtivo! :D", 3)

                elif self.number_of_sessions > 0 and not self.interval and self.finish == 0: 
                    
                    threading.Thread(
                        target=lambda: self.notification_interval("Hora da pausa!", "Clique aqui para começar seu intervalo", 120),
                        daemon=True
                    ).start()

                
                elif self.number_of_sessions > 0 and self.interval and self.finish == 0:
                    
                    threading.Thread(
                        target=lambda: self.notification_focus("Fim do intervalo", "Clique aqui para voltar ao foco", 120),
                        daemon=True
                    ).start()
                
                self.finish += 1
                
            if self.finish > 2:
                self.finish = 0 
        
        except ValueError:
            pass

    def start_timer(self, initial_timer):
        
        self.combo_hour.state(["disabled"])
        self.combo_hour2.state(["disabled"]) #disabled combobox when starting the timer
        self.combo_hour3.state(["disabled"])

        self.actual = True

        if initial_timer == 0:
            notificationSystem("Selecione um timer!", "Você precisa selecionar um tempo para iniciar", 3)
            return

        def _wait_and_start():
            if self.timer_thread and self.timer_thread.is_alive():
                # Reagenda para verificar daqui 50ms sem travar a UI
                self.root.after(50, _wait_and_start)
            else:
                
                self.timer_thread = TimerThread(initial_timer, self.thread_safe_update)
                self.timer_thread.start()
                
                return 

        _wait_and_start()  

    def reset_timer(self):
        
        if self.timer_thread:
            self.timer_thread.stop()
            self.interval = False 

            self.actual = False 
            self.root.after(0, lambda: self.update_ui(self.initial_timer_user))
        
        self.number_of_sessions = 0 
        self.time_interval = 0
        self.initial_timer_user = 0 
        self.combo_hour3.set("intervalo")
        self.combo_hour2.set("sessões")
        self.combo_hour.set("concentração")
        self.changeStatusButton("disabled")
        self.update_ui(0)
        self.combo_hour.state("disabled")
        self.combo_hour2.state("disabled") #disabled combobox when starting the timer
        self.combo_hour3.state("disabled")

            
    def thread_safe_update(self, remaining_seconds):
        if self.actual: # só atualiza se o lock permitir
            # Garante que a atualização da UI ocorra na thread principal
            self.root.after(0, lambda: self.update_ui(remaining_seconds))

    def timer_change(self,value):

        if value.isdigit():
            self.initial_timer_user = int(value) * 60
            self.update_ui(self.initial_timer_user)
        else:
            self.initial_timer_user = 0


    def timer_sessions_change(self,value):
        value = int(value)
        
        if value > 0:
            
            self.number_of_sessions = value - 1 

    def timer_interval_change(self,value):

        self.time_interval = int(value) * 60


    def changeStatusButton(self, state):
        
        self.start_button.configure(state=state)

    def notification_interval(self, title, message, timeout):
        retorno = notification_with_click(title, message, timeout)

        if retorno:  # se clicou na notificação
            # agenda no Tkinter (sem travar)
            self.root.after(0, lambda: self.start_interval())

    def notification_focus(self, title, message, timeout):
        retorno = notification_with_click(title, message, timeout)

        if retorno:  # se clicou na notificação
            # agenda no Tkinter (sem travar)
            self.root.after(0, lambda: self.start_focus())

    def start_interval(self):
        """Inicia o intervalo após a notificação"""
        self.interval = True
        self.start_timer(self.time_interval)
        self.finish = False
    
    def start_focus(self):
        """Volta para a sessão de foco após a notificação"""
        self.interval = False
        self.start_timer(self.initial_timer_user)
        self.number_of_sessions -= 1


def main():

    root = Window(themename="solar")
    root.geometry("400x380")
    app = PomodoroApp(root)
    root.mainloop()
    
if __name__ == "__main__":
    
    main()