from ffpyplayer.player import MediaPlayer
import cv2
from PyQt5.QtWidgets import QWidget, QPushButton, QVBoxLayout, QFrame
import vlc
import sys
import time

class VidPlayer(QWidget):
    def __init__(self, vidpath, best_frame = 0):
        super().__init__()
        self.vidpath = vidpath
        self.best_frame = best_frame

        self.instance = vlc.Instance('-q')
        self.mediaplayer = self.instance.media_player_new()
        self.isPlaying = False

        self.setUI()


    def setUI(self):
        self.setGeometry(100, 100, 500, 500)
        layout = QVBoxLayout()
        self.setLayout(layout)

        if sys.platform == "darwin":  # macOS
            from PyQt5.QtWidgets import QMacCocoaViewContainer
            self.videoframe = QMacCocoaViewContainer(0)
        else:
            self.videoframe = QFrame()
        layout.addWidget(self.videoframe)

        self.play_button = QPushButton('Pause/Play', self)
        self.play_button.clicked.connect(self.play_vid)
        layout.addWidget(self.play_button)

        self.reset_button = QPushButton('Reset', self)
        self.reset_button.clicked.connect(self.reset_vid)
        layout.addWidget(self.reset_button)

        self.media = self.instance.media_new(self.vidpath)
        self.mediaplayer.set_media(self.media)

        if sys.platform == "win32":
            self.mediaplayer.set_hwnd(self.videoframe.winId())
        elif sys.platform == "darwin":
            self.mediaplayer.set_nsobject(int(self.videoframe.winId()))

        self.vidcap = cv2.VideoCapture(self.vidpath)
        if self.vidcap.isOpened():
            frames = self.vidcap.get(cv2.CAP_PROP_FRAME_COUNT)
            self.vidcap.release()
        else:
            print("can't open video")
            return

        self.mediaplayer.play()
        self.mediaplayer.set_position(self.best_frame / frames)
        time.sleep(0.02)  # show first frame
        self.mediaplayer.set_pause(1)


    def play_vid(self):
        if self.isPlaying:
            self.mediaplayer.pause()
            self.isPlaying = False
        else:
            self.mediaplayer.play()
            self.isPlaying = True


    def reset_vid(self):
        self.mediaplayer.set_position(0)


    def close(self, event):
        super().closeEvent(event)
        event.accept()
