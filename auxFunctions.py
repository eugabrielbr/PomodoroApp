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
        return  # Ignora se já estiver mostrando

    notificacao_ativa = True

    def worker():
        notification = ToastNotifier()
        notification.show_toast(
            title=titulo,
            msg=mensagem,
            duration=timeout,
            threaded=True,
            callback_on_click=ao_clicar
        )

        time.sleep(timeout)  # Aguarda o tempo da notificação desaparecer
        # não precisa redeclarar global aqui
        global notificacao_ativa
        notificacao_ativa = False

    # Inicia a thread
    threading.Thread(target=worker, daemon=True).start()

