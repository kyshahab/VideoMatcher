from ffpyplayer.player import MediaPlayer
import cv2
from PyQt5.QtWidgets import QWidget, QPushButton, QVBoxLayout, QLabel
from PyQt5.QtCore import QTimer, Qt 
from PyQt5.QtGui import QImage, QPixmap

class VidPlayer(QWidget):
    def __init__(self, vidpath, best_frame = 0):
        super().__init__()
        self.vidpath = vidpath
        self.best_frame = best_frame
        self.setUI()

    def setUI(self):
        self.setGeometry(100, 100, 500, 500)
        layout = QVBoxLayout()
        self.setLayout(layout)

        self.label = QLabel(self)
        self.label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.label)

        self.play_button = QPushButton('Pause/Play', self)
        self.play_button.clicked.connect(self.play_vid)
        layout.addWidget(self.play_button)

        self.reset_button = QPushButton('Reset', self)
        self.reset_button.clicked.connect(self.reset_vid)
        layout.addWidget(self.reset_button)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.next_frame)

        self.vidcap = cv2.VideoCapture(self.vidpath)
        if self.vidcap.isOpened():
            vid_fps = self.vidcap.get(cv2.CAP_PROP_POS_FRAMES)
            if vid_fps == 0:
                print("faulty fps")
                vid_fps = 30
            self.vidcap.set(cv2.CAP_PROP_POS_FRAMES, self.best_frame)
            self.player = MediaPlayer(self.vidpath, ff_opts={'sync': 'audio', 'ss': self.best_frame / self.vidcap.get(cv2.CAP_PROP_FPS)})
            self.next_frame()
            self.timer.start(int(1000/vid_fps))
        else:
            print("can't open video")
            return
        

    def play_vid(self):
        if self.timer.isActive():
            self.timer.stop()
            self.player.set_pause(True)
        else:
            self.timer.start(30)
            self.player.set_pause(False)
            
    
    def reset_vid(self):
        self.vidcap.set(cv2.CAP_PROP_POS_FRAMES, 0)
        self.player.seek(0, relative = False, accurate = True)
        self.next_frame()
        self.timer.start(int(1000/self.vidcap.get(cv2.CAP_PROP_FPS)))

    def next_frame(self):
        ret, frame = self.vidcap.read()
        if not ret:
            self.timer.stop()
            return
        try:
            audio_frame, val = self.player.get_frame()
        except Exception as e:
            print("error")
            return
        
        cur_img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        height, width, channel = cur_img.shape 
        qImg = QImage(cur_img.data, width, height, width * channel, QImage.Format_RGB888)
        self.label.setPixmap(QPixmap.fromImage(qImg))

    def close(self, event):
        self.vidcap.release()
        self.player.close_player()
        super().closeEvent(event)
        event.accept()



