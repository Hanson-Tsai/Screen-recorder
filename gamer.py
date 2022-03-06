import tkinter as tk
import socket
import threading
import requests
import cv2
import pyautogui
import numpy as np
import pickle
import struct
import pyaudio

# IP mode
default_ip_address = socket.gethostbyname(socket.gethostname())    #local-ip
#default_ip_address = requests.get('https://api.ipify.org').text  #public-ip
print("Default IP :", default_ip_address)



class StreamingClient:
    """
    Abstract class for the generic streaming client.
    Attributes
    ----------
    Private:
        __host : str
            host address to connect to
        __port : int
            port to connect to
        __running : bool
            inicates if the client is already streaming or not
        __encoding_parameters : list
            a list of encoding parameters for OpenCV
        __client_socket : socket
            the main client socket
    Methods
    -------
    Private:
        __client_streaming : main method for streaming the client data
    Protected:
        _configure : sets basic configurations (overridden by child classes)
        _get_frame : returns the frame to be sent to the server (overridden by child classes)
        _cleanup : cleans up all the resources and closes everything
    Public:
        start_stream : starts the client stream in a new thread
    """

    def __init__(self, host1, host2, port1, port2):
        """
        Creates a new instance of StreamingClient.
        Parameters
        ----------
        host : str
            host address to connect to
        port : int
            port to connect to
        """
        self.__host1 = host1
        self.__port1 = port1
        self.__host2 = host2
        self.__port2 = port2
        self._configure()
        self.__running = False
        self.__client_socket1 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.__client_socket2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def _configure(self):
        """
        Basic configuration function.
        """
        self.__encoding_parameters = [int(cv2.IMWRITE_JPEG_QUALITY), 90]

    def _get_frame(self):
        """
        Basic function for getting the next frame.
        Returns
        -------
        frame : the next frame to be processed (default = None)
        """
        return None

    def _cleanup(self):
        """
        Cleans up resources and closes everything.
        """
        cv2.destroyAllWindows()

    def __client_streaming(self):
        """
        Main method for streaming the client data.
        """
        self.__client_socket1.connect((self.__host1, self.__port1))
        self.__client_socket2.connect((self.__host2, self.__port2))
        while self.__running:
            frame = self._get_frame()
            result, frame = cv2.imencode('.jpg', frame, self.__encoding_parameters)
            data = pickle.dumps(frame, 0)
            size = len(data)

            try:
                self.__client_socket1.sendall(struct.pack('>L', size) + data)
                self.__client_socket2.sendall(struct.pack('>L', size) + data)
            except ConnectionResetError:
                self.__running = False
            except ConnectionAbortedError:
                self.__running = False
            except BrokenPipeError:
                self.__running = False

        self._cleanup()

    def start_stream(self):
        """
        Starts client stream if it is not already running.
        """

        if self.__running:
            print("Client is already streaming!")
        else:
            self.__running = True
            client_thread = threading.Thread(target=self.__client_streaming)
            client_thread.start()

    def stop_stream(self):
        """
        Stops client stream if running
        """
        if self.__running:
            self.__running = False
        else:
            print("Client not streaming!")



class CameraClient(StreamingClient):
    """
    Class for the camera streaming client.
    Attributes
    ----------
    Private:
        __host : str
            host address to connect to
        __port : int
            port to connect to
        __running : bool
            inicates if the client is already streaming or not
        __encoding_parameters : list
            a list of encoding parameters for OpenCV
        __client_socket : socket
            the main client socket
        __camera : VideoCapture
            the camera object
        __x_res : int
            the x resolution
        __y_res : int
            the y resolution
    Methods
    -------
    Protected:
        _configure : sets basic configurations
        _get_frame : returns the camera frame to be sent to the server
        _cleanup : cleans up all the resources and closes everything
    Public:
        start_stream : starts the camera stream in a new thread
    """

    def __init__(self, host1, host2, port1, port2, x_res=1024, y_res=576):
        """
        Creates a new instance of CameraClient.
        Parameters
        ----------
        host : str
            host address to connect to
        port : int
            port to connect to
        x_res : int
            the x resolution
        y_res : int
            the y resolution
        """
        self.__x_res = x_res
        self.__y_res = y_res
        self.__camera = cv2.VideoCapture(0)
        super(CameraClient, self).__init__(host1, host2, port1, port2)

    def _configure(self):
        """
        Sets the camera resultion and the encoding parameters.
        """
        self.__camera.set(3, self.__x_res)
        self.__camera.set(4, self.__y_res)
        super(CameraClient, self)._configure()

    def _get_frame(self):
        """
        Gets the next camera frame.
        Returns
        -------
        frame : the next camera frame to be processed
        """
        ret, frame = self.__camera.read()
        return frame

    def _cleanup(self):
        """
        Cleans up resources and closes everything.
        """
        self.__camera.release()
        cv2.destroyAllWindows()



