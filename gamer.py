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
def start_camera_stream():
    camera_client = CameraClient(text_streamer_ip.get(1.0, 'end-1c'), 10600)
    t3 = threading.Thread(target=camera_client.start_stream)
    camera_client = CameraClient(text_audience_ip.get(1.0, 'end-1c'), 12600)
    t4 = threading.Thread(target=camera_client.start_stream)
    t3.start()
    t4.start()

def start_screen_sharing():
    screen_client = ScreenShareClient(text_streamer_ip.get(1.0, 'end-1c'), 10600)
    t5 = threading.Thread(target=screen_client.start_stream)
    screen_client = ScreenShareClient(text_audience_ip.get(1.0, 'end-1c'), 12600)
    t6 = threading.Thread(target=screen_client.start_stream)
    t5.start()
    t6.start()

def start_audio_stream():
    audio_sender = AudioSender(text_streamer_ip.get(1.0, 'end-1c'), 10800)
    t7 = threading.Thread(target=audio_sender.start_stream)
    audio_sender = AudioSender(text_audience_ip.get(1.0, 'end-1c'), 12800)
    t8 = threading.Thread(target=audio_sender.start_stream)
    t7.start()
    t8.start()



# GUI
window = tk.Tk()
window.title("比賽場地")
window.geometry('300x200')

label_streamer_ip = tk.Label(window, text='Streamer IP:')
label_streamer_ip.pack()

text_streamer_ip = tk.Text(window, height=1)
text_streamer_ip.pack()

label_audience_ip = tk.Label(window, text='Audience IP:')
label_audience_ip.pack()

text_audience_ip = tk.Text(window, height=1)
text_audience_ip.pack()

btn_camera = tk.Button(window, text="Start Camera Stream", width=50, command=start_camera_stream)
btn_camera.pack(anchor=tk.CENTER, expand=True)

btn_screen = tk.Button(window, text="Start Screen Sharing", width=50, command=start_screen_sharing)
btn_screen.pack(anchor=tk.CENTER, expand=True)

btn_audio = tk.Button(window, text="Start Audio Stream", width=50, command=start_audio_stream)
btn_audio.pack(anchor=tk.CENTER, expand=True)

window.mainloop()