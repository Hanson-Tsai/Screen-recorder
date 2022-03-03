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
server = StreamingServer(default_ip_address, 10600)
receiver = AudioReceiver(default_ip_address, 10800)

def start_listening():
    t1 = threading.Thread(target=server.start_server)
    t2 = threading.Thread(target=receiver.start_server)
    t1.start()
    t2.start()

def start_camera_stream():
    camera_client = CameraClient(text_audience_ip.get(1.0, 'end-1c'), 12600)
    t3 = threading.Thread(target=camera_client.start_stream)
    t3.start()

def start_screen_sharing():
    screen_client = ScreenShareClient(text_audience_ip.get(1.0, 'end-1c'), 12600)
    t4 = threading.Thread(target=screen_client.start_stream)
    t4.start()

def start_audio_stream():
    audio_sender = AudioSender(text_audience_ip.get(1.0, 'end-1c'), 12800)
    t5 = threading.Thread(target=audio_sender.start_stream)
    t5.start()



# GUI
window = tk.Tk()
window.title("賽評場地")
window.geometry('300x200')

label_audience_ip = tk.Label(window, text='Audience IP:')
label_audience_ip.pack()

text_audience_ip = tk.Text(window, height=1)
text_audience_ip.pack()

btn_listen = tk.Button(window, text="Start Listening", width=50, command=start_listening)
btn_listen.pack(anchor=tk.CENTER, expand=True)

btn_camera = tk.Button(window, text="Start Camera Stream", width=50, command=start_camera_stream)
btn_camera.pack(anchor=tk.CENTER, expand=True)

btn_screen = tk.Button(window, text="Start Screen Sharing", width=50, command=start_screen_sharing)
btn_screen.pack(anchor=tk.CENTER, expand=True)

btn_audio = tk.Button(window, text="Start Audio Stream", width=50, command=start_audio_stream)
btn_audio.pack(anchor=tk.CENTER, expand=True)

window.mainloop()