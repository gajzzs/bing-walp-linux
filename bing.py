import time
import requests
import json
from PySide6 import QtWidgets, QtUiTools, QtGui, QtCore
from PySide6.QtWidgets import QDialog
import sys
import os
import urllib
import threading
from datetime import datetime


class ImageAskDialog(QDialog):
    def __init__(self, name, parent):
        super().__init__(parent)
        
        self.loader = QtUiTools.QUiLoader()
        self.qdialogConf = self.loader.load("dialog.ui", parent)
        self.qdialogConf.setWindowModality(QtCore.Qt.ApplicationModal)
        self.qdialogConf.setWindowTitle(name)
        self.qdialogConf.show()
        self.qdialogConf.buttonBox.accepted.connect(lambda : self.showOpenFolderDialog())

        self.qdialogConf.buttonBox.rejected.connect(lambda : self.writeToFileNotTosave())
    
    def showOpenFolderDialog(self):
        filePath = QtWidgets.QFileDialog.getExistingDirectory(
            parent = self.qdialogConf,
            caption = 'Select a Folder',
        )
        if not filePath == '':
            f = open('getData.json', 'w')
            toWrite = '{ "isUserSeenDialog" : true ,"isSaveToFolder" : true, "data" : { "isFilePathSet" : true,  "FilePathUrl" : "'+ filePath +'"}}'
            f.write(toWrite)
            f.close()
        else : self.writeToFileNotTosave()

    def writeToFileNotTosave(self):
        f = open('getData.json', 'w')
        toWrite = '{ "isUserSeenDialog" : true ,"isSaveToFolder" : true, "data" : { "isFilePathSet" : false,  "FilePathUrl" : "None"}}'
        f.write(toWrite)
        f.close()


