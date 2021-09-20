# Qubators_Hackathon
 
## AutoTrader documentation
AutoTrader is a python script that connects to a binance 
server to automate your crypto trading startegies. It is still a prototype 
and as such it doesn't have a graphical user interface yet. To use 
simply set your desired parameters in userVariables.py and define 
your custom strategy in the provided function in the AutoTrader.py 
script, then run the script. Right now it isn't very user friendly but 
it was the best I could come up with in three days working alone. I 
have provided a sample strategy that uses an AI algorithm (LSTM 
regression model), to attempt to predict the price of BTCUSDT a minute 
into the future and make trades based on that prediction. For other 
pairs a very basic moving averages strategy was implemented

The program was asynchronously designed so as to be more time efficient, 
but it hasn't undergone rigorous testing so there will likely be a lot of 
bugs and it only trades one pair at a time. I would not recommend using the 
program with real money but I included an option to try it out on a testnet. 
The program works by fetching the latest prices for a currency pair
then evaluating your strategy every minute to determine whether or not 
to place a buy order. After making a purchase, it will sell if the price 
reaches the specified take profit or stop-loss prices. The program will 
record all its trades in TradeRecords.txt and stop trading at a determined 
trading time. I will submit the project through a public github repository.

### Dependencies
Familiarity with python

Binance account and API keys
Binance testnet account and API keys (optional)

Python

Python modules (can be installed with pip install *****)
- pandas
- numpy
- python-binance
- nest-asyncio (only required if script is run in spyder)
- ta (optional but contains many useful technical analysis indicators)
- sklearn (optional to use AI startegy)
- tensorflow (optional to use AI startegy)

## Update 3
I've been working on a GUI for the program so it can be packaged as an 
application and be more user-friendly. This is a completely new aspect 
of programming for me and I am constantly being exposed to new paradigms 
but I am enjoying the process and hope to be able to deliver a polished 
and useful program. The progress I am made on the UI design can be found 
in the gui folder.

## Update 2
I have finally completed the application GUI. AutoTrader is now a fully 
funcional trading program that is simple and easy to use. I had some 
challenges packaging the tensorflow model so it is not included in this 
version but better models and more trading strategies will be included in 
future updates. 
Includes:
- AutoTrader.exe

## Update 3
New and updated version of AutoTrader. 
- Fixed issues with closing time
- Fixed bugs preventing exiting
- Fixed freezing after long periods
- Improved GUI
- More charts and strategies
- Added functionality to manually close positions

## About the programmer
My name is Agbodesi Imoagene and I'm 19. I currently reside in Ireland 
and am a member of Christ Embassy Dublin. I am an undergraduate computer 
science student at University College Dublin about to begin my second 
year. Although I have relatively little programming experience (I've 
been programming for just under a year) I am very passionate about it 
and eager to learn. I can program in C, python and octave and I have 
spent a lot of time over the summer writing and training all sorts of 
machine learning algorithms. I believe that in the coming months I will
acquire the skills to polish this program and provide many more digital 
solutions.
