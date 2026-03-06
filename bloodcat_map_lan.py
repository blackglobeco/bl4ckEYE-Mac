#!/usr/bin/python3
# @Мартин.
# ███████╗              ██╗  ██╗    ██╗  ██╗     ██████╗    ██╗  ██╗     ██╗    ██████╗
# ██╔════╝              ██║  ██║    ██║  ██║    ██╔════╝    ██║ ██╔╝    ███║    ╚════██╗
# ███████╗    █████╗    ███████║    ███████║    ██║         █████╔╝     ╚██║     █████╔╝
# ╚════██║    ╚════╝    ██╔══██║    ╚════██║    ██║         ██╔═██╗      ██║     ╚═══██╗
# ███████║              ██║  ██║         ██║    ╚██████╗    ██║  ██╗     ██║    ██████╔╝
# ╚══════╝              ╚═╝  ╚═╝         ╚═╝     ╚═════╝    ╚═╝  ╚═╝     ╚═╝    ╚═════╝
import sys
import math
import cv2
from PyQt5 import QtCore, QtGui, QtWidgets
from lib.camlib import CamLib
from lib.version import VERSION

LOGO = "\033[38;5;208m"+r'''
                                               .--.
                                               `.  \
                                                 \  \
                                                  .  \
                                                  :   .
                                                  |    .
                                                  |    :
                                                  |    |
  ..._  ___                                       |    |
 `."".`---'""--..___                              |    |
 ,-\  \             ""-...__         _____________/    |
 / ` " '                    `"""""""""                  .
 \                                                      L
 (>                                                      \
/                                                         \
\_    ___..---.                                            L
  `--'         '.                                           \
                 .                                           \_
                _/`.                                           `.._
             .'     -.                                             `.
            /     __.-Y     /''''''-...___,...--------.._            |
           /   _."    |    /                ' .      \   '---..._    |
          /   /      /    /                _,. '    ,/           |   |
          \_,'     _.'   /              /''     _,-'            _|   |
                  '     /               `-----''               /     |
                  `...-'                                       `...
[Maptnh@S-H4CK13]      [Blood Cat Map LAN '''+VERSION+''']    [https://github.com/MartinxMax]'''+"\033[0m"
 
class VideoThread(QtCore.QThread):
    frame_ready = QtCore.pyqtSignal(QtGui.QImage)

    def __init__(self, rtsp_url, width=640, height=480, parent=None, target_fps=6, max_width=640):
        super().__init__(parent)
        self.rtsp_url = rtsp_url
        self._running = True
        self.width = width
        self.height = height
        self.cap = None
        self.target_fps = target_fps
        self.max_width = max_width
        self._last_emit = 0.0

    def run(self):
        try:
            self.cap = cv2.VideoCapture(self.rtsp_url, cv2.CAP_FFMPEG)
        except Exception:
            try:
                self.cap = cv2.VideoCapture(self.rtsp_url)
            except Exception:
                self.cap = None

        try:
            self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
        except Exception:
            pass

        if not self.cap or not self.cap.isOpened():
            img = QtGui.QImage(self.width, self.height, QtGui.QImage.Format_RGB888)
            img.fill(QtGui.QColor('black'))
            painter = QtGui.QPainter(img)
            painter.setPen(QtGui.QPen(QtGui.QColor('red')))
            painter.drawText(img.rect(), QtCore.Qt.AlignCenter, 'Unable to open stream')
            painter.end()
            self.frame_ready.emit(img)
            return

        min_frame_interval = 1.0 / float(max(1, self.target_fps))
        while self._running:
            ret, frame = self.cap.read()
            if not ret or frame is None:
                self.msleep(100)
                continue

            now = QtCore.QTime.currentTime().msecsSinceStartOfDay() / 1000.0
            if (now - self._last_emit) < min_frame_interval:
                continue
            self._last_emit = now

            h, w = frame.shape[:2]
            if w > self.max_width:
                scale = self.max_width / float(w)
                new_w = int(w * scale)
                new_h = int(h * scale)
                frame = cv2.resize(frame, (new_w, new_h), interpolation=cv2.INTER_LINEAR)

            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            h, w, ch = rgb.shape
            bytes_per_line = ch * w
            qimg = QtGui.QImage(rgb.data, w, h, bytes_per_line, QtGui.QImage.Format_RGB888)
            if self.width and self.height:
                qimg = qimg.scaled(self.width, self.height, QtCore.Qt.KeepAspectRatio)
            self.frame_ready.emit(qimg)
            self.msleep(5)

        if self.cap:
            try:
                self.cap.release()
            except Exception:
                pass

    def stop(self):
        self._running = False
        self.wait()
 
