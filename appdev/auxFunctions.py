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
    return


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
            callback_on_click=ao_clicar,
            icon_path="C:/vscode/PomodoroApp/resources/icons/notification.ico"
        )
        
        time.sleep(timeout)
        notificacao_ativa = False

    thread = threading.Thread(target=worker, daemon=True).start()

def notification_with_click(titulo, mensagem, timeout):
    """
    Mostra uma notificação e só retorna depois que o usuário clicar.
    """
    clicou_event = threading.Event()  # cria um evento para sincronização
    timeout_click = 240
   
    def ao_clicar():
        print("Notificação clicada!")
        clicou_event.set()  # libera a espera

    notification = ToastNotifier()
    notification.show_toast(
        title=titulo,
        msg=mensagem,
        duration=timeout,
        threaded=True,
        callback_on_click=ao_clicar,
        icon_path="C:/vscode/PomodoroApp/resources/icons/notification.ico"
    )

    print("Esperando clique do usuário...")
    clicou_event.wait(timeout_click)  # bloqueia aqui até clicar ou expirar o timeout
    if not clicou_event.is_set():
        print("Tempo expirou sem clique")
        return False 
        

      
    return clicou_event.is_set()  # True se clicou, False se expirou