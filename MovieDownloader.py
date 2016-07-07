import sys
from PyQt5 import QtGui, QtWidgets, QtCore
import requests
from bs4 import BeautifulSoup
import image as Image
import os
import datetime
from functools import partial

class MainWindow(QtWidgets.QMainWindow): 

    def __init__(self):
        super(MainWindow, self).__init__()
        self.move(100, 100)
        self.setFixedSize(600, 800)
        self.setWindowTitle("Search Movies")
        self.setWindowIcon(QtGui.QIcon('movies.png'))

        self.home()

    def home(self):

        #Scroll
        self.scroll = QtWidgets.QScrollArea(self)
        self.scroll.move(0,0)
        self.scroll.setFixedSize(600,800)
        self.scroll.setWidgetResizable(True)

        self.scrollContent = QtWidgets.QWidget(self.scroll)

        self.scrollLayout = QtWidgets.QVBoxLayout(self.scrollContent)
        self.scrollContent.setLayout(self.scrollLayout)
        self.scroll.setWidget(self.scrollContent)

        #Main Window Title
        self.mainTitle = QtWidgets.QLabel("SEARCH MOVIE", self)
        self.mainTitle.resize(400, 150)
        self.mainTitle.move(140, 150)

        #Main Window Title Font
        self.mainTitleFont = QtGui.QFont()
        self.mainTitleFont.setPointSize(30);
        self.mainTitleFont.setBold(True);
        self.mainTitle.setFont(self.mainTitleFont)

        #Movie Titles Font
        self.movieTitleFont = QtGui.QFont()
        self.movieTitleFont.setPointSize(15);
        self.movieTitleFont.setBold(True);
        
        #Search TextBox
        self.textBox = QtWidgets.QTextEdit(self)
        self.textBox.resize(300, 30)
        self.textBox.move(145, 350)

        #Search Button
        self.searchBtn = QtWidgets.QPushButton("Search", self)
        self.searchBtn.clicked.connect(partial(self.searchYTS, "1"))
        self.searchBtn.resize(100, 40)
        self.searchBtn.move(240,400)

        #Return Home Button
        self.returnHome = QtWidgets.QPushButton("Return Home", self)
        self.returnHome.clicked.connect(partial(self.goToHomePage))
        self.returnHome.resize(200, 50)
        self.returnHome.move(190, 400)
        self.returnHome.setVisible(False)

        #No movies found label
        self.noMoviesFound = QtWidgets.QLabel("NO MOVIES FOUND", self)
        self.noMoviesFound.resize(400, 150)
        self.noMoviesFound.move(100, 150)
        self.noMoviesFound.setFont(self.mainTitleFont)
        self.noMoviesFound.setVisible(False)


    def goToHomePage(self):

        #Make Home Widgets Visible
        self.mainTitle.setVisible(True)
        self.textBox.setVisible(True)
        self.searchBtn.setVisible(True)
        
        #Make No Movies Found Label Insivible
        self.noMoviesFound.setVisible(False)

        #Make Return Home Button Invisible
        self.returnHome.setVisible(False)


    def searchYTS (self, currentPage):
        movie = self.textBox.toPlainText()
        ytsUrl = "https://yts.ag/"

        if currentPage == "1":
            ytsSearch = requests.get(ytsUrl + "browse-movies/" + movie + "/all/all/0/latest")
        else:
            ytsSearch = requests.get(ytsUrl + "browse-movies/" + movie + "/all/all/0/latest?page=" + currentPage)
        
        page = BeautifulSoup(ytsSearch.content, "html.parser")
        
        pages = page.find("ul", {"class":"tsc_pagination tsc_paginationA tsc_paginationA06"})
        ytsTag = page.find_all("div", {"class":"browse-movie-wrap col-xs-10 col-sm-4 col-md-5 col-lg-4"})

        if ytsTag:
            movieList = []
            self.getMovieListYTS(ytsTag, movieList)
            self.showMoviesFound(movieList, pages)
        else:


            #Make Home Widgets invisible
            self.mainTitle.setVisible(False)
            self.textBox.setVisible(False)
            self.textBox.clear()
            self.searchBtn.setVisible(False)

            #Make No Movies Found Label Insivible
            self.noMoviesFound.setVisible(True)

            #Make Return Home Button Visible
            self.returnHome.setVisible(True)


    def searchKickass(self):

        movie = self.textBox.toPlainText()
        kickassUrl = "https://kat.cr"
        kickassSearch = requests.get(url + "/usearch/" + movie + "%20category:movies/")

        page = BeautifulSoup(kickassSearch.content, "html.parser")
        kickassTagOdd = page.find_all("tr", {"class":"odd"})
        kickassTagEven = page.find_all("tr", {"class":"even"})

        if kickassTagOdd is not None or kickassTagEven is not None:
            self.getMovieListKickass()


    def getMovieListYTS(self, ytsTag, movieList):

        for tag in ytsTag:

            movieFound = []
            movieImg = tag.find("img", {"class":"img-responsive"})
            movieTitle = tag.find("a", {"class":"browse-movie-title"}).text
            divHD = tag.find("a", string="720p")
            divFullHD = tag.find("a", string="1080p")

            if divHD and divFullHD:
                movieFound = [movieTitle, movieImg.attrs['src'], [divHD.attrs['href'], "720p"], [divFullHD.attrs['href'], "1080p"]]
            elif not divFullHD and divHD:
                movieFound = [movieTitle, movieImg.attrs['src'], [divHD.attrs['href'], "720p"]]
            else:
                movieFound = [movieTitle, movieImg.attrs['src'], [divFullHD.attrs['href'], "1080p"]]

            movieList.append(movieFound)


    def showMoviesFound(self, movieList, pages):

        movies = [[0 for x in range(3)] for y in range(len(movieList))]

        #Make Home Widgets invisible
        self.mainTitle.setVisible(False)
        self.textBox.setVisible(False)
        self.searchBtn.setVisible(False)

        for i in range(len(movieList)):

            #Show Movie Title
            movies[i][0] = QtWidgets.QLabel("Titulo: " + movieList[i][0])
            movies[i][0].setGeometry(100, 50, 15, 20)
            movies[i][0].setFont(self.movieTitleFont)
            self.scrollLayout.addWidget(movies[i][0])

            #Get amd Show Movie Cover Image
            data = requests.get(movieList[i][1])
            image = QtGui.QImage()
            image.loadFromData(data.content)
            imageLabel = QtWidgets.QLabel(self)
            imageLabel.setPixmap(QtGui.QPixmap(image))
            imageLabel.setGeometry(100, 20, 100, 100)
            self.scrollLayout.addWidget(imageLabel)


            #If length is 4 then it has 2 available resolutions
            if len(movieList[i]) == 4:
                

                #Show Resolutions Buttons for Download
                movies[i][2] = [QtWidgets.QPushButton(movieList[i][2][1], self), QtWidgets.QPushButton(movieList[i][3][1], self)]

                movies[i][2][0].clicked.connect(partial(self.downloadMovie, movieList[i], movieList[i][2][1]))
                movies[i][2][0].setGeometry(0, 0, 0, 0)

                movies[i][2][1].clicked.connect(partial(self.downloadMovie, movieList[i], movieList[i][3][1]))
                movies[i][2][1].setGeometry(0, 0, 0, 0)

                self.scrollLayout.addWidget(movies[i][2][0])
                self.scrollLayout.addWidget(movies[i][2][1])

            else:

                #Show Resolution Button for Download (when only one available)
                movies[i][2] = [QtWidgets.QPushButton(movieList[i][2][1], self)]
                movies[i][2][0].clicked.connect(partial(self.downloadMovie, movieList[i], movieList[i][2][1]))
                movies[i][2][0].setGeometry(0, 0, 0, 0)

                self.scrollLayout.addWidget(movies[i][2][0])

        #Checks if there are any result pages
        if len(pages.contents) > 1:

            del pages.contents[0]
            del pages.contents[-1]

            pagesButtonsLayout = QtWidgets.QVBoxLayout()
            pageNumbers = int(pages.contents[-3].text)

            #Adds a button for each one
            for i in range(pageNumbers):
                    pageButton = QtWidgets.QPushButton(str(i + 1), self)
                    pageButton.setGeometry(0,0,5,5)
                    pageButton.clicked.connect(partial(self.searchYTS, str(i)))
                    
                    pagesButtonsLayout.addWidget(pageButton)

            self.scrollLayout.addLayout(pagesButtonsLayout)


    def downloadMovie(self, movieToDownload, resolution):

        torrentExtension = ".torrent"

        if resolution == "720p":
            try:
                r = requests.get(movieToDownload[1][0], stream=True)
                fname = movieToDownload[0] + torrentExtension
                with open(fname, "wb") as f:
                    for chunk in r.iter_content(chunk_size=1024):
                        if chunk:
                            f.write(chunk)
                            f.flush()
            
            except requests.exceptions.RequestException as e:
                #print('\n' + str(e))
                sys.exit(1)
        else:
            try:
                r = requests.get(movieToDownload[2][0], stream=True)
                fname = movieToDownload[0] + torrentExtension
                with open(fname, "wb") as f:
                    for chunk in r.iter_content(chunk_size=1024):
                        if chunk:
                            f.write(chunk)
                            f.flush()
            
            except requests.exceptions.RequestException as e:
                #print('\n' + str(e))
                sys.exit(1)

        self.startDownloadOnTorrentClient(fname)


    def startDownloadOnTorrentClient(self, fname):

        os.startfile(fname)


def run():
    app = QtWidgets.QApplication(sys.argv)
    GUI = MainWindow()
    GUI.show()
    sys.exit(app.exec_())

run()