class VideoWidget(QtWidgets.QLabel):
    def __init__(self, placeholder='./location/main.png', parent=None):
        super().__init__(parent)
        self.setMinimumSize(320, 240)
        self.setAlignment(QtCore.Qt.AlignCenter)
        self.setScaledContents(True)
        self.thread = None
        self.placeholder = placeholder
        self._deferred_rtsp = None
        self.set_placeholder()

    def sizeHint(self):
        return QtCore.QSize(320, 240)

    def set_placeholder(self):
        pix = QtGui.QPixmap(self.placeholder)
        if pix and not pix.isNull():
            self.setPixmap(pix.scaled(self.size(), QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation))
        else:
            img = QtGui.QImage(self.width(), self.height(), QtGui.QImage.Format_RGB32)
            img.fill(QtGui.QColor('#222'))
            p = QtGui.QPainter(img)
            p.setPen(QtGui.QPen(QtGui.QColor('#888')))
            p.drawText(img.rect(), QtCore.Qt.AlignCenter, 'No stream')
            p.end()
            self.setPixmap(QtGui.QPixmap.fromImage(img))

    @QtCore.pyqtSlot(QtGui.QImage)
    def update_frame(self, qimg: QtGui.QImage):
        self.setPixmap(QtGui.QPixmap.fromImage(qimg))

    def start_stream(self, rtsp_url=None):
        self.stop_stream()
        if rtsp_url:
            self._deferred_rtsp = None
            w = max(320, self.width())
            h = max(240, self.height())
            self.thread = VideoThread(rtsp_url, width=w, height=h)
            self.thread.frame_ready.connect(self.update_frame)
            self.thread.start()

    def lazy_start(self):
        if self._deferred_rtsp:
            self.start_stream(self._deferred_rtsp)

    def stop_stream(self):
        if self.thread:
            try:
                self.thread.stop()
            except Exception:
                pass
            self.thread = None
            self.set_placeholder()

    def closeEvent(self, event):
        self.stop_stream()
        super().closeEvent(event)

 
