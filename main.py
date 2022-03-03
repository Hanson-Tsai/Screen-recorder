import tkinter as tk
#import gamer
import streamer
#import audience

window = tk.Tk()
window.title("運動賽事遠距即時直播與講評")
window.geometry('300x200')

label_target_ip = tk.Label(window, text='請先選擇您的場地')
label_target_ip.pack()

#gamer_mode = tk.Button(window, text="比賽場地", width=50, command=gamer.start_listening)
#gamer_mode.pack(anchor=tk.CENTER, expand=True)

streamer_mode = tk.Button(window, text="賽評場地", width=50, command=streamer.start_camera_stream)
streamer_mode.pack(anchor=tk.CENTER, expand=True)

#audience_mode = tk.Button(window, text="觀眾場地", width=50, command=audience.start_screen_sharing)
#audience_mode.pack(anchor=tk.CENTER, expand=True)

window.mainloop()