from email.policy import default
from cv2 import LineSegmentDetector
from matplotlib.pyplot import text
from vidstream import *
import tkinter as tk
import socket
import threading
import requests

# IP mode
default_ip_address = socket.gethostbyname(socket.gethostname())    #local-ip
#default_ip_address = requests.get('https://api.ipify.org').text  #public-ip
print("Default IP :", default_ip_address)



# Function
server = StreamingServer(default_ip_address, 12600)
receiver = AudioReceiver(default_ip_address, 12800)

def start_listening():
    t1 = threading.Thread(target=server.start_server)
    t2 = threading.Thread(target=receiver.start_server)
    t1.start()
    t2.start()


# GUI
window = tk.Tk()
window.title("觀眾場地")
window.geometry('300x200')

btn_listen = tk.Button(window, text="Start Listening", width=50, command=start_listening)
btn_listen.pack(anchor=tk.CENTER, expand=True)

window.mainloop()