import sys, json, os
from PyQt5.QtWidgets import *
from PyQt5 import uic
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import time
import fnmatch
import cv2
import json
from ui_main import Ui_MainWindow
import threading
import numpy as np
from alpr import detect_plate
from highway import detect_highway


class MyLineEdit(QLineEdit):
    def __init__(self, parent, text):
        super().__init__(text, parent)
    def labelTypeChanged(self):
        names = []
        for i in window.num_relation:
            if self.objectName() != 'mTitleLine_' + str(i):
                names.append(window.findChild(MyLineEdit, 'mTitleLine_' + str(i)).text())
        if self.text() in names:
            self.setText(self.text()[:-1])

class MyButton(QPushButton):
    def __init__(self, parent, text):
        super().__init__(text, parent)
    def pressedBtn(self):
        index = int(self.objectName().split('_')[1])
        tempWgt = window.findChild(QWidget, 'mRWdt_' + str(index))
        tempWgt.deleteLater()
        del window.num_relation[window.num_relation.index(index)]

class MyDrawWidget(QLabel):
    def __init__(self, selectedType):
        super().__init__()

        self.setMouseTracking(True)
        self.pos = None
        self.firstPos = None
        self.secondPos = None

    def mouseMoveEvent(self, event):
        if not window.image:
            return
        if window.mStart.text() == "Stop":
            return
        self.pos = event.pos()
        self.update()
    
    def mousePressEvent(self, event):
        if not window.image:
            return
        if window.mStart.text() == "Stop":
            return
        if not self.firstPos:
            if window.mSelectLine.currentIndex() == 3 or window.mSelectLine.currentIndex() == 4:
                if len(window.lines) > 1:
                    return
            self.firstPos = (event.pos().x()/self.rect().width(), event.pos().y()/self.rect().height())
        else:
            self.secondPos = (event.pos().x()/self.rect().width(), event.pos().y()/self.rect().height())
            window.lines.append((self.firstPos, self.secondPos))
            item = QListWidgetItem("New Line " + str(len(window.lines)))
            window.mLineList.addItem(item)
            try:
                for i in range(1, window.num_relation+1):
                    tempWgt = window.findChild(QComboBox, 'mBox1_' + str(i))
                    tempWgt.addItem("New Line " + str(len(window.lines)))
                    tempWgt = window.findChild(QComboBox, 'mBox2_' + str(i))
                    tempWgt.addItem("New Line " + str(len(window.lines)))
            except:
                pass

            self.firstPos = None
            self.secondPos = None
        self.update()

    def paintEvent(self, event):
        if not window.image:
            return
        painter = QPainter(self)
        painter.drawImage(self.rect(), window.image)

        if window.mStart.text() == "Stop":
            return
        for line in window.lines:
            painter.setPen(QPen(QColor(255, 0, 0), 2))
            painter.drawLine(round(line[1][0]*self.rect().width()), round(line[1][1]*self.rect().height()), round(line[0][0]*self.rect().width()), round(line[0][1]*self.rect().height()))           
            painter.setFont(QFont('Helvetica [Cronyx]', 15))
            text = window.mLineList.item(window.lines.index(line)).text()
            painter.drawText(round((line[1][0]*self.rect().width() + line[0][0]*self.rect().width())/2), round((line[1][1]*self.rect().height() + line[0][1]*self.rect().height())/2), text)

        if window.mSelectLine.currentIndex() == 3:
            if len(window.lines) > 1:
                return
        if window.mSelectLine.currentIndex() == 4:
            if window.mLPRROI1.isChecked():
                if len(window.lines) > 1:
                    return
            else:
                return
        painter.setPen(QPen(QColor(255, 0, 0), 2))

        if not self.firstPos:
            pass
        elif not self.secondPos:
            painter.drawLine(self.pos.x(), self.pos.y(), round(self.firstPos[0]*self.rect().width()), round(self.firstPos[1]*self.rect().height()))
        else:
            painter.drawLine(round(self.secondPos[0]*self.rect().width()), round(self.secondPos[1]*self.rect().height()), round(self.firstPos[0]*self.rect().width()), round(self.firstPos[1]*self.rect().height()))        

