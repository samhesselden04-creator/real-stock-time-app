
import tkinter as tk
from tkinter import messagebox
import threading
import requests
import time
import os
try:
    import psutil
except ImportError:
    psutil = None
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

from datetime import datetime
apiKey = "d96i16hr01qr77dkif1gd96i16hr01qr77dkif20"
backgroundColour = "#F1F5F9"
sidebarColour = "#152238"

sideSelected = "#203653"
sidebarText = "#B8C6DA"
cardColour = "#FFFFFF"
entryColour = "#F8FAFC"
primaryColour = "#2563EB"

primaryHover = "#1D4ED8"

textColour = "#172033"
secondaryText = "#64748B"
lightText = "#94A3B8"
borderColour = "#DCE4EE"
gridColour = "#E2E8F0"

green = "#16A36A"

greenBackground = "#E7F7F0"
redColour = "#DC3545"
redBackground = "#FCEBEC"

class StockGraph:

    #sets things up
    def __init__(self, parent, symbol, title, large=False):
        self.parent = parent
        self.symbol = symbol

        self.title = title
        self.large = large
        self.timeValues = []
        self.priceValues = []

        self.currentPrice = 0

        self.previousClose = 0
        self.priceChange = 0
        self.percentageChange = 0
        self.frame = tk.Frame(
            parent,
            bg=cardColour,
            highlightbackground=borderColour,
            highlightthickness=1
        )
        self.createHeader()
        self.createGraph()

    #creates header
    def createHeader(self):
        self.headerFrame = tk.Frame(
            self.frame,
            bg=cardColour
        )
        self.headerFrame.pack(
            fill=tk.X,
            padx=18 if self.large else 12,
            pady=(15 if self.large else 10, 4)
        )
        self.titleLabel = tk.Label(
            self.headerFrame,
            text=self.title.upper(),
            bg=cardColour,
            fg=secondaryText,
            font=("Segoe UI Semibold", 9 if self.large else 7)
        )
        self.titleLabel.pack(anchor="w")
        infoFrame = tk.Frame(
            self.headerFrame,
            bg=cardColour
        )
        infoFrame.pack(
            fill=tk.X,
            pady=(4, 0)
        )
        self.symbolLabel = tk.Label(
            infoFrame,
            text=self.symbol,
            bg=cardColour,
            fg=textColour,
            font=("Segoe UI Semibold", 22 if self.large else 13)
        )
        self.symbolLabel.pack(side=tk.LEFT)

        self.priceLabel = tk.Label(
            infoFrame,
            text="Waiting...",
            bg=cardColour,
            fg=secondaryText,
            font=("Segoe UI Semibold", 19 if self.large else 11)
        )
        self.priceLabel.pack(side=tk.RIGHT)
        self.changeLabel = tk.Label(
            self.headerFrame,
            text="Live market price",
            bg=cardColour,
            fg=secondaryText,
            font=("Segoe UI", 9 if self.large else 7)
        )

        self.changeLabel.pack(anchor="e")

    #creates graph
    def createGraph(self):
        if self.large:
            figureSize = (7, 4.4)
        else:
            figureSize = (2.4, 1.1)
        self.figure = Figure(
            figsize=figureSize,
            dpi=100,
            facecolor=cardColour
        )
        self.axis = self.figure.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(
            self.figure,
            master=self.frame
        )
        canvasWidget = self.canvas.get_tk_widget()
        canvasWidget.configure(
            bg=cardColour,
            highlightthickness=0
        )
        canvasWidget.pack(
            fill=tk.BOTH,
            expand=True,
            padx=8,
            pady=(0, 8)
        )
        self.drawEmptyGraph()

    #styles graph
    def styleGraph(self):
        self.axis.set_facecolor(cardColour)
        self.axis.grid(
            True,
            axis="y",
            linestyle="--",
            linewidth=0.7,
            color=gridColour,
            alpha=0.9
        )
        self.axis.tick_params(
            axis="both",
            colors=secondaryText,
            labelsize=8 if self.large else 5,
            length=0
        )
        for spine in self.axis.spines.values():
            spine.set_visible(False)

    #draws empty graph
    def drawEmptyGraph(self):
        self.axis.clear()

        self.styleGraph()
        self.axis.text(
            0.5,
            0.5,
            "Collecting live market data...",
            horizontalalignment="center",
            verticalalignment="center",
            transform=self.axis.transAxes,
            fontsize=11 if self.large else 7,
            color=secondaryText
        )
        self.axis.set_xticks([])

        self.axis.set_yticks([])
        self.figure.tight_layout()
        self.canvas.draw_idle()

    #gets stock price
    def fetchStockPrice(self, callback=None):
        requestThread = threading.Thread(
            target=self.performRequest,
            args=(callback,),
            daemon=True
        )
        requestThread.start()

    #sends api request
    def performRequest(self, callback):
        try:
            url = "https://finnhub.io/api/v1/quote"
            response = requests.get(
                url,
                params={
                    "symbol": self.symbol,
                    "token": apiKey
                },
                timeout=8
            )
            response.raise_for_status()
            stockData = response.json()
            currentPrice = stockData.get("c", 0)

            previousClose = stockData.get("pc", 0)

            if currentPrice and currentPrice > 0:
                self.frame.after(
                    0,
                    lambda: self.processPrice(
                        float(currentPrice),
                        float(previousClose),
                        callback
                    )
                )
            else:
                self.frame.after(
                    0,
                    lambda: self.showNoData(callback)
                )
        except requests.RequestException:
            self.frame.after(
                0,
                lambda: self.showConnectionError(callback)
            )
        except Exception as error:
            print(
                f"Error retrieving stock data for "
                f"{self.symbol}: {error}"
            )

            self.frame.after(
                0,
                lambda: self.showConnectionError(callback)
            )

    #processes price
    def processPrice(self, currentPrice, previousClose, callback):
        self.currentPrice = currentPrice

        self.previousClose = previousClose
        currentTime = datetime.now().strftime("%H:%M:%S")
        self.timeValues.append(currentTime)

        self.priceValues.append(currentPrice)
        if len(self.timeValues) > 30:
            self.timeValues.pop(0)
            self.priceValues.pop(0)
        if previousClose > 0:
            self.priceChange = currentPrice - previousClose
            self.percentageChange = (
                self.priceChange / previousClose
            ) * 100
        self.updatePriceLabels()
        self.updateGraph()
        if callback != None:
            callback(True, self.symbol)

    #updates price labels
    def updatePriceLabels(self):
        self.priceLabel.configure(
            text=f"${self.currentPrice:,.2f}",
            fg=textColour
        )
        if self.priceChange > 0:
            moveSymbol = "▲"
            movementColour = green
        elif self.priceChange < 0:
            moveSymbol = "▼"
            movementColour = redColour
        else:
            moveSymbol = "•"
            movementColour = secondaryText
        self.changeLabel.configure(
            text=(
                f"{moveSymbol} "
                f"{self.priceChange:+.2f} "
                f"({self.percentageChange:+.2f}%) today"
            ),
            fg=movementColour
        )

    #updates graph
    def updateGraph(self):
        self.axis.clear()
        self.styleGraph()
        if len(self.priceValues) > 1:
            if self.priceValues[-1] >= self.priceValues[0]:
                lineColour = green
            else:
                lineColour = redColour
        else:
            lineColour = primaryColour
        self.axis.plot(
            self.timeValues,
            self.priceValues,
            color=lineColour,
            linewidth=2.5 if self.large else 1.6
        )
        if len(self.priceValues) > 1:
            self.axis.fill_between(
                self.timeValues,
                self.priceValues,
                min(self.priceValues),
                color=lineColour,
                alpha=0.08
            )
        self.axis.tick_params(
            axis="x",
            rotation=35 if self.large else 25,
            labelsize=8 if self.large else 5
        )
        self.axis.tick_params(
            axis="y",
            labelsize=8 if self.large else 5
        )
        if self.large:
            self.axis.set_xlabel(
                "Time",
                fontsize=9,
                color=secondaryText,
                labelpad=8
            )

            self.axis.set_ylabel(
                "Price in USD",
                fontsize=9,
                color=secondaryText,
                labelpad=8
            )
        if len(self.priceValues) == 1:
            currentVal = self.priceValues[0]
            margin = max(
                currentVal * 0.001,
                0.05
            )
            self.axis.set_ylim(
                currentVal - margin,
                currentVal + margin
            )
        elif len(self.priceValues) > 1:
            lowPrice = min(self.priceValues)
            highPrice = max(self.priceValues)
            priceRange = highPrice - lowPrice
            margin = max(
                priceRange * 0.25,
                highPrice * 0.0005
            )
            self.axis.set_ylim(
                lowPrice - margin,
                highPrice + margin
            )
        self.figure.tight_layout()

        self.canvas.draw_idle()

    #shows no data
    def showNoData(self, callback):
        self.priceLabel.configure(
            text="No data",
            fg=redColour
        )
        self.changeLabel.configure(
            text="Check stock symbol",
            fg=redColour
        )

        if callback is not None:
            callback(False, self.symbol)

    #shows connection error
    def showConnectionError(self, callback):
        self.priceLabel.configure(
            text="Offline",
            fg=redColour
        )
        self.changeLabel.configure(
            text="Unable to retrieve data",
            fg=redColour
        )
        if callback:
            callback(False, self.symbol)

    #changes stock symbol
    def changeSymbol(self, newSymbol):
        self.symbol = newSymbol

        self.timeValues.clear()

        self.priceValues.clear()

        self.currentPrice = 0

        self.previousClose = 0
        self.priceChange = 0
        self.percentageChange = 0
        self.symbolLabel.configure(
            text=newSymbol
        )

        self.priceLabel.configure(
            text="Waiting...",
            fg=secondaryText
        )

        self.changeLabel.configure(
            text="Live market price",
            fg=secondaryText
        )
        self.drawEmptyGraph()

