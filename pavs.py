from PyQt5.QtWidgets import QMainWindow, QApplication, QPushButton, QLineEdit, QFileDialog, QHBoxLayout, QLabel, QSizePolicy, QSlider, QStyle, QVBoxLayout, QWidget, QStatusBar, QTableWidget, QVBoxLayout, QTableWidgetItem, QHBoxLayout, QSplitter, QGroupBox, QFormLayout, QAction, QGridLayout, QShortcut
from PyQt5.QtMultimedia import QMediaContent, QMediaPlayer
from PyQt5.QtMultimediaWidgets import QVideoWidget
from PyQt5 import QtCore, Qt, QtGui
from PyQt5.QtCore import QRect, QSize, Qt, QUrl, QDir, QTime, pyqtSlot
from PyQt5.QtGui import QFont, QPixmap, QImage, QColor, QPainter, QPen, QKeySequence, QStandardItemModel
import os
import csv
import cv
import cv2
import sys
import numpy as np

audio_extensions = [".wav", ".mp3"]
video_extensions = [".avi", ".mp4", ".mkv"]

class Window(QMainWindow):

    def __init__(self):
        super().__init__()

        self.title = "Python Annotator for VideoS"
        # self.top = 100
        # self.left = 100
        # self.width = 300
        # self.height = 400
        # self.setWindowState = "Qt.WindowMaximized"
        iconName = "home.png"
        self.InitWindow()

    def InitWindow(self):
        self.setWindowTitle(self.title)
        # self.setWindowIcon(QtGui.QIcon(iconName))
        self.setWindowState(QtCore.Qt.WindowMaximized)

        self.UiComponents()

        self.show()

    def UiComponents(self):

        self.rowNo = 1
        self.colNo = 0

        self.model = QStandardItemModel()

        self.mediaPlayer = QMediaPlayer(None, QMediaPlayer.VideoSurface)
        self.tableWidget = QTableWidget()
        self.tableWidget.setColumnCount(4) #, Start Time, End Time, TimeStamp
        self.tableWidget.setRowCount(50)

        self.tableWidget.setItem(0, 0, QTableWidgetItem("Extra"))
        self.tableWidget.setItem(0, 1, QTableWidgetItem("Start Time"))
        self.tableWidget.setItem(0, 2, QTableWidgetItem("End Time"))
        self.tableWidget.setItem(0, 3, QTableWidgetItem("label"))

        self.videoWidget = QVideoWidget()
        self.frameID=0

        openButton = QPushButton("Open...")
        openButton.clicked.connect(self.openFile)

        self.playButton = QPushButton()
        self.playButton.setEnabled(False)
        self.playButton.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))
        self.playButton.clicked.connect(self.play)

        self.lbl = QLabel('00:00:00')
        self.lbl.setFixedWidth(60)
        self.lbl.setUpdatesEnabled(True)
        # self.lbl.setStyleSheet(stylesheet(self))

        self.elbl = QLabel('00:00:00')
        self.elbl.setFixedWidth(60)
        self.elbl.setUpdatesEnabled(True)
        # self.elbl.setStyleSheet(stylesheet(self))


        self.nextButton = QPushButton("-->")
        self.nextButton.clicked.connect(self.next)

        self.delButton = QPushButton("Delete")
        self.delButton.clicked.connect(self.delete)

        self.exportButton = QPushButton("Export")
        self.exportButton.clicked.connect(self.export)

        self.ctr = QLineEdit()
        self.ctr.setPlaceholderText("Extra")

        self.startTime = QLineEdit()
        self.startTime.setPlaceholderText("Select Start Time")

        self.endTime = QLineEdit()
        self.endTime.setPlaceholderText("Select End Time")

        self.iLabel = QLineEdit()
        self.iLabel.setPlaceholderText("Label")

        self.positionSlider = QSlider(Qt.Horizontal)
        self.positionSlider.setRange(0, 100)
        self.positionSlider.sliderMoved.connect(self.setPosition)
        self.positionSlider.sliderMoved.connect(self.handleLabel)
        self.positionSlider.setSingleStep(2)
        self.positionSlider.setPageStep(20)
        self.positionSlider.setAttribute(Qt.WA_TranslucentBackground, True)

        self.errorLabel = QLabel()
        self.errorLabel.setSizePolicy(QSizePolicy.Preferred,
                QSizePolicy.Maximum)

        # Main plotBox
        plotBox = QHBoxLayout()

        controlLayout = QHBoxLayout()
        controlLayout.setContentsMargins(0, 0, 0, 0)
        controlLayout.addWidget(openButton)
        controlLayout.addWidget(self.playButton)
        controlLayout.addWidget(self.lbl)
        controlLayout.addWidget(self.positionSlider)
        controlLayout.addWidget(self.elbl)

        wid = QWidget(self)
        self.setCentralWidget(wid)

        # Left Layout{
        # vidLayout = QVBoxLayout()
        # vidLayout.addWidget(self.videoWidget)
        # vidLayout.addLayout(self.grid_root)
        # layout.addWidget(self.videoWidget)

        layout = QVBoxLayout()
        # layout.addLayout(self.grid_root)
        layout.addWidget(self.videoWidget)
        layout.addLayout(controlLayout)
        layout.addWidget(self.errorLabel)

        plotBox.addLayout(layout, 2)
        # }

        # Right Layout {
        inputFields = QHBoxLayout()
        inputFields.addWidget(self.ctr)
        inputFields.addWidget(self.startTime)
        inputFields.addWidget(self.endTime)
        inputFields.addWidget(self.iLabel)

        feats = QHBoxLayout()
        feats.addWidget(self.nextButton)
        feats.addWidget(self.delButton)
        feats.addWidget(self.exportButton)

        layout2 = QVBoxLayout()
        layout2.addWidget(self.tableWidget)
        layout2.addLayout(inputFields, 2)
        layout2.addLayout(feats, 2)
        # layout2.addWidget(self.nextButton)
        # }

        plotBox.addLayout(layout2, 1)

        # self.setLayout(layout)
        wid.setLayout(plotBox)

        self.shortcut = QShortcut(QKeySequence("["), self)
        self.shortcut.activated.connect(self.addStartTime)
        self.shortcut = QShortcut(QKeySequence("]"), self)
        self.shortcut.activated.connect(self.addEndTime)

        self.shortcut = QShortcut(QKeySequence(Qt.Key_Right), self)
        self.shortcut.activated.connect(self.forwardSlider)
        self.shortcut = QShortcut(QKeySequence(Qt.Key_Left), self)
        self.shortcut.activated.connect(self.backSlider)
        self.shortcut = QShortcut(QKeySequence(Qt.Key_Up), self)
        self.shortcut.activated.connect(self.volumeUp)
        self.shortcut = QShortcut(QKeySequence(Qt.Key_Down), self)
        self.shortcut.activated.connect(self.volumeDown)
        self.shortcut = QShortcut(QKeySequence(Qt.ShiftModifier +  Qt.Key_Right) , self)
        self.shortcut.activated.connect(self.forwardSlider10)
        self.shortcut = QShortcut(QKeySequence(Qt.ShiftModifier +  Qt.Key_Left) , self)
        self.shortcut.activated.connect(self.backSlider10)

        self.mediaPlayer.setVideoOutput(self.videoWidget)
        self.mediaPlayer.stateChanged.connect(self.mediaStateChanged)
        self.mediaPlayer.positionChanged.connect(self.positionChanged)
        self.mediaPlayer.positionChanged.connect(self.handleLabel)
        self.mediaPlayer.durationChanged.connect(self.durationChanged)
        self.mediaPlayer.error.connect(self.handleError)

    def openFile(self):
        fileName, _ = QFileDialog.getOpenFileName(self, "Open Movie",
                QDir.homePath())

        if fileName != '':
            self.mediaPlayer.setMedia(
                    QMediaContent(QUrl.fromLocalFile(fileName)))
            self.playButton.setEnabled(True)
        self.videopath = QUrl.fromLocalFile(fileName)

    def play(self):
        # self.is_playing_video = not self.is_playing_video
        if self.mediaPlayer.state() == QMediaPlayer.PlayingState:
            self.mediaPlayer.pause()
        else:
            self.mediaPlayer.play()
            # self._play_video()
            # self.errorLabel.setText("Start: " + " -- " + " End:")

    def _play_video(self):
        if self.is_playing_video and self.video_fps:
            frame_idx = min(self.render_frame_idx+1, self.frame_count)
            print(frame_idx)

            if frame_idx == self.frame_count:
                self.on_play_video_clicked()
            else:
                self.target_frame_idx = frame_idx

    def addStartTime(self):
        self.startTime.setText(self.lbl.text())

    def addEndTime(self):
        self.endTime.setText(self.elbl.text())

    def next(self):
        self.tableWidget.setItem(self.rowNo, self.colNo, QTableWidgetItem(self.ctr.text()))
        self.colNo += 1
        self.tableWidget.setItem(self.rowNo, self.colNo, QTableWidgetItem(self.startTime.text()))
        self.colNo += 1
        self.tableWidget.setItem(self.rowNo, self.colNo, QTableWidgetItem(self.endTime.text()))
        self.colNo += 1
        self.tableWidget.setItem(self.rowNo, self.colNo, QTableWidgetItem(self.iLabel.text()))
        self.colNo = 0
        self.rowNo += 1
        # print(self.ctr.text(), self.startTime.text(), self.iLabel.text(), self.rowNo, self.colNo)
        # print("Next Clicked")

    def delete(self):
        # print("delete")
        index_list = []
        for model_index in self.tableWidget.selectionModel().selectedRows():
            index = QtCore.QPersistentModelIndex(model_index)
            index_list.append(index)

        self.rowNo = self.rowNo - len(index_list)

        for index in index_list:
            self.tableWidget.removeRow(index.row())


        # self.tableWidget.

    def export(self):
        path, _ = QFileDialog.getSaveFileName(self, 'Save File', QDir.homePath() + "/export.csv", "CSV Files(*.csv *.txt)")
        if path:
            with open(path, 'w') as stream:
                print("saving", path)
                writer = csv.writer(stream)
                # writer = csv.writer(stream, delimiter=self.delimit)
                for row in range(self.tableWidget.rowCount()):
                    rowdata = []
                    for column in range(self.tableWidget.columnCount()):
                        item = self.tableWidget.item(row+1, column)
                        if item is not None:
                            rowdata.append(item.text())
                        else:
                            rowdata.append('')
                    writer.writerow(rowdata)
        # self.isChanged = False
        # self.setCurrentFile(path)

    def mediaStateChanged(self, state):
        if self.mediaPlayer.state() == QMediaPlayer.PlayingState:
            self.playButton.setIcon(
                    self.style().standardIcon(QStyle.SP_MediaPause))
        else:
            self.playButton.setIcon(
                    self.style().standardIcon(QStyle.SP_MediaPlay))

    def positionChanged(self, position):
        self.positionSlider.setValue(position)

    def durationChanged(self, duration):
        self.positionSlider.setRange(0, duration)
        mtime = QTime(0,0,0,0)
        mtime = mtime.addMSecs(self.mediaPlayer.duration())
        self.elbl.setText(mtime.toString())

    def setPosition(self, position):
        self.mediaPlayer.setPosition(position)

    def handleError(self):
        self.playButton.setEnabled(False)
        self.errorLabel.setText("Error: " + self.mediaPlayer.errorString())

    def forwardSlider(self):
        self.mediaPlayer.setPosition(self.mediaPlayer.position() + 1*60)

    def forwardSlider10(self):
            self.mediaPlayer.setPosition(self.mediaPlayer.position() + 1000*60)

    def backSlider(self):
        self.mediaPlayer.setPosition(self.mediaPlayer.position() - 1*60)

    def backSlider10(self):
        self.mediaPlayer.setPosition(self.mediaPlayer.position() - 1000*60)

    def volumeUp(self):
        self.mediaPlayer.setVolume(self.mediaPlayer.volume() + 10)
        print("Volume: " + str(self.mediaPlayer.volume()))

    def volumeDown(self):
        self.mediaPlayer.setVolume(self.mediaPlayer.volume() - 10)
        print("Volume: " + str(self.mediaPlayer.volume()))

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton:
            self.move(event.globalPos() \
                        - QPoint(self.frameGeometry().width() / 2, \
                        self.frameGeometry().height() / 2))
            event.accept()

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.accept()
        else:
            event.ignore()

    ##################### update Label ##################################
    def handleLabel(self):
        self.lbl.clear()
        mtime = QTime(0,0,0,0)
        self.time = mtime.addMSecs(self.mediaPlayer.position())
        self.lbl.setText(self.time.toString())

    def dropEvent(self, event):
        f = str(event.mimeData().urls()[0].toLocalFile())
        self.loadFilm(f)

    def clickFile(self):
        print("File Clicked")

    def clickExit(self):
        sys.exit()

App = QApplication(sys.argv)
window = Window()
sys.exit(App.exec())