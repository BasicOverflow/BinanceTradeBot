# KronoBot 1.9.0

* Old Binance Trading bot that has since probably been depricated from the platform. Essentially, 
it is a series of tcp local servers that spawn clients who share information with each other. Uses
websockets to stream live market data and sqlite db's to store/update everything real time.

* If I were to go back to this project, I would definately use something like redis to read/write
the market data and build it around some sort of modern API framework like fastAPI

* Designed to easily integrate new algorithmic strategies, providing the developer with direct
access to all market data as well as common statistical operations on price data, like moving averages,
standard deviations, RSI, etc.

* Also comes with a cool (i think) terminal UI design that the user can interact with