class ScreenShareClient(StreamingClient):
    """
    Class for the screen share streaming client.
    Attributes
    ----------
    Private:
        __host : str
            host address to connect to
        __port : int
            port to connect to
        __running : bool
            inicates if the client is already streaming or not
        __encoding_parameters : list
            a list of encoding parameters for OpenCV
        __client_socket : socket
            the main client socket
        __x_res : int
            the x resolution
        __y_res : int
            the y resolution
    Methods
    -------
    Protected:
        _get_frame : returns the screenshot frame to be sent to the server
    Public:
        start_stream : starts the screen sharing stream in a new thread
    """

    def __init__(self, host1, host2, port1, port2, x_res=1024, y_res=576):
        """
        Creates a new instance of ScreenShareClient.
        Parameters
        ----------
        host : str
            host address to connect to
        port : int
            port to connect to
        x_res : int
            the x resolution
        y_res : int
            the y resolution
        """
        self.__x_res = x_res
        self.__y_res = y_res
        super(ScreenShareClient, self).__init__(host1, host2, port1, port2)

    def _get_frame(self):
        """
        Gets the next screenshot.
        Returns
        -------
        frame : the next screenshot frame to be processed
        """
        screen = pyautogui.screenshot()
        frame = np.array(screen)
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame = cv2.resize(frame, (self.__x_res, self.__y_res), interpolation=cv2.INTER_AREA)
        return frame



class AudioReceiver:

    def __init__(self, host, port, slots=8, audio_format=pyaudio.paInt16, channels=1, rate=44100, frame_chunk=4096):
        self.__host = host
        self.__port = port

        self.__slots = slots
        self.__used_slots = 0

        self.__audio_format = audio_format
        self.__channels = channels
        self.__rate = rate
        self.__frame_chunk = frame_chunk

        self.__audio = pyaudio.PyAudio()

        self.__server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.__server_socket.bind((self.__host, self.__port))

        self.__block = threading.Lock()
        self.__running = False

    def start_server(self):
        if self.__running:
            print("Audio server is running already")
        else:
            self.__running = True
            self.__stream = self.__audio.open(format=self.__audio_format, channels=self.__channels, rate=self.__rate, output=True, frames_per_buffer=self.__frame_chunk)
            thread = threading.Thread(target=self.__server_listening)
            thread.start()

    def __server_listening(self):
        self.__server_socket.listen()
        while self.__running:
            self.__block.acquire()
            connection, address = self.__server_socket.accept()
            if self.__used_slots >= self.__slots:
                print("Connection refused! No free slots!")
                connection.close()
                self.__block.release()
                continue
            else:
                self.__used_slots += 1

            self.__block.release()
            thread = threading.Thread(target=self.__client_connection, args=(connection, address,))
            thread.start()

    def __client_connection(self, connection, address):
        while self.__running:
            data = connection.recv(self.__frame_chunk)
            self.__stream.write(data)

    def stop_server(self):
        if self.__running:
            self.__running = False
            closing_connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            closing_connection.connect((self.__host, self.__port))
            closing_connection.close()
            self.__block.acquire()
            self.__server_socket.close()
            self.__block.release()
        else:
            print("Server not running!")



class AudioSender:

    def __init__(self, host1, host2, port1, port2, audio_format=pyaudio.paInt16, channels=1, rate=44100, frame_chunk=4096):
        self.__host1 = host1
        self.__port1 = port1
        self.__host2 = host2
        self.__port2 = port2

        self.__audio_format = audio_format
        self.__channels = channels
        self.__rate = rate
        self.__frame_chunk = frame_chunk

        self.__sending_socket1 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.__sending_socket2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.__audio = pyaudio.PyAudio()

        self.__running = False

    #
    # def __callback(self, in_data, frame_count, time_info, status):
    #     if self.__running:
    #         self.__sending_socket.send(in_data)
    #         return (None, pyaudio.paContinue)
    #     else:
    #         try:
    #             self.__stream.stop_stream()
    #             self.__stream.close()
    #             self.__audio.terminate()
    #             self.__sending_socket.close()
    #         except OSError:
    #             pass # Dirty Solution For Now (Read Overflow)
    #         return (None, pyaudio.paComplete)

    def start_stream(self):
        if self.__running:
            print("Already streaming")
        else:
            self.__running = True
            thread = threading.Thread(target=self.__client_streaming)
            thread.start()

    def stop_stream(self):
        if self.__running:
            self.__running = False
        else:
            print("Client not streaming")

    def __client_streaming(self):
        self.__sending_socket1.connect((self.__host1, self.__port1))
        self.__sending_socket2.connect((self.__host2, self.__port2))
        self.__stream = self.__audio.open(format=self.__audio_format, channels=self.__channels, rate=self.__rate, input=True, frames_per_buffer=self.__frame_chunk)
        while self.__running:
            self.__sending_socket1.send(self.__stream.read(self.__frame_chunk))
            self.__sending_socket2.send(self.__stream.read(self.__frame_chunk))



# Function
def start_camera_stream():
    camera_client = CameraClient(text_streamer_ip.get(1.0, 'end-1c'), text_audience_ip.get(1.0, 'end-1c'), 10600, 12600)
    t1 = threading.Thread(target=camera_client.start_stream)
    t1.start()

def start_screen_sharing():
    screen_client = ScreenShareClient(text_streamer_ip.get(1.0, 'end-1c'), text_audience_ip.get(1.0, 'end-1c'), 10600, 12600)
    t2 = threading.Thread(target=screen_client.start_stream)
    t2.start()

def start_audio_stream():
    audio_sender = AudioSender(text_streamer_ip.get(1.0, 'end-1c'), text_audience_ip.get(1.0, 'end-1c'), 10800, 12800)
    #audio_sender = AudioSender(text_audience_ip.get(1.0, 'end-1c'), 12800)
    t3 = threading.Thread(target=audio_sender.start_stream)
    t3.start()



receiver = AudioReceiver(default_ip_address, 8888)

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