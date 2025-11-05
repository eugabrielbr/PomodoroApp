from ttkbootstrap import ttk, Window
import ttkbootstrap as tb
from ttkbootstrap.constants import *
import threading
import time

from timerThread import TimerThread
from notification import format_time, notificationSystem, ao_clicar, notification_with_click


class PomodoroApp:
    def __init__(self, root):
        # variáveis de controle
        self.initial_timer_user = 0
        self.number_of_sessions = 0
        self.time_interval = 0
        self.interval = False
        self.lock = threading.Lock()
        self.finished = False
        self.actual = True
        self.timer_thread = None

        # configuração da janela
        self.root = root
        self.root.title("Pomodoro Timer")

        # frames principais
        frame_label = ttk.Frame(root)
        frame_label.pack(pady=10)

        frame_combos = ttk.Frame(root)
        frame_combos.pack(pady=10)

        frame_timer = ttk.Frame(root)
        frame_timer.pack(pady=10)

        frame_buttons = ttk.Frame(root)
        frame_buttons.pack(pady=10)

        # label informativa
        self.label_aviso = ttk.Label(
            frame_label,
            text="Selecione um tempo de concentração, intervalo e número de sessões",
            font=("Arial", 8)
        )
        self.label_aviso.pack(pady=1, side="left")

        # combobox de concentração
        self.combo_hour = ttk.Combobox(
            frame_combos,
            values=[f"{i:01d} min" for i in range(5, 61, 5)],
            width=13,
            state="readonly"
        )
        self.combo_hour.set("concentração")
        self.combo_hour.configure(foreground="gray")
        self.combo_hour.pack(pady=1, padx=5, side="left")
        self.combo_hour.bind(
            "<<ComboboxSelected>>",
            lambda e: (
                self.timer_change(self.combo_hour.get().strip(" min")),
                self.changeStatusButton("normal")
            )
        )

        # combobox de intervalo
        self.combo_hour3 = ttk.Combobox(
            frame_combos,
            values=["5 min", "10 min", "15 min", "30 min"],
            width=13,
            state="readonly"
        )
        self.combo_hour3.set("intervalo")
        self.combo_hour3.configure(foreground="gray")
        self.combo_hour3.pack(pady=1, padx=5, side="left")
        self.combo_hour3.bind(
            "<<ComboboxSelected>>",
            lambda e: self.timer_interval_change(self.combo_hour3.get().strip(" min"))
        )

        # combobox de sessões
        self.combo_hour2 = ttk.Combobox(
            frame_combos,
            values=[f"{i:01d}" for i in range(1, 11)],
            width=13,
            state="readonly"
        )
        self.combo_hour2.set("sessões")
        self.combo_hour2.configure(foreground="gray")
        self.combo_hour2.pack(pady=1, padx=5, side="left")
        self.combo_hour2.bind(
            "<<ComboboxSelected>>",
            lambda e: self.timer_sessions_change(self.combo_hour2.get())
        )

        # label do timer
        self.label_timer = ttk.Label(
            frame_timer,
            text=format_time(self.initial_timer_user),
            font=("Terminal", 50),
            foreground="white"
        )
        self.label_timer.pack(pady=20)

        # botão de start
        self.start_button = ttk.Button(
            frame_buttons,
            text="Start",
            command=lambda: self.start_timer(self.initial_timer_user),
            bootstyle=(SUCCESS),
            width=8,
            state="disabled"
        )
        self.start_button.pack(pady=5, padx=5, side="left", ipady=5)

        # botão de reset
        self.reset_button = ttk.Button(
            frame_buttons,
            text="Reset",
            command=self.reset_timer,
            bootstyle=(DANGER, OUTLINE),
            width=8
        )
        self.reset_button.pack(pady=5, padx=5, side="left", ipady=5)

    # atualiza o timer na interface
    def update_ui(self, remaining_seconds):
        self.label_timer.config(text=format_time(remaining_seconds))
        try:
            if remaining_seconds == 0 and not self.finished:
                self.timer_thread.stop()

                if self.number_of_sessions == 0:
                    self.end_cycle()
                    notificationSystem(
                        "Timer expirado!",
                        "Sua sessão pomodoro acabou. Espero que tenha sido produtivo! :D",
                        15
                    )

                elif self.number_of_sessions > 0 and not self.interval:
                    threading.Thread(
                        target=lambda: self.notification_interval(
                            "Hora da pausa!",
                            "Clique aqui para começar seu intervalo",
                            15
                        ),
                        daemon=True
                    ).start()

                elif self.number_of_sessions > 0 and self.interval:
                    threading.Thread(
                        target=lambda: self.notification_focus(
                            "Fim do intervalo",
                            "Clique aqui para voltar ao foco",
                            15
                        ),
                        daemon=True
                    ).start()

                self.finished = True
        except ValueError:
            pass

    # atualização segura a partir da thread
    def thread_safe_update(self, remaining_seconds):
        if self.actual:
            self.root.after(0, lambda: self.update_ui(remaining_seconds))

    # inicia o timer
    def start_timer(self, initial_timer):
        self.combo_hour.state(["disabled"])
        self.combo_hour2.state(["disabled"])
        self.combo_hour3.state(["disabled"])
        self.changeStatusButton("disabled")

        self.actual = True
        self.finished = False

        if initial_timer == 0: 
            notificationSystem(
                "Selecione um timer!",
                "Você precisa selecionar um tempo para iniciar",
                3
            )
            return

        def _wait_and_start():
            if self.timer_thread and self.timer_thread.is_alive():
                self.root.after(50, _wait_and_start)
            else:
                self.timer_thread = TimerThread(initial_timer, self.thread_safe_update)
                self.timer_thread.start()
                return

        _wait_and_start()

    # reseta o timer
    def reset_timer(self):
        if self.timer_thread:
            self.timer_thread.stop()
            self.interval = False
            self.actual = False
            self.root.after(0, lambda: self.update_ui(self.initial_timer_user))
        self.end_cycle()

    # finaliza o ciclo e reseta UI
    def end_cycle(self):
        self.label_timer.config(text="00:00")

        self.combo_hour3.set("intervalo")
        self.combo_hour2.set("sessões")
        self.combo_hour.set("concentração")

        self.combo_hour.state(["!disabled"])
        self.combo_hour2.state(["!disabled"])
        self.combo_hour3.state(["!disabled"])

        self.initial_timer_user = 0
        self.number_of_sessions = 0
        self.time_interval = 0

        self.changeStatusButton("disabled")

    # altera o tempo de foco
    def timer_change(self, value):
        if value.isdigit():
            self.initial_timer_user = int(value) 
            self.update_ui(self.initial_timer_user)
        else:
            self.initial_timer_user = 0

    # altera o número de sessões
    def timer_sessions_change(self, value):
        value = int(value)
        if value > 0:
            self.number_of_sessions = value - 1

    # altera o tempo de intervalo
    def timer_interval_change(self, value):
        self.time_interval = int(value) 

    # altera o estado do botão start
    def changeStatusButton(self, state):
        self.start_button.configure(state=state)

    # notificação para início de intervalo
    def notification_interval(self, title, message, timeout):
        retorno = notification_with_click(title, message, timeout)
        if retorno:
            self.root.after(0, lambda: self.start_interval())
        else:
            self.root.after(0, lambda: self.end_cycle())

    # notificação para retorno ao foco
    def notification_focus(self, title, message, timeout):
        retorno = notification_with_click(title, message, timeout)
        if retorno:
            self.root.after(0, lambda: self.start_focus())
        else:
            self.root.after(0, lambda: self.end_cycle())

    # inicia intervalo
    def start_interval(self):
        self.interval = True
        self.start_timer(self.time_interval)

    # inicia foco
    def start_focus(self):
        self.interval = False
        self.start_timer(self.initial_timer_user)
        self.number_of_sessions -= 1


# executa o app
def main():
    root = Window(themename="solar")
    root.geometry("400x380")
    app = PomodoroApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