class WorkerThread(QThread):
    progress = pyqtSignal(int)
    detectImage = pyqtSignal(np.ndarray)
    showResult = pyqtSignal(dict)
    def __init__(self, index, source, filename, output, webcam, lines, linestext, save_video):
        QThread.__init__(self)
        self.index = index
        self.source = source
        self.filename = filename
        self.output = output
        self.webcam = webcam
        self.lines = lines
        self.linestext = linestext
        self.save_video = save_video
    def run(self):
        if self.index == 1:
            detect_highway(self.source, self.filename, self.output, self.webcam, self.lines, self.linestext, self.progress, self.detectImage, self.showResult, self.save_video)
        elif self.index == 4:
            detect_plate(self.source, self.filename, self.output, self.webcam, self.lines, self.linestext, self.progress, self.detectImage, self.showResult, self.save_video)

class MyWindow(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        self.showMaximized()
        

        self.setWindowTitle("TRAFFIC ANALYZER")

        self.lines = []
        self.image = None

        self.mDrawWidget = MyDrawWidget(0)
        self.mDrawLayout.addWidget(self.mDrawWidget)

        self.dir_path1 = ""
        self.dir_path2 = ""

        self.num_relation = []

        self.mLPRROI1.hide()
        self.mLPRROI2.hide()
        self.mResultTable.hide()

        self.mSelectLine.currentIndexChanged.connect(self.changedROI)

        self.mLineList.setContextMenuPolicy(Qt.CustomContextMenu)
        self.mLineList.customContextMenuRequested.connect(self.showLineListContextMenu)

        self.mLineList.itemDoubleClicked.connect(self.editLineName)
        self.mLineList.itemChanged.connect(self.changeLineList)

        self.mFileList1.itemClicked.connect(self.showFrame)

        self.mRadioVideo.pressed.connect(self.pressedVideo)
        self.mRadioCamera.pressed.connect(self.pressedCamera)

        self.mLPRROI2.pressed.connect(self.pressedROI2)

        self.mOpenBtn1.clicked.connect(self.openDir1)
        # self.mOpenBtn2.clicked.connect(self.openDir2)
        self.mLoadROI.clicked.connect(self.loadROI)
        self.mSaveROI.clicked.connect(self.saveROI)
        self.mAddR.clicked.connect(self.addRelation)
        self.mDelR.clicked.connect(self.deleteRelation)
        self.mStart.clicked.connect(self.startProcess)

        self.mProgressBar.setRange(0, 1000)

    def keyPressEvent(self, event):
        pass

    def pressedVideo(self):
        if self.mRadioVideo.isChecked():
            return
        self.mTypeLabel.setText("Dir path::")
        self.mOpenLine1.clear()
        self.mOpenLine1.setReadOnly(True)
        self.mOpenBtn1.setText("Open")
        self.mFileList1.clear()
        self.image = None
        self.changedROI(self.mSelectLine.currentIndex())

    def pressedCamera(self):
        if self.mRadioCamera.isChecked():
            return
        self.mTypeLabel.setText("URL:")
        self.mOpenLine1.clear()
        self.mOpenLine1.setReadOnly(False)
        self.mOpenBtn1.setText("Add")
        self.mFileList1.clear()
        self.image = None
        self.changedROI(self.mSelectLine.currentIndex())

    def pressedROI2(self):
        self.lines.clear()
        self.mLineList.clear()
        self.mDrawWidget.update()

    def drawText(self, event, qp):
        qp.setPen(QColor(168, 34, 3))
        qp.setFont(QFont('Decorative', 10))
        qp.drawText(event.rect(), Qt.AlignCenter, self.text)

    def editLineName(self, item):
        item.setFlags(item.flags() | Qt.ItemIsEditable)
        self.mLineList.editItem(item)

    def changeLineList(self, item):
        index = self.mLineList.row(item)
        names = []
        for i in range(len(self.lines)):
            if index != i:
                names.append(self.mLineList.item(i).text())
        if item.text() in names:
            item.setText(item.text()+'_1')
        try:
            for i in self.num_relation:
                tempWgt = self.findChild(QComboBox, 'mBox1_' + str(i))
                tempWgt.setItemText(index, item.text())
                tempWgt = self.findChild(QComboBox, 'mBox2_' + str(i))
                tempWgt.setItemText(index, item.text())
        except:
            pass
        self.mDrawWidget.update()

    def showLineListContextMenu(self, pos):
        globalPos = self.mLineList.mapToGlobal(pos)
        myMenu = QMenu(self)
        act_delete = myMenu.addAction("Delete")
        act_delete.triggered.connect(self.deleteLineItem)
        myMenu.exec(globalPos)

    def deleteLineItem(self):
        if len(self.lines) == 0:
            return
        index = self.mLineList.currentRow()
        self.mLineList.removeItemWidget(self.mLineList.takeItem(index))
        del self.lines[index]
        self.mDrawWidget.update()
        try:
            for i in self.num_relation:
                tempWgt = self.findChild(QComboBox, 'mBox1_' + str(i))
                tempWgt.removeItem(index)
                tempWgt = self.findChild(QComboBox, 'mBox2_' + str(i))
                tempWgt.removeItem(index)
        except:
            pass

    def closeEvent(self, event):
        reply = QMessageBox.question(self, 'Window Close', 'Are you sure you want to close the window?', QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

        if reply == QMessageBox.Yes:
            pass
        else:
            event.ignore()

    def openDir1(self):
        if self.mRadioVideo.isChecked():
            self.dir_path1 = QFileDialog.getExistingDirectory(self,"Choose Directory","")
            if self.dir_path1 != "":
                filelist = []
                typelist = ['.mp4', '.avi', 'mov', 'mpg', 'MP4', '.AVI', '.MOV', '.MPG', '.asf', '.ASF']
                for file in os.listdir(self.dir_path1):
                    if file[-4:] in typelist:
                        filelist.append(file)
                self.mFileList1.clear()
                self.mFileList1.addItems(filelist)
            
            if self.mFileList1.count() > 0:
                self.mOpenLine1.setText(self.dir_path1)
                self.capture = cv2.VideoCapture(self.dir_path1 + '/' + self.mFileList1.item(0).text())
                ret, frame = self.capture.read()
                if ret:
                    rgbImage = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    h, w, ch = rgbImage.shape
                    bytesPerLine = ch * w
                    self.image = QImage(rgbImage.data, w, h, bytesPerLine, QImage.Format_RGB888)
                    self.lines.clear()
                    self.mLineList.clear()
                    self.mDrawWidget.update()
                self.capture.release()
                self.changedROI(self.mSelectLine.currentIndex())
                self.mFileList1.setCurrentRow(0)
        else:
            url = self.mOpenLine1.text()
            try:
                self.capture = cv2.VideoCapture(url)
                ret, frame = self.capture.read()
            except:
                QMessageBox.warning(self, 'Warning', "Can't open this stream.")
                self.capture.release()
                return
            if not ret:
                QMessageBox.warning(self, 'Warning', "Can't open this stream.")
                self.capture.release()
                return
            rgbImage = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            h, w, ch = rgbImage.shape
            bytesPerLine = ch * w
            self.image = QImage(rgbImage.data, w, h, bytesPerLine, QImage.Format_RGB888)
            self.lines.clear()
            self.mLineList.clear()
            self.mDrawWidget.update()
            self.capture.release()
            self.mFileList1.addItem(url)
            self.changedROI(self.mSelectLine.currentIndex())

    def loadROI(self):
        file_path = QFileDialog.getOpenFileName(self, "Load PRM file", "", "prm file (*.prm)")
        if file_path[0] != "":
            file = open(file_path[0], 'r')
            data = json.load(file)
            file.close()
            self.restore(data)

    def saveROI(self):
        index = self.mSelectLine.currentIndex()
        if len(self.lines) == 0:
            if index != 4 or self.mLPRROI1.isChecked():
                QMessageBox.warning(self, 'Warning', 'There is no line')
                return

        dictionary = {
            'type' : None,
            'source' : {
                'type' : None,
                'path' : None,
            },
            'lines' : {},
        }

        dictionary['type'] = self.mSelectLine.currentText()

        if self.mRadioVideo.isChecked():
            dictionary['source']['type'] = 'video'
        else:
            dictionary['source']['type'] = 'camera'
        dictionary['source']['path'] = self.mOpenLine1.text()

        if index != 4:
            dictionary['save_interval'] = self.mTimeInterval.value()
    
        for i in range(len(self.lines)):
            dictionary['lines'][self.mLineList.item(i).text()] = self.lines[i]


        if index in [0, 2]:
            if len(self.num_relation) == 0:
                QMessageBox.warning(self, "Warning", "There is no label.")
                return
            dictionary['labels'] = {}
            labels = []
            for i in self.num_relation:
                label = {}
                if index == 0:
                    label['type'] = 'vehicle' if self.findChild(QRadioButton, 'mRadioV_' + str(i)).isChecked() else 'ped & bic'
                name = self.findChild(MyLineEdit, 'mTitleLine_' + str(i)).text()
                label['from'] = self.findChild(QComboBox, 'mBox1_' + str(i)).currentText()
                label['to'] = self.findChild(QComboBox, 'mBox2_' + str(i)).currentText()
                dictionary['labels'][name] = label
        
        # file_path = QFileDialog.getSaveFileName(self, "Save PRM file", "", "prm file (*.prm)")
        # if file_path[0] != "":
        for i in range(self.mFileList1.count()):
            text = self.mFileList1.item(i).text()
            extension = text.split('.')[-1]
            file = open(self.dir_path1 + '/' + text.replace(extension, 'prm'), 'w')
            json.dump(dictionary, file)
            file.close()

    def restore(self, data):
        list = ['Junction', 'Highway', 'Ped & Bicycle', 'ML model', 'LPR']
        self.mOpenLine1.setText(data['source']['path'])

        if data['source']['type'] == 'video':
            self.mRadioVideo.setChecked(True)
            filelist = []
            typelist = ['.mp4', '.avi', '.mov', '.mpg', '.MP4', '.AVI', '.MOV', '.MPG', '.asf', '.ASF']
            for file in os.listdir(data['source']['path']):
                if file[-4:] in typelist:
                    filelist.append(file)
            self.mFileList1.clear()
            self.mFileList1.addItems(filelist)
            if self.mFileList1.count() > 0:
                self.dir_path1 = data['source']['path']
                self.mOpenLine1.setText(self.dir_path1)
                self.capture = cv2.VideoCapture(data['source']['path'] + '/' + self.mFileList1.item(0).text())
                ret, frame = self.capture.read()
                if ret:
                    rgbImage = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    h, w, ch = rgbImage.shape
                    bytesPerLine = ch * w
                    self.image = QImage(rgbImage.data, w, h, bytesPerLine, QImage.Format_RGB888)
                    self.lines.clear()
                    self.mLineList.clear()
                    self.mDrawWidget.update()
                self.capture.release()
                self.changedROI(list.index(data['type']))
                self.mSelectLine.setCurrentIndex(list.index(data['type']))

        else:
            self.mRadioCamera.setChecked(True)
            url = data['source']['path']
            try:
                self.capture = cv2.VideoCapture(url)
                ret, frame = self.capture.read()
            except:
                QMessageBox.warning(self, 'Warning', "Can't open this stream.")
                self.capture.release()
                return
            if not ret:
                QMessageBox.warning(self, 'Warning', "Can't open this stream.")
                self.capture.release()
                return
            rgbImage = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            h, w, ch = rgbImage.shape
            bytesPerLine = ch * w
            self.image = QImage(rgbImage.data, w, h, bytesPerLine, QImage.Format_RGB888)
            self.lines.clear()
            self.mLineList.clear()
            self.mDrawWidget.update()
            self.capture.release()
            self.mFileList1.addItem(url)
            # self.changedROI(list.index(data['type']))
            self.mSelectLine.setCurrentIndex(list.index(data['type']))

        if len(data['lines']) == 0:
            self.mLPRROI2.setChecked(True)
            self.mDrawWidget.update()
            return

        for key in data['lines'].keys():
            self.lines.append(data['lines'][key])
            self.mLineList.addItem(key)
            self.mDrawWidget.update()


        if data['type'] in ['Junction', 'Ped & Bicycle']:
            i = 1
            for key in data['labels'].keys():
                self.addRelation()
                if data['type'] == 'Junction':
                    self.findChild(QRadioButton, 'mRadioV_' + str(i)).setChecked(True) if data['labels'][key]['type'] == 'vehicle' else self.findChild(QRadioButton, 'mRadioP_' + str(i)).setChecked(True)
                self.findChild(MyLineEdit, 'mTitleLine_' + str(i)).setText(key)
                self.findChild(QComboBox, 'mBox1_' + str(i)).setCurrentIndex([k for k in data['lines'].keys()].index(data['labels'][key]['from']))
                self.findChild(QComboBox, 'mBox2_' + str(i)).setCurrentIndex([k for k in data['lines'].keys()].index(data['labels'][key]['to']))
                i+=1

                


    def showFrame(self, item):
        self.capture = cv2.VideoCapture(self.dir_path1 + '/' + item.text())
        ret, frame = self.capture.read()
        if ret:
            rgbImage = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            h, w, ch = rgbImage.shape
            bytesPerLine = ch * w
            self.image = QImage(rgbImage.data, w, h, bytesPerLine, QImage.Format_RGB888)
            self.mDrawWidget.update()
        self.capture.release()

    def changedROI(self, index):
        self.mLineList.clear()
        self.lines.clear()
        self.mDrawWidget.update()

        index = self.mSelectLine.currentIndex()

        if index in [1, 3, 4]:
            self.mAddR.hide()
            self.mDelR.hide()
        else:
            self.mAddR.show()
            self.mDelR.show()

        if index == 4:
            self.mLabelTime1.hide()
            self.mLabelTime2.hide()
            self.mTimeInterval.hide()
            self.mLPRROI1.show()
            self.mLPRROI1.setChecked(True)
            self.mLPRROI2.show()
        else:
            self.mLabelTime1.show()
            self.mLabelTime2.show()
            self.mTimeInterval.show()
            self.mLPRROI1.hide()
            self.mLPRROI2.hide()
        try:
            for i in self.num_relation:
                tempWgt = self.findChild(QWidget, 'mRWdt_' + str(i))
                tempWgt.deleteLater()
            self.num_relation = []
        except:
            pass

    def addRelation(self):
        if len(self.lines) == 0:
            return
        if len(self.num_relation) == 0:
            self.num_relation.append(1)
        else:
            self.num_relation.append(self.num_relation[-1] + 1)

        hlayout = QHBoxLayout(objectName='mRHlayout_' + str(self.num_relation[-1]))

        if self.mSelectLine.currentIndex() == 0:
            mRadioV = QRadioButton("v", self, objectName='mRadioV_' + str(self.num_relation[-1]))
            mRadioV.setChecked(True)
            mRadioV.setToolTip("relation for vehicle")
            mRadioP = QRadioButton("p", self, objectName='mRadioP_' + str(self.num_relation[-1]))
            mRadioP.setToolTip("relation for ped & bic")
            hlayout.addWidget(mRadioV)
            hlayout.addWidget(mRadioP)

        mTitleLine = MyLineEdit(self, 'label' + str(self.num_relation[-1]))
        mTitleLine.setObjectName('mTitleLine_' + str(self.num_relation[-1]))
        mTitleLine.textChanged.connect(mTitleLine.labelTypeChanged)
        mLab1 = QLabel("from")
        mBox1 = QComboBox(self, objectName='mBox1_' + str(self.num_relation[-1]))
        mLab2 = QLabel("to")
        mBox2 = QComboBox(self, objectName='mBox2_' + str(self.num_relation[-1]))
        mDel = MyButton(self, 'del')
        mDel.setObjectName('mBtnDel_' + str(self.num_relation[-1]))
        mDel.setFixedWidth(40)
        mDel.clicked.connect(mDel.pressedBtn)

        for i in range(self.mLineList.count()):
            mBox1.addItem(self.mLineList.item(i).text())
            mBox2.addItem(self.mLineList.item(i).text())

        hlayout.addWidget(mTitleLine)
        hlayout.addWidget(mLab1)
        hlayout.addWidget(mBox1)
        hlayout.addWidget(mLab2)
        hlayout.addWidget(mBox2)
        hlayout.addWidget(mDel)

        tempWgt = QWidget(self, objectName='mRWdt_' + str(self.num_relation[-1]))
        tempWgt.setLayout(hlayout)
        
        self.mRelationLt.addWidget(tempWgt)

    def deleteRelation(self):
        if len(self.num_relation) == 0:
            return
        tempWgt = self.findChild(QWidget, 'mRWdt_' + str(self.num_relation[-1]))
        tempWgt.deleteLater()
        self.num_relation = self.num_relation[:-1]

    def startProcess(self):
        if self.mStart.text() == "Start":
            index = self.mSelectLine.currentIndex()
            names = []
            for i in range(len(self.lines)):
                names.append(self.mLineList.item(i).text())
            if index in [1, 4]:
                if len(self.lines) == 2:
                    source = self.dir_path1+'/' + self.mFileList1.currentItem().text()
                    filename = self.mFileList1.currentItem().text()
                    output = self.dir_path1
                    webcam = 1
                    if self.mRadioVideo.isChecked():
                        webcam = 0
                    if self.mSavevideo.isChecked():
                        save_video = True
                    else:
                        save_video = False
                    self.workerThread = WorkerThread(index, source, filename, output, webcam, self.lines, names, save_video)
                    self.workerThread.progress.connect(self.setProgress)
                    self.workerThread.detectImage.connect(self.detectImage)
                    self.workerThread.showResult.connect(self.showResult)
                    self.workerThread.finished.connect(self.threadDeleteLater)
                    self.workerThread.start()
            self.mProgressBar.setValue(0)
            self.mStart.setText('Stop')
            self.mDirectoryWidget.hide()
            self.mFilesWidget.hide()
            self.mRelationWidget.hide()
            self.mStreamTypeWidget.hide()
            self.mTimeIntervalWgt.hide()
            self.mAnalyticsTypeWidget.hide()
            self.mResultTable.show()
            if index == 1:
                self.mResultTable.setColumnCount(len(self.lines))
                self.mResultTable.setRowCount(5)
                for i, line in enumerate(self.lines):
                    for j in range(5):
                        item = QTableWidgetItem('0')
                        self.mResultTable.setItem(j, i, item)
                self.mResultTable.setHorizontalHeaderLabels(names)
                self.mResultTable.setVerticalHeaderLabels(['bicycle', 'car', 'motorcycle', 'bus', 'truck'])
        else:
            self.workerThread.quit()
            self.mStart.setText('Start')
            self.mDirectoryWidget.show()
            self.mFilesWidget.show()
            self.mRelationWidget.show()
            self.mStreamTypeWidget.show()
            self.mTimeIntervalWgt.show()
            self.mAnalyticsTypeWidget.show()
            self.mResultTable.hide()
        
    @pyqtSlot(int)
    def setProgress(self, value):
        self.mProgressBar.setValue(value)

    @pyqtSlot()
    def threadDeleteLater(self):
        self.mProgressBar.setValue(1000)
        self.workerThread.deleteLater()
        self.mStart.setText('Start')
        self.mDirectoryWidget.setEnabled(True)
        self.mFilesWidget.setEnabled(True)
        self.mRelationWidget.setEnabled(True)
        self.mStreamTypeWidget.setEnabled(True)
        self.mTimeIntervalWgt.setEnabled(True)
        self.mAnalyticsTypeWidget.setEnabled(True)

    @pyqtSlot(np.ndarray)
    def detectImage(self, image):
        rgbImage = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        h, w, ch = rgbImage.shape
        bytesPerLine = ch * w
        self.image = QImage(rgbImage.data, w, h, bytesPerLine, QImage.Format_RGB888)
        self.mDrawWidget.update()

    @pyqtSlot(dict)
    def showResult(self, result):
        index = self.mSelectLine.currentIndex()
        print(result)
        if index == 1:
            row, column = result['name'], result['line']
            number = int(self.mResultTable.item(row, column).text()) + 1
            self.mResultTable.item(row, column).setText(str(number))

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MyWindow()
    window.show()
    sys.exit(app.exec_())