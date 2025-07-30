from win10toast_click import ToastNotifier
import threading
import time
import os

notificacao_ativa = False

def format_time(seconds):
    minutes = seconds // 60
    seconds = seconds % 60
    return f"{minutes:02}:{seconds:02}"

def ao_clicar():
    print("Notificação clicada!")

def notificationSystem(titulo, mensagem, timeout):
    global notificacao_ativa

    if notificacao_ativa:
        return  # Já tem notificação ativa

    notificacao_ativa = True

    def worker():
        global notificacao_ativa
        notification = ToastNotifier()
        notification.show_toast(
            title=titulo,
            msg=mensagem,
            duration=timeout,
            threaded=True,
            callback_on_click=ao_clicar
        )
        time.sleep(timeout)
        notificacao_ativa = False

    threading.Thread(target=worker, daemon=True).start()

