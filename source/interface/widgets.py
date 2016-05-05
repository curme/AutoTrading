import sys
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QColor, QIcon, QFont, QPalette
from PyQt5.QtWidgets import (QMainWindow, QWidget, QAction, qApp, QTabWidget, 
    QHBoxLayout, QVBoxLayout, QLabel, QToolBar, QToolButton, QTextEdit,
    QScrollArea, QPushButton, QDesktopWidget, QComboBox, QGridLayout, QCheckBox,
    QLineEdit)

class MainWindow(QMainWindow):

    def __init__(self):

        super(MainWindow, self).__init__()
        self.initUI()

    def initUI(self):

        self.setStyle()
        self.setWindowTitle('Auto Trading System')
        self.initToolBar()
        self.initMenuBar()
        self.initMainBoard()
        self.configPage()

        # make window in center point
        self.setFixedSize(1000, 700)
        qr = self.frameGeometry()
        qr.moveCenter(QDesktopWidget().availableGeometry().center())
        self.move(qr.topLeft())

        self.show()

    def initMainBoard(self):

        self.mainBoard = QWidget()
        self.setCentralWidget(self.mainBoard)
        self.pagesStatus = [0]*4
        self.pages = [QWidget(self.mainBoard) for i in self.pagesStatus]
        self.toolButtons

        self.mainBoard.setStyleSheet(self.mainBoardQSS)
        for page in self.pages: page.setStyleSheet(self.pagesQSS)

    def initToolBar(self):

        self.toolBar = QToolBar("Tools")
        self.toolBar.setMovable(False)
        self.addToolBar(Qt.LeftToolBarArea, self.toolBar)
        self.toolBar.setIconSize(QSize(20, 20))

        self.configButton = QToolButton()
        self.configButton.setText("Configure")
        self.configButton.setFixedSize(130, 25)
        self.atoTrdButton = QToolButton()
        self.atoTrdButton.setText("Auto Trade")
        self.atoTrdButton.setFixedSize(130, 25)
        self.trdPnlButton = QToolButton()
        self.trdPnlButton.setText("Profit and Loss")
        self.trdPnlButton.setFixedSize(130, 25)
        self.trdHisButton = QToolButton()
        self.trdHisButton.setText("Trade History")
        self.trdHisButton.setFixedSize(130, 25)

        self.configButton.clicked.connect(self.configPage)
        self.atoTrdButton.clicked.connect(self.atoTrdPage)
        self.trdPnlButton.clicked.connect(self.trdPnlPage)
        self.trdHisButton.clicked.connect(self.trdHisPage)

        self.toolBar.addWidget(self.configButton)
        self.toolBar.addWidget(self.atoTrdButton)
        self.toolBar.addWidget(self.trdPnlButton)
        self.toolBar.addWidget(self.trdHisButton)
        self.toolButtons = [self.configButton, self.atoTrdButton, self.trdPnlButton, self.trdHisButton]

    def initMenuBar(self):

        exitAction = QAction('&Exit', self)
        exitAction.setShortcut('Ctrl+Q')
        exitAction.triggered.connect(qApp.quit)

        launchAction = QAction('&Launch', self)
        launchAction.setShortcut('Ctrl+L')
        launchAction.triggered.connect(self.execute)

        menubar = self.menuBar()
        menubar.setNativeMenuBar(False)
        fannsMenu = menubar.addMenu('&App')
        fannsMenu.addAction(exitAction)
        editMenu = menubar.addMenu('&Func')
        editMenu.addAction(launchAction)

    def execute(self):

        print 'have a lunch!'

    # The confidgure page
    def configPage(self):

        # hide all pages to show self page
        for pi in range(0,len(self.pages)):
            self.toolButtons[pi].setStyleSheet(self.toolButtonHideQSS)
            self.pages[pi].hide()

        print "in config page"
        ci = 0
        page = self.pages[ci]
        self.toolButtons[ci].setStyleSheet(self.toolButtonFocusQSS)

        if self.pagesStatus[ci] == 0:

            vbox = QVBoxLayout(page)
            vbox.setContentsMargins(0, 5, 0, 0)

            titleLabel = QLabel("Configure")
            titleLabel.setFixedSize(860, 25)
            titleLabel.setStyleSheet(self.pageTitleQSS)
            vbox.addWidget(titleLabel)

            securityLabel = QLabel("Security Select", page)
            securityLabel.setFixedSize(860, 25)
            securityLabel.setStyleSheet(self.pageSubTitleQSS)
            vbox.addWidget(securityLabel)

            securityHbox = QHBoxLayout()
            securityHbox.setContentsMargins(30, 10, 0, 30)

            securityCode= QLabel("Security Code: ", page)
            securityCode.setFont(self.contentFont)
            securityCode.setFixedSize(100, 25)
            securityCode.setStyleSheet(self.itemNameQSS)
            securityHbox.addWidget(securityCode)

            securityCombo = QComboBox(page)
            securityCombo.setFixedSize(300, 25)
            securityCombo.setStyleSheet(self.comboQSS)
            securityCombo.addItem("HSI")
            securityCombo.addItem("HSI-1")
            securityCombo.addItem("HSI-2")
            securityCombo.addItem("HSI-3")
            securityCombo.addItem("HSI-4")
            securityCombo.addItem("HSI-10")
            securityCombo.addItem("Oil")
            securityCombo.addItem("Coal")
            securityCombo.addItem("Fe")
            securityCombo.addItem("Au")
            securityCombo.addItem("Ag")
            securityHbox.addWidget(securityCombo)

            securityHbox.addStretch(1)
            vbox.addLayout(securityHbox)

            strategiesLabel = QLabel("Strategies Select", page)
            strategiesLabel.setFixedSize(860, 25)
            strategiesLabel.setStyleSheet(self.pageSubTitleQSS)
            vbox.addWidget(strategiesLabel)

            strategiesWidget = QWidget(page)
            strategiesWidget.setFixedSize(700, 100)
            strategiesGrid = QGridLayout()
            strategiesGrid.setContentsMargins(30, 10, 0, 30)
            strategiesGrid.addWidget(QCheckBox("MACD"), *(1,1))
            strategiesGrid.addWidget(QCheckBox("Balling Band"), *(1,2))
            strategiesGrid.addWidget(QCheckBox("ANG-1"), *(1,3))
            strategiesGrid.addWidget(QCheckBox("ANG-2"), *(1,4))
            strategiesGrid.addWidget(QCheckBox("ANG-3"), *(1,5))
            strategiesGrid.addWidget(QCheckBox("ANG-96"), *(2,1))
            strategiesGrid.addWidget(QCheckBox("ANG-97"), *(2,2))
            strategiesGrid.addWidget(QCheckBox("ANG-98"), *(2,3))
            strategiesGrid.addWidget(QCheckBox("ANG-99"), *(2,4))
            strategiesGrid.addWidget(QCheckBox("ANG-100"), *(2,5))
            strategiesWidget.setLayout(strategiesGrid)
            vbox.addWidget(strategiesWidget)


            timeSpanLabel = QLabel("Trading Time Config", page)
            timeSpanLabel.setFixedSize(860, 25)
            timeSpanLabel.setStyleSheet(self.pageSubTitleQSS)
            vbox.addWidget(timeSpanLabel)

            timeVbox = QVBoxLayout()
            timeVbox.setContentsMargins(30, 10, 0, 30)
            startTimeHbox = QHBoxLayout()
            startTimeName = QLabel("Start Time: ", page)
            startTimeName.setFont(self.contentFont)
            startTimeName.setFixedSize(100, 25)
            startTimeName.setStyleSheet(self.itemNameQSS)
            startTimeHbox.addWidget(startTimeName)
            startTimeEdit = QLineEdit()
            startTimeEdit.setStyleSheet(self.lineEditQSS)
            startTimeEdit.setFixedSize(300, 25)
            startTimeHbox.addWidget(startTimeEdit)
            startTimeHbox.addStretch(1)
            timeVbox.addLayout(startTimeHbox)
            endTimeHbox = QHBoxLayout()
            endTimeName = QLabel("End Time: ", page)
            endTimeName.setFont(self.contentFont)
            endTimeName.setFixedSize(100, 25)
            endTimeName.setStyleSheet(self.itemNameQSS)
            endTimeHbox.addWidget(endTimeName)
            endTimeEdit = QLineEdit()
            endTimeEdit.setStyleSheet(self.lineEditQSS)
            endTimeEdit.setFixedSize(300, 25)
            endTimeHbox.addWidget(endTimeEdit)
            endTimeHbox.addStretch(1)
            timeVbox.addLayout(endTimeHbox)
            vbox.addLayout(timeVbox)


            page.setLayout(vbox)

            self.pagesStatus[ci] = 1

        page.show()

    def atoTrdPage(self):

        for pi in range(0,len(self.pages)):
            self.toolButtons[pi].setStyleSheet(self.toolButtonHideQSS)
            self.pages[pi].hide()

        print "in auto trade page"
        ci = 1
        page = self.pages[ci]
        self.toolButtons[ci].setStyleSheet(self.toolButtonFocusQSS)

        if self.pagesStatus[ci] == 0:

            vbox = QVBoxLayout(page)
            vbox.setContentsMargins(0, 5, 0, 0)

            titleLabel = QLabel("Auto Trade", page)
            titleLabel.setFixedSize(860, 25)
            titleLabel.setStyleSheet(self.pageTitleQSS)
            vbox.addWidget(titleLabel)

            page.setLayout(vbox)
            self.pagesStatus[ci] = 1

        page.show()

    def trdPnlPage(self):

        for pi in range(0,len(self.pages)):
            self.toolButtons[pi].setStyleSheet(self.toolButtonHideQSS)
            self.pages[pi].hide()

        print "in profit and loss page"
        ci = 2
        page = self.pages[ci]
        self.toolButtons[ci].setStyleSheet(self.toolButtonFocusQSS)

        if self.pagesStatus[ci] == 0:

            vbox = QVBoxLayout(page)
            vbox.setContentsMargins(0, 5, 0, 0)

            titleLabel = QLabel("Profit and Loss", page)
            titleLabel.setFixedSize(860, 25)
            titleLabel.setStyleSheet(self.pageTitleQSS)
            vbox.addWidget(titleLabel)

            page.setLayout(vbox)
            self.pagesStatus[ci] = 1

        page.show()

    def trdHisPage(self):

        for pi in range(0,len(self.pages)):
            self.toolButtons[pi].setStyleSheet(self.toolButtonHideQSS)
            self.pages[pi].hide()

        print "in trade history page"
        ci = 3
        page = self.pages[ci]
        self.toolButtons[ci].setStyleSheet(self.toolButtonFocusQSS)

        if self.pagesStatus[ci] == 0:

            vbox = QVBoxLayout(page)
            vbox.setContentsMargins(0, 5, 0, 0)

            titleLabel = QLabel("Trade History", page)
            titleLabel.setFixedSize(860, 25)
            titleLabel.setStyleSheet(self.pageTitleQSS)
            vbox.addWidget(titleLabel)

            page.setLayout(vbox)
            self.pagesStatus[ci] = 1

        page.show()

    def setStyle(self):

        self.setStyleSheet(
            "QToolBar {" +
                "background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 #203138, stop: 1.0 #000000);" +
                "border-right: 1px solid #065279;" +
                "padding: 5px}" +
            "QToolBar > QToolButton {" +
                "color: #ffffff;" +
                "font-family:'ArialRegular';" +
                "font-size: 14px}" +
            "QToolBar > QToolButton:hover {" +
                "background: qlineargradient(x1: 0, y1: 1, x2: 0, y2: 0, stop: 0 #ffcb06, stop: 1.0 #ff9c28);" +
                "border-radius:3px}" +
            "QLabel {" +
                "padding: 10px;}" +
            "QPushButton {" +
                "height: 20px}" +
            "QComboBox {" +
                "border-radius: 1px; " +
                "border-top-right-radius:11px;" +
                "border-bottom-right-radius:11px;" +
                "font-family:'ArialRegular'}" +
            "QComboBox::drop-down {" +
                "width:15px;" +
                "background-color: #ffcb06;" +
                "border-top-right-radius:10px;" +
                "border-bottom-right-radius:10px;}" +
            "QCheckBox {" +
                "color: #ffffff;" +
                "font-family:'ArialRegular'}" +
            "QCheckBox::indicator {" +
                "background-color:#ffffff;" +
                "border-radius: 1px}" +
            "QCheckBox::indicator:checked {" +
                "background-color:#ff9c28}" +
            "QLineEdit {" +
                "background:#ff9c28;" +
                "border-radius:1px}" +
            "QLineEdit:focus {" +
                "border-radius:1px;}"
        )

        self.mainBoardQSS       = "padding:0px; background:qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 #203138, stop: 1.0 #000000);"
        self.pagesQSS           = "background:none; padding: 0px"
        self.pageTitleQSS       = "padding-left:5px; background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 #ec2f4b, stop: 1.0 #85030f); color: #ffffff; font-family: 'ArialRegular'; font-weight:20; font-size: 16px"
        self.pageSubTitleQSS    = "padding-left:5px; background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 #495d76, stop: 1.0 #1f4e7c); color: #dddddd; font-family: 'ArialRegular'; font-weight:20; font-size: 14px"
        self.toolButtonHideQSS  = "background:none; font-size: 14px; font-family:'ArialRegular'"
        self.toolButtonFocusQSS = "background:qlineargradient(x1: 0, y1: 1, x2: 0, y2: 0, stop: 0 #ffcb06, stop: 1.0 #ff9c28);border-radius:3px; color:#000000"
        self.itemNameQSS        = "color: #ffffff; font-family: 'ArialRegular'"
        self.comboQSS           = "padding-left:5px;background-color: #ff9c28;"
        self.lineEditQSS        = "background-color: #ff9c28; border:0px; padding-left:5px; font-family:'ArialRegular'; font-weight:20; font-size: 14px"

        self.pageTitleFont  = QFont('ArialRegular')
        self.titleFont      = QFont('ArialRegular')
        self.contentFont    = QFont('ArialRegular')

        self.pageTitleColor = "#ffffff"
        self.titleColor     = "#ffffff"
        self.contentColor   = "#ffffff"