class StockApp:
    #sets things up
    def __init__(self, root):
        self.root = root
        self.root.title("Live Stock Dashboard")
        self.root.geometry("1250x750")
        self.root.minsize(1050, 650)
        self.root.configure(bg=backgroundColour)

        self.requestsRunning = False
        self.completedReqs = 0
        self.successfulRequests = 0
        self.createLayout()
        self.setupWindowEvents()
        self.startUpdates()

    #sets up window events
    def setupWindowEvents(self):
        self.root.bind("<Return>", lambda event: self.searchStock())
        self.searchEntry.focus_set()

    #starts updates
    def startUpdates(self):
        self.root.after(1000, self.updateAllGraphs)

    #creates app layout
    def createLayout(self):
        self.createSidebar()
        self.mainContainer = tk.Frame(
            self.root,
            bg=backgroundColour
        )

        self.mainContainer.pack(
            side=tk.RIGHT,
            fill=tk.BOTH,
            expand=True
        )
        self.createHeader()
        self.createSearchArea()
        self.createGraphs()
        self.createFooter()

    #creates sidebar
    def createSidebar(self):
        sidebar = tk.Frame(
            self.root,
            bg=sidebarColour,
            width=215
        )
        sidebar.pack(
            side=tk.LEFT,
            fill=tk.Y
        )
        sidebar.pack_propagate(False)
        self.createSidebarButton(
            sidebar,
            "▦",
            "Dashboard",
            selected=True
        )

        performanceButton = tk.Button(
            sidebar,
            text="⚙  Performance Test",
            command=self.runPerformanceTest,
            bg=sidebarColour,
            fg=sidebarText,
            activebackground=sideSelected,
            activeforeground="white",
            relief=tk.FLAT,
            bd=0,
            anchor="w",
            padx=22,
            pady=12,
            font=("Segoe UI", 10),
            cursor="hand2"
        )
        performanceButton.pack(
            fill=tk.X,
            padx=12,
            pady=(0, 8)
        )
        infoFrame = tk.Frame(
            sidebar,
            bg=sidebarColour
        )
        infoFrame.pack(
            side=tk.BOTTOM,
            fill=tk.X,
            padx=22,
            pady=24
        )
        connectionDot = tk.Label(
            infoFrame,
            text="●",
            bg=sidebarColour,
            fg=green,
            font=("Segoe UI", 9)
        )
        connectionDot.pack(side=tk.LEFT)
        connectionText = tk.Label(
            infoFrame,
            text="Finnhub market data",
            bg=sidebarColour,
            fg=sidebarText,
            font=("Segoe UI", 9)
        )
        connectionText.pack(
            side=tk.LEFT,
            padx=(6, 0)
        )

    #creates sidebar button
    def createSidebarButton(
        self,
        parent,
        icon,
        text,
        selected=False
    ):
        if selected:
            normalColour = sideSelected
            textColour = "white"
        else:
            normalColour = sidebarColour
            textColour = sidebarText
        buttonFrame = tk.Frame(
            parent,
            bg=normalColour,
            cursor="hand2"
        )
        buttonFrame.pack(
            fill=tk.X,
            padx=12,
            pady=3
        )
        buttonLabel = tk.Label(
            buttonFrame,
            text=f"  {icon}    {text}",
            bg=normalColour,
            fg=textColour,
            font=(
                "Segoe UI Semibold"
                if selected
                else "Segoe UI",
                10
            ),
            anchor="w",
            padx=10,
            pady=12,
            cursor="hand2"
        )
        buttonLabel.pack(fill=tk.X)
        if not selected:

            #handles button hover
            def enterButton(event):
                buttonFrame.configure(
                    bg=sideSelected
                )

                buttonLabel.configure(
                    bg=sideSelected,
                    fg="white"
                )

            #handles button exit
            def leaveButton(event):
                buttonFrame.configure(
                    bg=sidebarColour
                )
                buttonLabel.configure(
                    bg=sidebarColour,
                    fg=sidebarText
                )
            buttonFrame.bind(
                "<Enter>",
                enterButton
            )
            buttonFrame.bind(
                "<Leave>",
                leaveButton
            )
            buttonLabel.bind(
                "<Enter>",
                enterButton
            )
            buttonLabel.bind(
                "<Leave>",
                leaveButton
            )

    #creates header
    def createHeader(self):
        headerFrame = tk.Frame(
            self.mainContainer,
            bg=backgroundColour
        )
        headerFrame.pack(
            fill=tk.X,
            padx=30,
            pady=(24, 16)
        )
        titleFrame = tk.Frame(
            headerFrame,
            bg=backgroundColour
        )
        titleFrame.pack(side=tk.LEFT)
        titleLabel = tk.Label(
            titleFrame,
            text="Market Dashboard",
            bg=backgroundColour,
            fg=textColour,
            font=("Segoe UI Semibold", 25)
        )
        titleLabel.pack(anchor="w")
        dateLabel = tk.Label(
            titleFrame,
            text=datetime.now().strftime(
                "%A, %d %B %Y"
            ),
            bg=backgroundColour,
            fg=secondaryText,
            font=("Segoe UI", 10)
        )
        dateLabel.pack(
            anchor="w",
            pady=(2, 0)
        )
        self.connectionFrame = tk.Frame(
            headerFrame,
            bg=greenBackground,
            padx=11,
            pady=7
        )
        self.connectionFrame.pack(
            side=tk.RIGHT
        )
        self.connectionDot = tk.Label(
            self.connectionFrame,
            text="●",
            bg=greenBackground,
            fg=green,
            font=("Segoe UI", 9)
        )
        self.connectionDot.pack(side=tk.LEFT)
        self.connectionLabel = tk.Label(
            self.connectionFrame,
            text="Live connection",
            bg=greenBackground,
            fg=green,
            font=("Segoe UI Semibold", 9)
        )
        self.connectionLabel.pack(
            side=tk.LEFT,
            padx=(5, 0)
        )

    #creates search area
    def createSearchArea(self):
        searchCard = tk.Frame(
            self.mainContainer,
            bg=cardColour,
            highlightbackground=borderColour,
            highlightthickness=1
        )
        searchCard.pack(
            fill=tk.X,
            padx=30,
            pady=(0, 16)
        )

        searchContent = tk.Frame(
            searchCard,
            bg=cardColour
        )
        searchContent.pack(
            fill=tk.X,
            padx=18,
            pady=15
        )
        searchTextFrame = tk.Frame(
            searchContent,
            bg=cardColour
        )

        searchTextFrame.pack(side=tk.LEFT)
        searchTitle = tk.Label(
            searchTextFrame,
            text="Search for a stock",
            bg=cardColour,
            fg=textColour,
            font=("Segoe UI Semibold", 10)
        )

        searchTitle.pack(anchor="w")
        searchHelp = tk.Label(
            searchTextFrame,
            text="Enter a ticker such as NVDA",
            bg=cardColour,
            fg=secondaryText,
            font=("Segoe UI", 8)
        )
        searchHelp.pack(anchor="w")
        self.searchVar = tk.StringVar()
        validateCommand = self.root.register(
            self.validateStockCode
        )
        entryContainer = tk.Frame(
            searchContent,
            bg=borderColour,
            padx=1,
            pady=1
        )
        entryContainer.pack(
            side=tk.LEFT,
            fill=tk.X,
            expand=True,
            padx=(20, 10)
        )
        self.searchEntry = tk.Entry(
            entryContainer,
            textvariable=self.searchVar,
            validate="key",
            validatecommand=(
                validateCommand,
                "%P"
            ),
            bg=entryColour,
            fg=textColour,
            insertbackground=textColour,
            relief=tk.FLAT,
            borderwidth=0,
            font=("Segoe UI", 11)
        )

        self.searchEntry.pack(
            fill=tk.X,
            padx=12,
            ipady=9
        )
        self.searchButton = tk.Button(
            searchContent,
            text="Search stock",
            command=self.searchStock,
            bg=primaryColour,
            fg="white",
            activebackground=primaryHover,
            activeforeground="white",
            relief=tk.FLAT,
            borderwidth=0,
            cursor="hand2",
            font=("Segoe UI Semibold", 10),
            padx=24,
            pady=10
        )
        self.searchButton.pack(
            side=tk.RIGHT
        )
        self.searchButton.bind(
            "<Enter>",
            lambda event: self.searchButton.configure(
                bg=primaryHover
            )
        )

        self.searchButton.bind(
            "<Leave>",
            lambda event: self.searchButton.configure(
                bg=primaryColour
            )
        )

    #creates stock graphs
    def createGraphs(self):
        graphsFrame = tk.Frame(
            self.mainContainer,
            bg=backgroundColour
        )
        graphsFrame.pack(
            fill=tk.BOTH,
            expand=True,
            padx=30,
            pady=(0, 14)
        )

        leftFrame = tk.Frame(
            graphsFrame,
            bg=backgroundColour
        )
        leftFrame.pack(
            side=tk.LEFT,
            fill=tk.BOTH,
            expand=True
        )
        rightFrame = tk.Frame(
            graphsFrame,
            bg=backgroundColour,
            width=305
        )
        rightFrame.pack(
            side=tk.RIGHT,
            fill=tk.Y,
            padx=(16, 0)
        )

        rightFrame.pack_propagate(False)
        self.mainGraph = StockGraph(
            leftFrame,
            "TSLA",
            "Selected stock",
            large=True
        )
        self.mainGraph.frame.pack(
            fill=tk.BOTH,
            expand=True
        )
        self.sideGraphs = [
            StockGraph(
                rightFrame,
                "TSLA",
                "Tesla"
            ),
            StockGraph(
                rightFrame,
                "AAPL",
                "Apple"
            ),
            StockGraph(
                rightFrame,
                "AMZN",
                "Amazon"
            )
        ]
        for graphNum, graph in enumerate(
            self.sideGraphs
        ):
            graph.frame.pack(
                fill=tk.BOTH,
                expand=True,
                pady=(
                    0 if graphNum == 0 else 8,
                    0
                )
            )

    #creates footer
    def createFooter(self):
        footerFrame = tk.Frame(
            self.mainContainer,
            bg=backgroundColour
        )
        footerFrame.pack(
            fill=tk.X,
            padx=30,
            pady=(0, 12)
        )
        self.statusLabel = tk.Label(
            footerFrame,
            text="Preparing live market data...",
            bg=backgroundColour,
            fg=secondaryText,
            font=("Segoe UI", 9)
        )
        self.statusLabel.pack(side=tk.LEFT)

        providerLabel = tk.Label(
            footerFrame,
            text="Market data provided by Finnhub",
            bg=backgroundColour,
            fg=secondaryText,
            font=("Segoe UI", 9)
        )

        providerLabel.pack(side=tk.RIGHT)

    #checks stock code
    def validateStockCode(self, newText):
        if len(newText)>5:
            return False
        if newText == "":
            return True
        return newText.isalnum()

    #searches for stock
    def searchStock(self):
        stockCode = (
            self.searchVar
            .get()
            .strip()
            .upper()
        )
        if (
            not stockCode

            or not stockCode.isalnum()
            or len(stockCode) > 5
        ):
            messagebox.showerror(
                "Invalid stock code",
                "Stock code must contain 1-5 letters or numbers."
            )
            return
        self.mainGraph.changeSymbol(
            stockCode
        )
        self.searchVar.set("")
        self.statusLabel.configure(
            text=(
                f"Loading live market data "

                f"for {stockCode}..."
            )
        )
        self.mainGraph.fetchStockPrice(
            self.searchCompleted
        )

    #handles search result
    def searchCompleted(self, successful, symbol):
        currentTime = datetime.now().strftime(
            "%H:%M:%S"
        )

        if successful:
            self.statusLabel.configure(
                text=(
                    f"{symbol} loaded successfully • "
                    f"{currentTime}"
                )
            )
        else:
            self.statusLabel.configure(
                text=(
                    f"Unable to retrieve data "
                    f"for {symbol}"
                )
            )

    #updates all graphs
    def updateAllGraphs(self):
        if self.requestsRunning:
            self.root.after(
                1000,
                self.updateAllGraphs
            )
            return
        self.requestsRunning = True
        self.completedReqs = 0
        self.successfulRequests = 0
        allGraphs = [self.mainGraph] + self.sideGraphs
        self.requestGraphUpdates(allGraphs)

    #requests graph updates
    def requestGraphUpdates(self, graphs):
        for graph in graphs:
            graph.fetchStockPrice(self.graphRequestCompleted)

    #handles graph update
    def graphRequestCompleted(
        self,
        successful,
        symbol
    ):
        self.completedReqs += 1

        if successful:
            self.successfulRequests += 1
        graphTotal = len(
            self.sideGraphs
        ) + 1
        if self.completedReqs >= graphTotal:
            self.requestsRunning = False
            currentTime = datetime.now().strftime(
                "%H:%M:%S"
            )

            if self.successfulRequests == graphTotal:
                self.setConnectionStatus(
                    True,
                    "Live connection"
                )
                self.statusLabel.configure(
                    text=(
                        f"All market data updated • "
                        f"{currentTime}"
                    )
                )
            elif self.successfulRequests > 0:
                self.setConnectionStatus(
                    False,
                    "Partial connection"
                )
                self.statusLabel.configure(
                    text=(
                        f"{self.successfulRequests} of "
                        f"{graphTotal} stocks updated • "

                        f"{currentTime}"
                    )
                )
            else:
                self.setConnectionStatus(
                    False,
                    "Connection unavailable"
                )
                self.statusLabel.configure(
                    text="Unable to retrieve market data"
                )
            self.root.after(
                1000,
                self.updateAllGraphs
            )

    #runs performance test
    def runPerformanceTest(self):
        if psutil is None:
            messagebox.showerror(
                "Performance Test",
                "The psutil package is required for CPU and memory testing.\n\n"
                "Install it in the same Python environment used by PyScripter with:\n"
                "pip install psutil"
            )
            return
        if self.requestsRunning:
            messagebox.showinfo(
                "Performance Test",
                "Please wait for the current market update to finish."
            )
            return
        symbol = self.mainGraph.symbol
        testWindow = tk.Toplevel(self.root)
        testWindow.title("Performance Test")
        testWindow.geometry("540x470")
        testWindow.configure(bg=cardColour)
        testWindow.resizable(False, False)

        titleLabel = tk.Label(
            testWindow,
            text="Performance Test",
            bg=cardColour,
            fg=textColour,
            font=("Segoe UI Semibold", 18)
        )
        titleLabel.pack(pady=(22, 4))
        descriptionLabel = tk.Label(
            testWindow,
            text=f"Testing {symbol} using 10 API requests",
            bg=cardColour,
            fg=secondaryText,
            font=("Segoe UI", 10)
        )
        descriptionLabel.pack(pady=(0, 12))
        resultLabel = tk.Label(
            testWindow,
            text="Running test...",
            justify="left",
            anchor="w",
            bg=entryColour,
            fg=textColour,
            font=("Consolas", 10),
            padx=18,
            pady=16
        )
        resultLabel.pack(fill=tk.X, padx=25, pady=10)

        closeButton = tk.Button(
            testWindow,
            text="Close",
            command=testWindow.destroy,
            bg=primaryColour,
            fg="white",
            relief=tk.FLAT,
            padx=25,
            pady=8,
            font=("Segoe UI Semibold", 10)
        )
        closeButton.pack(pady=12)

        #runs the test
        def performTest():
            process = psutil.Process(os.getpid())
            cpuCount = psutil.cpu_count(logical=True) or 1
            requestTimes = []
            memoryValues = []
            cpuValues = []
            successfulRequests = 0
            process.cpu_percent(interval=None)
            wallStart = time.perf_counter()
            for testNo in range(1, 11):
                reqStart = time.perf_counter()
                try:
                    response = requests.get(
                        "https://finnhub.io/api/v1/quote",
                        params={
                            "symbol": symbol,
                            "token": apiKey
                        },
                        timeout=8
                    )
                    response.raise_for_status()
                    stockData = response.json()
                    if stockData.get("c", 0):
                        successfulRequests += 1
                except Exception:
                    pass
                requestTime = (
                    time.perf_counter() - reqStart
                ) * 1000
                requestTimes.append(requestTime)
                currentMem = (
                    process.memory_info().rss
                    / (1024 * 1024)
                )
                memoryValues.append(currentMem)
                cpuNow = (
                    process.cpu_percent(interval=None)
                    / cpuCount
                )
                cpuValues.append(cpuNow)
                avgRequest = (
                    sum(requestTimes)
                    / len(requestTimes)
                )

                averageMemory = (
                    sum(memoryValues)
                    / len(memoryValues)
                )

                peakMemory = max(memoryValues)
                avgCpu = (
                    sum(cpuValues)
                    / len(cpuValues)
                )

                liveText = (
                    "RUNNING TEST\n\n"
                    f"Progress:               {testNo}/10\n"
                    f"Successful requests:    {successfulRequests}/{testNo}\n\n"
                    f"Current request time:   {requestTime:.2f} ms\n"
                    f"Average request time:   {avgRequest:.2f} ms\n\n"
                    f"Current memory usage:   {currentMem:.2f} MB\n"

                    f"Average memory usage:   {averageMemory:.2f} MB\n"
                    f"Peak memory usage:      {peakMemory:.2f} MB\n\n"
                    f"Current CPU usage:      {cpuNow:.2f}%\n"
                    f"Average CPU usage:      {avgCpu:.2f}%"
                )
                self.root.after(
                    0,
                    lambda currentText=liveText:
                        resultLabel.configure(
                            text=currentText
                        )
                )
            elapsed = (
                time.perf_counter() - wallStart
            )
            avgRequest = (
                sum(requestTimes)
                / len(requestTimes)
            )
            minRequest = min(requestTimes)
            maximumRequest = max(requestTimes)
            averageMemory = (
                sum(memoryValues)
                / len(memoryValues)
            )
            peakMemory = max(memoryValues)
            avgCpu = (
                sum(cpuValues)
                / len(cpuValues)
            )
            resultText = (
                "PYTHON PERFORMANCE TEST\n"
                "========================================\n\n"
                f"Requests completed:      10\n"
                f"Successful requests:     {successfulRequests}\n\n"
                f"Average request time:    {avgRequest:.2f} ms\n"

                f"Fastest request:         {minRequest:.2f} ms\n"
                f"Slowest request:         {maximumRequest:.2f} ms\n\n"
                f"Average memory usage:    {averageMemory:.2f} MB\n"
                f"Peak memory usage:       {peakMemory:.2f} MB\n\n"

                f"Average CPU usage:       {avgCpu:.2f}%\n"
                f"Total test time:         {elapsed * 1000:.0f} ms"
            )

            self.root.after(
                0,
                lambda: resultLabel.configure(
                    text=resultText
                )
            )
        threading.Thread(
            target=performTest,
            daemon=True
        ).start()

    #updates connection status
    def setConnectionStatus(
        self,
        connected,
        message
    ):
        if connected:
            backgroundColour = greenBackground
            statusColour = green
        else:
            backgroundColour = redBackground
            statusColour = redColour
        self.connectionFrame.configure(
            bg=backgroundColour
        )
        self.connectionDot.configure(
            bg=backgroundColour,
            fg=statusColour
        )
        self.connectionLabel.configure(
            text=message,
            bg=backgroundColour,
            fg=statusColour
        )
if __name__ == "__main__":
    root = tk.Tk()
    app = StockApp(root)
    root.mainloop()
