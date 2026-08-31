# real-stock-time-app
real-stock-time-app
# Real-Time Stock Market Application
This repository contains the two programs developed as part of my MSc Computer Science project. The project was implemented to investigate the differences between Python and Java when producing software that handles and displays real-time stock market data.
Two separate applications were produced, with one developed using Python and the other using Java. Both programs were designed to provide similar functionality, allowing the development and performance of each language to be compared under similar conditions.
## Project Structure
The repository contains both implementations of the project.
### Python Implementation
`PythonStockImplementation.py`
The Python application was developed using Tkinter for the user interface and Matplotlib for displaying and updating the stock graphs.
### Java Implementation
`MasterProject/src/application/StockApp.java`
The Java application was developed using Java Swing for the user interface, with the stock graphs being drawn and updated as new stock prices are received.
## Application Features
Both programs were developed around the same main requirements, including:
- A large main stock graph
- Three smaller stock graphs
- Default graphs for TSLA, AAPL and AMZN
- A search function for entering different stock codes
- Input validation for stock searches
- Regular retrieval of current stock prices
- Live updating stock graphs
- Handling of unavailable or incorrect stock data
- Performance testing functionality
The main graph can be changed by entering a stock code into the search bar, while the smaller graphs continuously display a selection of default stocks.
## Performance Testing
Performance testing was included within both programs to allow measurements to be collected from each implementation. The tests consider API response time, memory usage, CPU usage, successful requests and the overall time required to complete the test.
This allowed results to be collected from both programs under similar conditions and used within the final comparison between Python and Java.
## Project Purpose
The stock market application provides a practical example of a real-time system that can be implemented using both languages. The intention of the project is to use the two applications to explore differences in development, functionality and performance rather than to produce a commercial stock trading system.
The wider project considers areas including development time, available tools and frameworks, memory usage, CPU usage, performance and the challenges experienced during the implementation of both programs.
## Dissertation
The development process, methodology, testing, results and final comparison of the two implementations are discussed in further detail within the accompanying MSc Computer Science dissertation. The code within this repository is provided as supporting material for the project.