class Window():
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.app = QtWidgets.QApplication(sys.argv)
        
        self.loader = QtUiTools.QUiLoader()
        self.window = self.loader.load("bing.ui", None)
        self.imageIndex = 1

        if not os.path.exists('getData.json'):
            f = open('getData.json', 'w')
            f.write("""{ "isUserSeenDialog" : false ,"isSaveToFolder" : false, "data" : { "isFilePathSet" : true,  "FilePathUrl" : "None"}}""")
            f.close()
        
        self.window.fetchImage.clicked.connect(lambda: self.fetchImage(self.imageIndex))
        self.window.next.clicked.connect(lambda: self.nextImage())
        self.window.back.clicked.connect(lambda: self.backImage())
        self.window.setasBackground.clicked.connect(lambda: self.setAsBackgroundClick())
        self.window.setWindowTitle("BING WALLPAPER - LINUX")

        self.window.show()

        # ImageAskDialog('f', self.window)

        sys.exit(self.app.exec_())


    def nextImage(self):
        self.imageIndex+=1
        self.fetchImage(self.imageIndex)
        if (self.imageIndex > 0 ):
            self.window.back.setEnabled(True)

    def backImage(self):
        if (self.imageIndex <= 0 ):
            print(self.imageIndex)
            self.window.back.setEnabled(False)
            self.window.alertMSG.setText('<p style="color:red;">Error No Image Found!!</p>')
        else:
            self.imageIndex-=1
            self.fetchImage(self.imageIndex)

    def copyRightText(self, text):
        textLen = len(text)
        if textLen >= 55 :
            text = text[0:55]+'...'
            return text
        else:
            print('here:')
            return text
        
    def getImageFromUrl(self, imageUrl, imageTitle):
        try :
            return urllib.request.urlretrieve(imageUrl, imageTitle)
        except Exception as e:
            connectDialogUiLoader = QtUiTools.QUiLoader()
            self.connectDialogUi = connectDialogUiLoader.load('connectionProblem.ui', self.window)
            self.connectDialogUi.setWindowModality(QtCore.Qt.ApplicationModal)
            self.connectDialogUi.setWindowTitle("Connection Problem!!")
            self.connectDialogUi.show()
            # sys.exit(e)

    def getUrlDataImage(self, url):
        try :
            return requests.get(url)
        except Exception as e:
            self.connectDialogUiLoader = QtUiTools.QUiLoader()
            self.connectDialogUi = self.connectDialogUiLoader.load('connectionProblem.ui', self.window)
            self.connectDialogUi.setWindowModality(QtCore.Qt.ApplicationModal)
            self.connectDialogUi.setWindowTitle("Connection Problem!!")
            self.connectDialogUi.show()
            return False

    def fetchImage(self, imageIndex):
        
        url = f"https://www.bing.com/HPImageArchive.aspx?format=js&idx={imageIndex}&n=1&mkt=en-US"

        return_get = self.getUrlDataImage(url)
        print(return_get)

        if return_get != False:
                
            base_url = return_get.content
            base_image_data = json.loads(base_url)
            

            url = base_image_data["images"][0]['url']
            self.image_title_from_url = base_image_data["images"][0]['title']
            self.window.alertMSG.setText(self.image_title_from_url)
            copyText = base_image_data["images"][0]['copyright']

            copyTextt = self.copyRightText(copyText)
            self.window.setWindowTitle( f"BING - {copyTextt}")
            image_url = f"https://bing.com{url}"

            self.imageLable = self.window.imageBG
            self.isImagePathSetFile = open('getData.json', 'r')
            self.isToSaveImage = self.isImagePathSetFile.read()
            self.isImagePathSetFile.close()
            print(self.isToSaveImage)

            self.isToSaveImage = json.loads(self.isToSaveImage)
            print(self.isToSaveImage)

            self.image_title = ''
            
            # TODO : if user want to use default path /usr/share/backgrounds then use root or else define path
            if self.isToSaveImage['data']['isFilePathSet']:
                date = datetime.now().strftime("%Y-%m-%d%H:%M:%S")
                self.image_title = f"{self.isToSaveImage['data']['FilePathUrl']}/{self.image_title_from_url}.jpg"
                self.getImageFromUrl(image_url, self.image_title)
            

            if self.isToSaveImage['isSaveToFolder'] and not self.isToSaveImage['data']['isFilePathSet']:
                filePath = QtWidgets.QFileDialog.getExistingDirectory(
                    parent = self.window,
                    caption = 'Select a Folder',
                )
                if not filePath == '':
                    f = open('getData.json', 'w')
                    toWrite = '{ "isUserSeenDialog" : true ,"isSaveToFolder" : true, "data" : { "isFilePathSet" : true,  "FilePathUrl" : "'+ filePath +'"}}'
                    f.write(toWrite)
                    f.close()
                    date = datetime.now().strftime('%Y-%m-%d%H:%M:%S')
                    self.image_title = f"{filePath}/{self.image_title_from_url}.jpg"
                    self.getImageFromUrl(image_url, self.image_title)
                else:
                        f = open('getData.json', 'w')
                        toWrite = '{ "isUserSeenDialog" : true ,"isSaveToFolder" : true, "data" : { "isFilePathSet" : false,  "FilePathUrl" : "None"}}'
                        f.write(toWrite)
                        f.close()


            self.imageContentData = urllib.request.urlopen(image_url).read()
            
            i = QtGui.QPixmap()
            i.loadFromData(self.imageContentData)
            i = i.scaled(461, 211)
            i = self.imageLable.setPixmap(i)

            
            if not self.isToSaveImage['isUserSeenDialog']:
                ImageAskDialog("Alert", self.window)

    def getDesktopEnviroment(self):
        de = os.popen('env | grep DESKTOP_SESSION=').read()
        return de.split('=')[1]


    def setAsBackgroundClick(self):
        # TODO : try execpt if self.imageContentData is not Defined
        
        default_path = "/usr/share/backgrounds/pop/"
        path = self.isToSaveImage['data']['FilePathUrl']
        f = open(path + '/' + self.image_title_from_url + '.jpg', 'wb')
        f.write(self.imageContentData)
        f.close()
        print(path)
        
        de = self.getDesktopEnviroment()
        
        # for only plasma supports/ gnome has problem it reqires logout then login to relect desktop
        s = os.system("""qdbus org.kde.plasmashell /PlasmaShell org.kde.PlasmaShell.evaluateScript 'var allDesktops = desktops();print (allDesktops);for (i=0;i<allDesktops.length;i++) {d = allDesktops[i];d.wallpaperPlugin = "org.kde.image";d.currentConfigGroup = Array("Wallpaper", "org.kde.image", "General");d.writeConfig("Image", "file://"""+ path +"""/""" + self.image_title_from_url + """.jpg")}'""")
        print(s)
        if de == "plasma":
            print('here i am plasma')
        

        # imageFileUrlToSet = f"gsettings set org.gnome.desktop.background picture-uri file:///{self.isImagePathSet['FilePathUrl']}/{self.imageIndex}.jpg"
        # os.popen(imageFileUrlToSet)

Window()