class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("BloodCat Map LAN Viewer @ S-H4CK13    [https://github.com/MartinxMax]")
        try:
            self.setWindowIcon(QtGui.QIcon('./location/ico.png'))
        except Exception:
            pass
        self.set_dark_theme()

        self.cam = CamLib()
        self.LOCAL_LAN_DB = './data/lan.lc'
        try:
            raw = self.cam.get_LocalDB_data(self.LOCAL_LAN_DB)
        except Exception:
            raw = []

        self.ip_map = {}
        for item in raw:
            rtsp = item.get('rtsp')
            data = item.get('data', {})
            lan = data.get('lan')
            if lan and rtsp:
                self.ip_map.setdefault(lan, []).append(rtsp)

        self.rtsp_list_all = [it.get('rtsp') for it in raw if it.get('rtsp')]

        self.setStyleSheet("""
            QWidget { background-color: #1E1E1E; color: #E6E6E6; }
            QFrame { background-color: #1A1A1A; }
            QListWidget { background-color: #121212; border:1px solid #333; color:#E6E6E6;}
            QListWidget::item { padding:6px; }
            QListWidget::item:selected { background-color:#2B5C8A; color:#FFF; }
            QListWidget::item:hover { background-color:#2A2A2A; }
            QLabel { color:#CCC; }
            QPushButton { color:#E6E6E6; background-color:#2D2D2D; border:1px solid #444; padding:6px; }
            QPushButton:hover { background-color:#3A3A3A; }
            QPushButton:pressed { background-color:#1F1F1F; }
            QPushButton:disabled { color:#777; }
        """)

        self.init_ui()
        self.showMaximized()

    def set_dark_theme(self):
        dark = QtGui.QPalette()
        dark.setColor(QtGui.QPalette.Window, QtGui.QColor(30,30,30))
        dark.setColor(QtGui.QPalette.WindowText, QtGui.QColor(220,220,220))
        dark.setColor(QtGui.QPalette.Base, QtGui.QColor(18,18,18))
        dark.setColor(QtGui.QPalette.AlternateBase, QtGui.QColor(53,53,53))
        dark.setColor(QtGui.QPalette.Text, QtGui.QColor(220,220,220))
        dark.setColor(QtGui.QPalette.Button, QtGui.QColor(45,45,45))
        dark.setColor(QtGui.QPalette.ButtonText, QtGui.QColor(230,230,230))
        dark.setColor(QtGui.QPalette.Disabled, QtGui.QPalette.ButtonText, QtGui.QColor(120,120,120))
        self.setPalette(dark)

    def init_ui(self):
        central = QtWidgets.QWidget()
        self.setCentralWidget(central)
        h = QtWidgets.QHBoxLayout(central)
        h.setContentsMargins(6,6,6,6)
        h.setSpacing(8)

 
        left_w = QtWidgets.QFrame()
        left_w.setMinimumWidth(220)
        left_layout = QtWidgets.QVBoxLayout(left_w)
        left_layout.setContentsMargins(6,6,6,6)
        left_layout.setSpacing(6)
        lbl = QtWidgets.QLabel('LAN Hosts')
        left_layout.addWidget(lbl)
        self.list_widget = QtWidgets.QListWidget()
        self.list_widget.addItems(sorted(self.ip_map.keys()))
        left_layout.addWidget(self.list_widget)
        self.reload_btn = QtWidgets.QPushButton('Reload')
        left_layout.addWidget(self.reload_btn)
        h.addWidget(left_w)

  
        self.stack = QtWidgets.QStackedWidget()
        self.stack.setMinimumWidth(640)
        ph = VideoWidget('./location/main.png')
        self.stack.addWidget(ph)
        self.single_view = VideoWidget('./location/main.png')
        self.stack.addWidget(self.single_view)

        self.grid_container = QtWidgets.QScrollArea()
        self.grid_container.setWidgetResizable(True)
        self.grid_inner = QtWidgets.QWidget()
        self.grid_layout = QtWidgets.QGridLayout(self.grid_inner)
        self.grid_layout.setSpacing(6)
        self.grid_container.setWidget(self.grid_inner)
        self.stack.addWidget(self.grid_container)
        h.addWidget(self.stack, stretch=1)

 
        right_w = QtWidgets.QFrame()
        right_w.setMinimumWidth(160)
        right_layout = QtWidgets.QVBoxLayout(right_w)
        right_layout.setContentsMargins(6,6,6,6)
        right_layout.setSpacing(6)
        auto_btn = QtWidgets.QPushButton('Auto layout all streams')
        right_layout.addWidget(auto_btn)
        stop_all_btn = QtWidgets.QPushButton('Stop all streams')
        right_layout.addWidget(stop_all_btn)
        right_layout.addStretch()
        h.addWidget(right_w)

 
        self.list_widget.itemClicked.connect(self.on_item_clicked)
        self.reload_btn.clicked.connect(self.reload_db)
        auto_btn.clicked.connect(self.on_auto_layout)
        stop_all_btn.clicked.connect(self.stop_all_streams)

 
        self.active_grid_widgets = []
        self.active_single_rtsp = None

 
    def reload_db(self):
        try:
            raw = self.cam.get_LocalDB_data(self.LOCAL_LAN_DB)
        except Exception:
            raw = []
        self.ip_map = {}
        for item in raw:
            rtsp = item.get('rtsp')
            data = item.get('data',{})
            lan = data.get('lan')
            if lan and rtsp:
                self.ip_map.setdefault(lan, []).append(rtsp)
        self.list_widget.clear()
        self.list_widget.addItems(sorted(self.ip_map.keys()))

 
    def on_item_clicked(self, item):
        ip = item.text()
        rtsps = self.ip_map.get(ip) or []
        if not rtsps:
            QtWidgets.QMessageBox.warning(self, 'No stream', f'No RTSP found for {ip}')
            return
        self.stop_all_streams()
        rtsp = rtsps[0]
        self.active_single_rtsp = rtsp
        self.single_view.start_stream(rtsp)
        self.stack.setCurrentWidget(self.single_view)

 
    def on_auto_layout(self):
        self.stop_all_streams()
        all_rtsps = list(dict.fromkeys(self.rtsp_list_all))
        if not all_rtsps:
            QtWidgets.QMessageBox.information(self,'No streams','No RTSP streams found in DB')
            return

        count = len(all_rtsps)
        cols = math.ceil(math.sqrt(count))
        rows = math.ceil(count / cols)

        while self.grid_layout.count():
            item = self.grid_layout.takeAt(0)
            w = item.widget()
            if w:
                try: w.stop_stream()
                except Exception: pass
                w.setParent(None)
                w.deleteLater()
        self.active_grid_widgets = []

        MAX_CONCURRENT = 9
        idx = 0
        started = 0
        for r in range(rows):
            for c in range(cols):
                if idx >= count:
                    spacer = QtWidgets.QWidget()
                    spacer.setMinimumSize(10,10)
                    self.grid_layout.addWidget(spacer,r,c)
                    continue
                rtsp = all_rtsps[idx]
                vw = VideoWidget()
                vw.setMinimumSize(320,240)
                vw.setSizePolicy(QtWidgets.QSizePolicy.Expanding,QtWidgets.QSizePolicy.Expanding)
                self.grid_layout.addWidget(vw,r,c)
                self.active_grid_widgets.append(vw)
                if started < MAX_CONCURRENT:
                    vw.start_stream(rtsp)
                    started +=1
                else:
                    vw._deferred_rtsp = rtsp
                idx +=1

        for c in range(cols): self.grid_layout.setColumnStretch(c,1)
        for r in range(rows): self.grid_layout.setRowStretch(r,1)
        self.grid_inner.adjustSize()
        self.stack.setCurrentWidget(self.grid_container)
 
    def stop_all_streams(self):
        try: self.single_view.stop_stream()
        except Exception: pass
        for w in self.active_grid_widgets:
            try: w.stop_stream()
            except Exception: pass
            try: w.setParent(None)
            except Exception: pass
        self.active_grid_widgets=[]
        self.stack.setCurrentIndex(0)

    def closeEvent(self,event):
        self.stop_all_streams()
        super().closeEvent(event)

 
def main():
    print(LOGO)
    app = QtWidgets.QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
