import speech_recognition as sr
import pyttsx3
import datetime
import wikipedia
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtWebEngineWidgets import *
from PyQt5 import QtCore, QtGui,QtWidgets ,QtWebEngineWidgets

listener = sr.Recognizer()
engine = pyttsx3.init()

class BookMarkToolBar(QtWidgets.QToolBar):
    bookmarkClicked = QtCore.pyqtSignal(QtCore.QUrl, str)

    def __init__(self, parent=None):
        super(BookMarkToolBar, self).__init__(parent)
        self.actionTriggered.connect(self.onActionTriggered)
        self.bookmark_list = []

    def setBoorkMarks(self, bookmarks):
        for bookmark in bookmarks:
            self.addBookMarkAction(bookmark["title"], bookmark["url"])

    def addBookMarkAction(self, title, url):
        bookmark = {"title": title, "url": url}
        fm = QtGui.QFontMetrics(self.font())
        if bookmark not in self.bookmark_list:
            text = fm.elidedText(title, QtCore.Qt.ElideRight, 150)
            action = self.addAction(text)
            action.setData(bookmark)
            self.bookmark_list.append(bookmark)

    #@QtCore.pyqtSlot(QtWidgets.QAction)
    def onActionTriggered(self, action):
        bookmark = action.data()
        self.bookmarkClicked.emit(bookmark["url"], bookmark["title"])


