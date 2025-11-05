from win10toast_click import ToastNotifier
import threading
import time
import os

notificacao_ativa = False

# Formata o tempo no formato mm:ss
def format_time(seconds):
    minutes = seconds // 60
    seconds = seconds % 60
    return f"{minutes:02}:{seconds:02}"

# Função chamada ao clicar na notificação
def ao_clicar():
    print("Notificação clicada!")
    # Aqui você pode abrir o app, iniciar um novo pomodoro etc.
    return

# Mostra uma notificação simples
def notificationSystem(titulo, mensagem, timeout):
    global notificacao_ativa

    if notificacao_ativa:
        return  # já tem notificação ativa

    notificacao_ativa = True

    def worker():
        global notificacao_ativa
        toaster = ToastNotifier()
        toaster.show_toast(
            title=titulo,
            msg=mensagem,
            icon_path="C:/vscode/PomodoroApp/resources/icons/notification.ico",
            duration=timeout,
            threaded=True,
            callback_on_click=ao_clicar
        )
        # Espera até o tempo acabar
        time.sleep(timeout)
        notificacao_ativa = False

    threading.Thread(target=worker, daemon=True).start()

# Mostra uma notificação e espera clique ou timeout
def notification_with_click(titulo, mensagem, timeout):
    clicou_event = threading.Event()
    timeout_click = 240

    def ao_clicar_interno():
        print("Notificação clicada!")
        clicou_event.set()

    toaster = ToastNotifier()
    toaster.show_toast(
        title=titulo,
        msg=mensagem,
        icon_path="C:/vscode/PomodoroApp/resources/icons/notification.ico",
        duration=timeout,
        threaded=True,
        callback_on_click=ao_clicar_interno
    )

    print("Esperando clique do usuário...")
    clicou_event.wait(timeout_click)
    if not clicou_event.is_set():
        print("Tempo expirou sem clique")
        return False

    return clicou_event.is_set()
