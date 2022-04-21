import os
import time
import cv2
import threading
from datetime import datetime

DVR_LOCATION = '/dvr/'

class dvr_handler:
    def __init__(self,fps,resolution = (640, 480)):
        self.fps = fps
        self.res = resolution
        self.frame_buffer = []

    def begin(self):
        thread = threading.Thread(target=self._file_handler)
        thread.daemon = True
        thread.start()
        thread_space = threading.Thread(target=self._handle_space)
        thread_space.daemon = True
        thread_space.start()
        
    
    def _file_handler(self):
        recordtime = 60*60*6 # Create new file every 6 hours
        while True:
            now = datetime.now()
            filename = now.strftime(r"%Y%m%d_%H%M%S")
            filename = f"{DVR_LOCATION}{filename}.avi"
            self._video_save(filename,recordtime)
        
    def _video_save(self,filename,recordtime):
        fourcc = cv2.VideoWriter_fourcc(*'XVID')   # COMPRESSED
        out = cv2.VideoWriter(filename, fourcc, float(self.fps), self.res)
        _record_start = int(time.time())
        total_time_recorded = lambda : int(time.time()) - _record_start
        while total_time_recorded() < recordtime:
            try:
                if len(self.frame_buffer) > 0:
                    out.write(self.frame_buffer[0])
                    self.frame_buffer.pop(0)
                else: 
                    time.sleep(0.001)
            except:
                break
        out.release()

    def _handle_space(self):
        max_size = 3*1024*1024*1024 # Delete oldest files if total recordings are bigger than 3 GB
        while True:
            total_size = 0
            for f in os.listdir(DVR_LOCATION):
                if os.path.isfile(f"{DVR_LOCATION}{f}"):
                    total_size += os.path.getsize(f"{DVR_LOCATION}{f}")
            if total_size > max_size:   
                files = os.listdir(DVR_LOCATION)
                files.sort()
                print(files[0])
                os.remove(f"{DVR_LOCATION}{files[0]}")
            time.sleep(60)
