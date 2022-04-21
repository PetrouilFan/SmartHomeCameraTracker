import imutils
import cv2
import utils
import led_controller                                   # Custom Libraries I made to control my house
import wakeonlanlib                                     # Custom Libraries I made to control my house
from dvr import dvr_handler
import time
# ( DEBUGGING ) #
showwindows = True
showonlyfinals = False
prints = True
dvr_only = False

##### ( SETTINGS ) #####

# algo settings
VIDEO_SOURCE = r'http://192.168.1.253:8080/shot.jpg'    # 0 (as int) to use the first local WebCam
max_frame_difference = 50                               # max percentage of pixels moved in frame
min_area = 300                                          # min area of contour it will be taken into account
max_area = -1                                           # max area of contour it will be taken into account (-1 for unlimited)
frame_history_size = 3                                  # how many previus frames will be used to get the dif (Must be odd)
resolution = [640,360]                                  # frame size sent from the camera, and used for calcs

# timing settings
min_valid_movement = 1500                               # minimum time (ms) that it will be needed in order to be measured as "movement" (Prevents Miss-Opens)
max_valid_no_movement = 600                             # maximum time (ms) beetween movements that it will be needed to be measured as movement reset

# Smart settings
turnoff_after = 20*60*1000                              # how much time to keep the smart switch on 

#########################

prevFrame = None
framehistory = []
lasttimeenabled = 0
smart_state = False

def smart_handler():
    global lasttimeenabled
    global smart_state
    if utils.ms(lasttimeenabled) < turnoff_after and not smart_state:
        # Enable
        led_controller.turn_on()                        # Custom libary to turn on my ledstrips
        wakeonlanlib.wake()                             # Custom libary to turn on my PC
        smart_state = True
        
    elif utils.ms(lasttimeenabled) > turnoff_after and smart_state:
        # Disable
        led_controller.turn_off()                       # Custom libary to turn off my ledstrips
        smart_state = False

dvr = dvr_handler(7)
dvr.begin()

#FirstRead
if __name__ == '__main__':
    ret, frame = cv2.VideoCapture(VIDEO_SOURCE).read()
    no_resize_frame = frame
    frame = cv2.resize(frame, (resolution[0],resolution[1]), interpolation = cv2.INTER_AREA)
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray, (21, 21), 0)
    framehistory.append(gray)

    time_since_no_movement = utils.ms()
    time_since_movement = utils.ms()
    
    while True:
        ret, frame = cv2.VideoCapture(VIDEO_SOURCE).read()
        if ret:
            no_resize_frame = frame
            frame = cv2.resize(frame, (resolution[0],resolution[1]), interpolation = cv2.INTER_AREA)
            orignal_frame = frame
            moved = False
            if frame is None:
                break
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            gray = cv2.GaussianBlur(gray, (21, 21), 0)

            while len(framehistory) < frame_history_size + 1:
                framehistory.append(gray)
            framehistory.pop(0)
            prevFrame = framehistory[0] 
            for x in range(1,frame_history_size):
                prevFrame = cv2.absdiff(prevFrame, framehistory[x])
            frameDelta = cv2.absdiff(prevFrame, gray)
            thresh = cv2.threshold(frameDelta, 25, 255, cv2.THRESH_BINARY)[1]
            thresh = cv2.dilate(thresh, None, iterations=2)
            cnts = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL,
                cv2.CHAIN_APPROX_SIMPLE)
            cnts = imutils.grab_contours(cnts)
            totalarea = 0
            for c in cnts:
                if (cv2.contourArea(c) < min_area or (max_area>0 and (cv2.contourArea(c) > max_area))):
                    continue
                totalarea += cv2.contourArea(c)
                (x, y, w, h) = cv2.boundingRect(c)
                if showwindows:
                    cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                moved = True
            if not dvr_only:
                smart_handler()

            if (utils.ms(time_since_no_movement)>min_valid_movement):
                print("Lights: On ",end="   ")
                lasttimeenabled = utils.ms()
            else:
                print("Lights: Off",end="   ")

            if moved:
                dvr.frame_buffer.append(utils.add_dt_on_frame(no_resize_frame))
                time_since_movement = utils.ms()    
            else:
                if utils.ms(time_since_movement)>max_valid_no_movement:
                    time_since_no_movement = utils.ms()
            
            ############ ( DEBUGING ) ############
            if showwindows:
                if not moved:
                    cv2.putText(frame, "Moving: No ", (10, 20),cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
                else:
                    cv2.putText(frame, "Moving: Yes", (10, 20),cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
                if not showonlyfinals:
                    cv2.imshow("Thresh", thresh)
                    cv2.imshow("Frame Delta", frameDelta)
                cv2.imshow("Final", frame)
                key = cv2.waitKey(1) & 0xFF
                if key == ord("q"):
                    break
            if prints:
                print("Movement: ", utils.char_filler(moved, 5),end="   ")
                print("Dif %: ", utils.char_filler(round(totalarea/(resolution[0]*resolution[1])*100,1),4),end="   ")   
                print('FPS: ',utils.calc_fr(),end="   \r")
        else:
            print("No connected camera",end='\r')
        #####################################
        time.sleep(0.02)

    if showwindows:
        cv2.destroyAllWindows()