# main window
class MainWindow(QtWidgets.QMainWindow):

	# constructor
	def __init__(self, parent=None):
		super(MainWindow, self).__init__(parent)

		# creating a tab widget
		self.tabs = QTabWidget()

		# making document mode true
		self.tabs.setDocumentMode(True)

		# adding action when double clicked
		self.tabs.tabBarDoubleClicked.connect(self.tab_open_doubleclick)

		# adding action when tab is changed
		self.tabs.currentChanged.connect(self.current_tab_changed)

		# making tabs closeable
		self.tabs.setTabsClosable(True)

		# adding action when tab close is requested
		self.tabs.tabCloseRequested.connect(self.close_current_tab)

		# making tabs as central widget
		self.setCentralWidget(self.tabs)

		# creating a status bar
		self.status = QStatusBar()

		# setting status bar to the main window
		self.setStatusBar(self.status)

		self.defaultUrl = QtCore.QUrl()
		# creating a tool bar for navigation
		navtb = QToolBar("Navigation")

		# adding tool bar tot he main window
		self.addToolBar(navtb)

		# creating back action
		back_btn = QAction(QIcon('backbutton.jpg'), "Back", self)

		# setting status tip
		back_btn.setStatusTip("Back to previous page")

		# adding action to back button
		# making current tab to go back
		back_btn.triggered.connect(lambda: self.tabs.currentWidget().back())

		# adding this to the navigation tool bar
		navtb.addAction(back_btn)

		# similarly adding next button
		next_btn = QAction(QIcon('forwardbutton.jpg'), "Forward", self)
		next_btn.setStatusTip("Forward to next page")
		next_btn.triggered.connect(lambda: self.tabs.currentWidget().forward())
		navtb.addAction(next_btn)

		# similarly adding reload button
		reload_btn = QAction(QIcon('reloadbutton.jpg'), "Reload", self)
		reload_btn.setStatusTip("Reload page")
		reload_btn.triggered.connect(lambda: self.tabs.currentWidget().reload())
		navtb.addAction(reload_btn)

		# creating home action
		home_btn = QAction(QIcon('homebutton.jpg'), "Home", self)
		home_btn.setStatusTip("Go home")

		# adding action to home button
		home_btn.triggered.connect(self.navigate_home)
		navtb.addAction(home_btn)

		# adding a separator
		navtb.addSeparator()

		# creating a line edit widget for URL
		self.urlbar = QLineEdit()

		# adding action to line edit when return key is pressed
		self.urlbar.returnPressed.connect(self.navigate_to_url)

		# adding line edit to tool bar
		navtb.addWidget(self.urlbar)

		self.favoriteButton = QtWidgets.QToolButton()
		self.favoriteButton.setIcon(QtGui.QIcon("fav.jpg"))
		self.favoriteButton.clicked.connect(self.addFavoriteClicked)
		navtb.addWidget(self.favoriteButton)

		self.addToolBarBreak()
		self.bookmarkToolbar = BookMarkToolBar()
		self.bookmarkToolbar.bookmarkClicked.connect(self.add_new_tab)
		self.addToolBar(self.bookmarkToolbar)
		self.readsettings()

		# similarly adding voice search action
		vo_btn = QAction(QIcon('vbbtn.jpg'), "Virtual Assistant", self)
		vo_btn.setStatusTip("Here Is your Virtual Assistant And Please Command After He is Listening")
		vo_btn.triggered.connect(self.vos)
		navtb.addAction(vo_btn)

		# similarly adding stop action
		stop_btn = QAction(QIcon('stopbutton.jpg'), "Stop", self)
		stop_btn.setStatusTip("Stop loading current page")
		stop_btn.triggered.connect(lambda: self.tabs.currentWidget().stop())
		navtb.addAction(stop_btn)


		# creating first tab
		self.add_new_tab(QUrl('http://www.bing.com'), 'Homepage')

		# showing all the components

		# setting window title
		self.showMaximized()
		self.setWindowTitle("M.O.B")
		self.setWindowIcon(QIcon("Icon.ico"))
		self.setWindowIconText("Browser Logo")


	def addFavoriteClicked(self):
		loop = QtCore.QEventLoop()

		def callback(resp):
			setattr(self, "title", resp)
			loop.quit()

		browser = self.tabs.currentWidget()
		browser.page().runJavaScript("(function() { return document.title;})();", callback)
		url = browser.url()
		loop.exec_()
		self.bookmarkToolbar.addBookMarkAction(getattr(self, "title"), url)
		settings = QtCore.QSettings()
		settings.setValue("bookmarks", self.bookmarkToolbar.bookmark_list)

	def readsettings(self):
		setting = QtCore.QSettings()
		self.defaultUrl = setting.value("defaultUrl", QtCore.QUrl('http://www.bing.com'))
		#self.add_new_tab(self.defaultUrl, 'Home Page')
		self.bookmarkToolbar.setBoorkMarks(setting.value("bookmarks", []))

	def savesettins(self):
		settings = QtCore.QSettings()
		settings.setValue("defaultUrl", self.defaultUrl)
		settings.setValue("bookmarks", self.bookmarkToolbar.bookmark_list)

	def closeEvent(self, event):
		self.savesettins()
		super(MainWindow, self).closeEvent(event)

	def vos(self):
		engine.say('What can I do for you')
		engine.runAndWait()
		self.urlbar.setCursorPosition(0)
		try:
			with sr.Microphone() as source:
				engine.say('I am Listening')
				engine.runAndWait()
				voice = listener.listen(source)
				command = listener.recognize_google(voice)
				command = command.lower()
				if 'hey bro' in command:
					command = command.replace('hey bro', '')
		except:
			engine.say('Please Click and Say the command again')
			engine.runAndWait()
		if 'play' in command:
			song = command.replace('play', '')
			engine.say('Here are youtube result of' + song)
			engine.runAndWait()
			self.add_new_tab(QUrl('https://www.youtube.com/results?search_query=' + song), 'Homepage')
		elif 'time' in command:
			time = datetime.datetime.now().strftime('%I:%M %p')
			engine.say('Current time is' + time)
			engine.runAndWait()
		elif 'search' in command:
			site = command.replace('search for', '')
			engine.say('searching' + site)
			engine.runAndWait()
			self.add_new_tab(QUrl('https://www.bing.com/search?q=' + site), 'Homepage')
		elif 'show me' in command:
			site = command.replace('show me', '')
			engine.say('showing results for' + site)
			engine.runAndWait()
			self.add_new_tab(QUrl('https://www.bing.com/search?q=' + site), 'Homepage')
		elif 'who is' in command:
			person = command.replace('who is', '')
			info = wikipedia.summary(person, 2)
			engine.say(info)
			engine.runAndWait()
		elif 'go on a date' in command:
			engine.say('sorry,I have A work with the system tonight')
			engine.runAndWait()
		elif 'are you single' in command:
			engine.say('Sorry Noo I am in a virtual relationship of internet')
			engine.runAndWait()
		else:
			engine.say('Please click and say the command again.')
			engine.runAndWait()
		self.urlbar.setCursorPosition(0)


	# method for adding new tab
	def add_new_tab(self, qurl = None, label ="Blank"):

		# if url is blank
		if qurl is None:
			# creating a bing url
			qurl = QUrl('http://www.bing.com')

		# creating a QWebEngineView object
		browser = QWebEngineView()


		# setting url to browser
		browser.setUrl(qurl)

		# setting tab index
		i = self.tabs.addTab(browser, label)
		self.tabs.setCurrentIndex(i)

		# adding action to the browser when url is changed
		# update the url
		browser.urlChanged.connect(lambda qurl, browser = browser:
								self.update_urlbar(qurl, browser))

		# adding action to the browser when loading is finished
		# set the tab title
		browser.loadFinished.connect(lambda _, i = i, browser = browser:
									self.tabs.setTabText(i, browser.page().title()))

	# when double clicked is pressed on tabs
	def tab_open_doubleclick(self, i):

		# checking index i.e
		# No tab under the click
		if i == -1:
			# creating a new tab
			self.add_new_tab()

	# wen tab is changed
	def current_tab_changed(self, i):

		# get the curl
		qurl = self.tabs.currentWidget().url()

		# update the url
		self.update_urlbar(qurl, self.tabs.currentWidget())

		# update the title
		self.update_title(self.tabs.currentWidget())

	# when tab is closed
	def close_current_tab(self, i):

		# if there is only one tab
		if self.tabs.count() < 2:
			# do nothing
			return

		# else remove the tab
		self.tabs.removeTab(i)

	# method for updating the title
	def update_title(self, browser):

		# if signal is not from the current tab
		if browser != self.tabs.currentWidget():
			# do nothing
			return

		# get the page title
		title = self.tabs.currentWidget().page().title()

		# set the window title
		self.setWindowTitle("% s - M.O.B" % title)

	# action to go to home
	def navigate_home(self):

		# go to bing
		self.tabs.currentWidget().setUrl(QUrl("http://www.bing.com"))

	# method for navigate to url
	def navigate_to_url(self):

		# get the line edit text
		# convert it to QUrl object
		q = QUrl(self.urlbar.text())

		# if scheme is blank
		if q.scheme() == "":
			# set scheme
			q.setScheme("http")

		# set the url
		self.tabs.currentWidget().setUrl(q)

	# method to update the url
	def update_urlbar(self, q, browser = None):

		# If this signal is not from the current tab, ignore
		if browser != self.tabs.currentWidget():

			return

		# set text to the url bar
		self.urlbar.setText(q.toString())

		# set cursor position
		self.urlbar.setCursorPosition(0)

if __name__ == '__main__':
	import sys

	QtCore.QCoreApplication.setOrganizationName("MBrowser.org")
	QtCore.QCoreApplication.setOrganizationDomain("www.mobbrowser.com")
	QtCore.QCoreApplication.setApplicationName("M.O.B")
	# creating a PyQt5 application
	app = QtWidgets.QApplication(sys.argv)
	# creating MainWindow object
	window = MainWindow()
	# loop
	sys.exit(app.exec_())
#Group No.-B06 Batch No.- B3 Guided by Mrs.Dhanashree Phalke Mam