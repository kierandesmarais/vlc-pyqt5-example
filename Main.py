#! /usr/bin/python

#
# Qt example for VLC Python bindings
# Copyright (C) 2009-2010 the VideoLAN team
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston MA 02110-1301, USA.
#

#https://github.com/devos50/vlc-pyqt5-example

import os.path
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QPalette, QColor
from PyQt5.QtWidgets import QMainWindow, QWidget, QFrame, QSlider, QHBoxLayout, QPushButton, \
    QVBoxLayout, QAction, QFileDialog, QApplication, QLineEdit, QListWidget
import pafy, vlc, requests, sys
from bs4 import BeautifulSoup as bs

class Player(QMainWindow):
    """A simple Media Player using VLC and Qt
    """
    def __init__(self, master=None):
        QMainWindow.__init__(self, master)
        self.setWindowTitle("Media Player")
        
        self.isAudio = False

        # creating a basic vlc instance
        self.instance = vlc.Instance()
        # creating an empty vlc media player
        self.mediaplayer = self.instance.media_player_new()

        self.createUI()
        self.isPaused = False

    def createUI(self):
        """Set up the user interface, signals & slots
        """
        self.widget = QWidget(self)
        self.setCentralWidget(self.widget)

        # In this widget, the video will be drawn
        if sys.platform == "darwin": # for MacOS
            from PyQt5.QtWidgets import QMacCocoaViewContainer	
            self.videoframe = QMacCocoaViewContainer(0)
        else:
            self.videoframe = QFrame()
        
        
        self.palette = self.videoframe.palette()
        self.palette.setColor (QPalette.Window,
                               QColor(0,0,0))
        self.videoframe.setPalette(self.palette)
        self.videoframe.setAutoFillBackground(True)

        self.positionslider = QSlider(Qt.Horizontal, self)
        self.positionslider.setToolTip("Position")
        self.positionslider.setMaximum(1000)
        self.positionslider.sliderMoved.connect(self.setPosition)

        self.hbuttonbox = QHBoxLayout()
        
        self.playbutton = QPushButton("►")
        self.hbuttonbox.addWidget(self.playbutton)
        self.playbutton.clicked.connect(self.PlayPause)

        self.stopbutton = QPushButton("⯀")
        self.hbuttonbox.addWidget(self.stopbutton)
        self.stopbutton.clicked.connect(self.Stop)
        
        self.audiobutton = QPushButton("𝅘𝅥")
        self.hbuttonbox.addWidget(self.audiobutton)
        self.audiobutton.setToolTip("Switch to audio only mode\n(must search again)")
        self.audiobutton.clicked.connect(self.AudioVideo)
        
        self.hbuttonbox.addStretch(1)
        self.volumeslider = QSlider(Qt.Horizontal, self)
        self.volumeslider.setMaximum(100)
        self.volumeslider.setValue(self.mediaplayer.audio_get_volume())
        self.volumeslider.setToolTip("Volume")
        self.hbuttonbox.addWidget(self.volumeslider)
        self.volumeslider.valueChanged.connect(self.setVolume)
        
        self.hbuttonbox2 = QHBoxLayout()
        
        self.searchline = QLineEdit()
        self.hbuttonbox2.addWidget(self.searchline)
        self.searchline.setToolTip("Enter search term here")
        
        self.searchbutton = QPushButton("Search")
        self.hbuttonbox2.addWidget(self.searchbutton)
        self.searchbutton.setToolTip("Press to search")
        self.searchbutton.clicked.connect(self.searchYouTube)
        
        self.searchresult = QHBoxLayout()
        
        #adding QListWidget to the layout causes the video frame
        #to disappear and im not sure why
        #self.searchresults = QListWidget(self)
        #self.searchresult.addWidget(self.searchresults)
        #self.searchresults.addItem("testing1")
        #self.searchresults.addItem("testing2")
        
        self.vboxlayout = QVBoxLayout()
        self.vboxlayout.addWidget(self.videoframe)
        self.vboxlayout.addWidget(self.positionslider)
        self.vboxlayout.addLayout(self.hbuttonbox)
        self.vboxlayout.addLayout(self.hbuttonbox2)
        #self.vboxlayout.addLayout(self.searchresult)
        
        self.widget.setLayout(self.vboxlayout)

        open = QAction("&Open", self)
        open.triggered.connect(lambda: self.OpenFile())
        exit = QAction("&Exit", self)
        exit.triggered.connect(sys.exit)
        download = QAction("&Download", self)
        download.triggered.connect(self.downloadFile)
        menubar = self.menuBar()
        filemenu = menubar.addMenu("&File")
        filemenu.addAction(open)
        filemenu.addSeparator()
        filemenu.addAction(exit)
        filemenu.addSeparator()
        filemenu.addAction(download)

        self.timer = QTimer(self)
        self.timer.setInterval(200)
        self.timer.timeout.connect(self.updateUI)
    
    def AudioVideo(self):
        """Toggle whether a video is shown or just audio.
        requires another search to take effect"""
        if self.isAudio == False:
            self.isAudio = True
            self.audiobutton.setText("🎥")
            self.audiobutton.setToolTip("Switch to video only mode\n(must search again)")
        else:
            self.isAudio = False
            self.audiobutton.setText("𝅘𝅥")
            self.audiobutton.setToolTip("Switch to audio only mode\n(must search again)")

    def PlayPause(self):
        """Toggle play/pause status
        """
        if self.mediaplayer.is_playing():
            self.mediaplayer.pause()
            self.playbutton.setText("►")
            self.isPaused = True
        else:
            if self.mediaplayer.play() == -1:
                self.searchYouTube()
                return
            self.mediaplayer.play()
            self.playbutton.setText("❚❚")
            self.timer.start()
            self.isPaused = False

    def Stop(self):
        """Stop player
        """
        self.mediaplayer.stop()
        self.playbutton.setText("►")

    def OpenFile(self, filename=None):
        """Open a media file in a MediaPlayer
        """
        if filename is None:
            filename = QFileDialog.getOpenFileName(self, "Open File", os.path.expanduser('~'))[0]
        if not filename:
            return

        # create the media
        if sys.version < '3':
            filename = unicode(filename)
        self.media = self.instance.media_new(filename)
        # put the media in the media player
        self.mediaplayer.set_media(self.media)

        # parse the metadata of the file
        self.media.parse()
        # set the title of the track as window title
        self.setWindowTitle(self.media.get_meta(0))

        # the media player has to be 'connected' to the QFrame
        # (otherwise a video would be displayed in it's own window)
        # this is platform specific!
        # you have to give the id of the QFrame (or similar object) to
        # vlc, different platforms have different functions for this
        if sys.platform.startswith('linux'): # for Linux using the X Server
            self.mediaplayer.set_xwindow(self.videoframe.winId())
        elif sys.platform == "win32": # for Windows
            self.mediaplayer.set_hwnd(self.videoframe.winId())
        elif sys.platform == "darwin": # for MacOS
            self.mediaplayer.set_nsobject(int(self.videoframe.winId()))
        self.PlayPause()
        
    def searchYouTube(self):
        """Search YouTube with search term and play top video"""
        searchTerm = self.searchline.text()
        self.searchline.clear()
        
        searchTerm = searchTerm.replace(" ", "+")       #For formatting
        
        #request youtube search results and web scrape information
        r = requests.get("https://www.youtube.com/results?search_query="+searchTerm)
        page = r.text
        soup = bs(page, 'html.parser')
        vids = soup.findAll('a', attrs={'class':'yt-uix-tile-link'})
        
        self.titlelist = []
        self.videolist = []
        #create a list with all the links and titles of youtube videos
        for v in vids:
            tmp = 'https://www.youtube.com' + v['href']
            self.videolist.append(tmp)
            self.titlelist.append(v['title'])
        
        #currently only the top video will play
        url_0 = self.videolist[0]
        
        #use pafy to convert into a VLC playable video
        self.video_0 = pafy.new(url_0)
        
        #chooses whether to get video or audio only
        if self.isAudio:
            self.best = self.video_0.getbestaudio()
        else:
            self.best = self.video_0.getbest()
            
        #play in VLC
        playurl = self.best.url
        self.media = self.instance.media_new(playurl)
        self.media.get_mrl()
        self.mediaplayer.set_media(self.media)
        
        if sys.platform.startswith('linux'): # for Linux using the X Server
            self.mediaplayer.set_xwindow(self.videoframe.winId())
        elif sys.platform == "win32": # for Windows
            self.mediaplayer.set_hwnd(self.videoframe.winId())
        elif sys.platform == "darwin": # for MacOS
            self.mediaplayer.set_nsobject(int(self.videoframe.winId()))
            
        self.setWindowTitle(self.titlelist[0])
        self.PlayPause()

    def setVolume(self, Volume):
        """Set the volume
        """
        self.mediaplayer.audio_set_volume(Volume)

    def setPosition(self, position):
        """Set the position
        """
        # setting the position to where the slider was dragged
        self.mediaplayer.set_position(position / 1000.0)
        # the vlc MediaPlayer needs a float value between 0 and 1, Qt
        # uses integer variables, so you need a factor; the higher the
        # factor, the more precise are the results
        # (1000 should be enough)
        
    def downloadFile(self):
        """downloads the file currently playing, .mp4 for video or .webm for audio
        settings can be altered but are left default for now"""
        self.best.download()

    def updateUI(self):
        """updates the user interface"""
        # setting the slider to the desired position
        self.positionslider.setValue(self.mediaplayer.get_position() * 1000)

        if not self.mediaplayer.is_playing():
            # no need to call this function if nothing is played
            self.timer.stop()
            if not self.isPaused:
                # after the video finished, the play button stills shows
                # "Pause", not the desired behavior of a media player
                # this will fix it
                self.Stop()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    player = Player()
    player.show()
    player.resize(640, 480)
    if sys.argv[1:]:
        player.OpenFile(sys.argv[1])
    sys.exit(app.exec_())
