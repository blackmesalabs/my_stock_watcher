# my_stock_watcher
 Stock watcher for a list of stocks.
 Yahoo killed my.yahoo.com, so I wrote this program to replace them.
 It highlights daily movers beyond 1% and 2% in Red/Green and Bold.
 It also displays 52-week low and highs and highlights when within 10%.

 Example usage:
  %python my_stock_watcher.py ^GSPC AMD AMZN MSFT NVDA
  %python my_stock_watcher.py stock_list.txt
  %python my_stock_watcher.py stock_list.txt -loop
  %python my_stock_watcher.py NFLX -history

 Note: stock_list.txt is a clear text file of stock symbols that looks like this:
 [stock_list.txt]
  AMD
  INTC
  NVDA
