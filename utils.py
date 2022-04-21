import time
import cv2
from datetime import datetime

frame_rate_history_size = 6 # Measured in framerate measures

# Fill string with spaces until the length of the string is == size
def char_filler(item,size):
    item = str(item)
    while len(item) < size:
        item += ' '
    return item

# Calculate Framerate
def calc_fr():
    global frhistory
    global ft_end
    global ft_start
    ft_end = time.time() * 1000
    fr = round(1000/(ft_end-ft_start))
    while len(frhistory) <= frame_rate_history_size + 1:
        frhistory.append(fr)
    frhistory.pop(0)
    averagefr = 0
    for ft in frhistory:
        averagefr += ft
    averagefr = round((averagefr)/len(frhistory))
    ft_start = time.time() * 1000
    return averagefr

def add_dt_on_frame(frame):
    now = datetime.now()
    dt = str(now.strftime(r"%d/%m/%Y %H:%M:%S"))
    font = cv2.FONT_HERSHEY_SIMPLEX
    frame = cv2.putText(frame, dt,(0, 23),font, 1,(10, 255, 155),2, cv2.LINE_8)
    return frame
# Timing util
def ms(end=0):
    return round((time.time()*1000)-end)
############# VAR SET #############

#fr: Frame Rate
frhistory = []
ft_end = 0
ft_start = 0
