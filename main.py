import cv2 as cv
import pyautogui
import numpy as np
import keyboard
import time



# Screen size info
left_top_x, left_top_y, left_down_x, left_down_y, right_top_x, right_top_y = 0, 0, 0, 0, 0, 0



def Adjust_screen_size():
    global left_top_x, left_top_y, left_down_x, left_down_y, right_top_x, right_top_y
    pyautogui.alert(text='移動鼠標到指定位置後，按下Ctrl，紀錄錄影視窗大小 (順序為，左上、左下、右上)', title='設定錄影視窗大小', button='OK')
    
    print('Left Top')
    while not keyboard.is_pressed('ctrl'):
        left_top_x, left_top_y = pyautogui.position()
    time.sleep(0.5)
    
    print('Left Down')
    while not keyboard.is_pressed('ctrl'):
        left_down_x, left_down_y = pyautogui.position()
    time.sleep(0.5)

    print('Right Top')
    while not keyboard.is_pressed('ctrl'):
        right_top_x, right_top_y = pyautogui.position()
    time.sleep(0.5)

    screen_x = int(right_top_x) - int(left_top_x)
    screen_y = int(left_down_y) - int(left_top_y)

    return screen_x, screen_y



def Recording(screen_x, screen_y):
    global left_top_x, left_top_y, left_down_x, left_down_y, right_top_x, right_top_y

    print("--- Recording")
    tmp_video = []
    frame_number = 0


    time_start = time.time()
    while True:
        #click screen shot
        screen_shot_img = pyautogui.screenshot()

        #convert into array
        frame = np.array(screen_shot_img)
        #change from BGR to RGB
        frame = cv.cvtColor(frame, cv.COLOR_BGR2RGB)
        
        tmp_video.append(frame[left_top_y:(left_top_y+screen_y), left_top_x:(left_top_x+screen_x), :])
        frame_number = frame_number + 1     

        if keyboard.is_pressed('ctrl'):
            break
    time_end = time.time()

    print('--- End Recording')
    cv.destroyAllWindows()

    frame_delay = round(frame_number / (time_end - time_start))
    #print(frame_delay)

    return tmp_video, frame_delay



def Replaying(tmp_video, frame_delay):

    print('--- Replaying')
    
    for frame in tmp_video:
        cv.imshow("Replay", frame)
        cv.waitKey(frame_delay)
        if keyboard.is_pressed('ctrl'):
            break
    
    cv.destroyAllWindows()



def Saving(tmp_video, frame_delay, screen_x, screen_y):
    fourcc = cv.VideoWriter_fourcc(*'XVID')
    video = cv.VideoWriter('test.avi', fourcc, 25, (screen_x, screen_y))
    for frame in tmp_video:
        video.write(frame)



if __name__== "__main__":

    screen_x, screen_y = Adjust_screen_size()

    while screen_x < 0 | screen_y < 0:
        print('Setting screen size error')
        screen_x, screen_y = Adjust_screen_size()

    while True:

        buttom_state = pyautogui.confirm(text='請選擇功能', title='運動賽事遠距即時直播與講評', buttons=['Record', 'Replay', 'Save', 'End'])

        if buttom_state == 'Record':
            tmp_video, frame_delay = Recording(screen_x, screen_y)

        elif buttom_state == 'Replay':
            # check whether you have record yet
            if tmp_video:
                Replaying(tmp_video, frame_delay)
            else:
                buttom_state = pyautogui.confirm(text='請先進行錄影', title='運動賽事遠距即時直播與講評', buttons=['Record', 'Replay', 'Save', 'End'])

        elif buttom_state == 'Save':
            if tmp_video:
                Saving(tmp_video, frame_delay, screen_x, screen_y)
            else:
                buttom_state = pyautogui.confirm(text='請先進行錄影', title='運動賽事遠距即時直播與講評', buttons=['Record', 'Replay', 'Save', 'End'])

        else:
            break