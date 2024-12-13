# Copyright (c) 2024 Kevin M. Hubbard Black Mesa Labs
# Source file: my_stock_watcher.py
# Date:    12.13.24
# Author:  Kevin M. Hubbard
# Description: Given a list of stock symbols, use yfinance to look up how the
#              the stock is doing today. Any movement above 1% is highlighted
#              in red or green text. Any movement above 2% is also made bold.
#
# License:
# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation; either version 3 of the License, or (at your option) any later
# version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.
# See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA

# pip install yfinance
#
# If SSL Failure, do the following per:
#   https://stackoverflow.com/questions/78166871/
#         ssl-certificate-verify-failed-yahoo-finance-api-python
# Modify data.py in c:\python\Lib\site-packages\yfinance\data.py
#  to add "verify=False" to web call
#
#   response = self._session.get(
#           url='https://fc.yahoo.com',
#           headers=self.user_agent_headers,
#           proxies=proxy,
#           timeout=timeout,
#           allow_redirects=True, verify=False)
# 
# Example usage:
#  %python my_stock_watcher.py ^GSPC AMD AMZN MSFT NVDA
#  %python my_stock_watcher.py stock_list.txt
#  %python my_stock_watcher.py stock_list.txt -loop
#  %python my_stock_watcher.py NFLX -history
#
# Note: stock_list.txt is a clear text file of stock symbols that looks like this:
# [stock_list.txt]
#  AMD
#  INTC
#  NVDA
# History:
# 2024.12.11 : Created
# 2024.12.12 : Added 52wk 10% low,high color highlighting
# 2024.12.13 : Added history plotting
#####################################################################################
import sys,platform,os,time,datetime;
import yfinance as yf

def main():
  os_sys = platform.system();  # Windows vs Linux
  if os_sys == "Windows":
    os.system("color");# Enable ANSI in Windows
  esc = "\033";
  # See https://gist.github.com/fnky/458719343aabd01cfb17a3a4f7296797
  ansi = {'esc':esc,'cls':esc+"[2J",'reset':esc+"[0m",
          'fg_blk':esc+"[30m",'fg_red':esc+"[31m",'fg_grn':esc+"[32m",
          'fg_ylw':esc+"[33m",'fg_blu':esc+"[34m",'fg_mgt':esc+"[35m",
          'fg_cya':esc+"[36m",'fg_wht':esc+"[37m",'fg_dft':esc+"[39m",
          'bg_blk':esc+"[40m",'bg_red':esc+"[41m",'bg_grn':esc+"[42m",
          'bg_ylw':esc+"[43m",'bg_blu':esc+"[44m",'bg_mgt':esc+"[45m",
          'bg_cya':esc+"[46m",'bg_wht':esc+"[47m",'bg_dft':esc+"[49m",
          'bold':esc+"[1m",'dim':esc+"[2m",'italic':esc+"[3m",
          'underline':esc+"[4m",'inverse':esc+"[7m",'strike':esc+"[9m",
         };

  args = sys.argv + [None]*4;# args[0] is "foo.py"
 
  stock_list = []; 
  loop_mode    = False;
  history_mode = False;
  for each in sys.argv[1:]:
    if "-history" in each:
      history_mode = True;
    if "-loop" in each:
      loop_mode = True;
      loop_interval = 15;# Minutes between updates
  for each in sys.argv[1:]:
    if "-" not in each:
      if os.path.exists( each ):
        stock_list = file2list( each );
      else:
        stock_list += [ each ];

  loop_forever = True;
  while loop_forever:
    print( time.ctime() );
    for each_stock in stock_list:
      words = " ".join(each_stock.split()).split(' ') + [None] * 4;
      symbol = words[0];
      if history_mode:
        plot_history(ansi, symbol );
      stock_info = yf.Ticker( symbol );
      print( display_line(ansi, stock_info ) );
    loop_forever = loop_mode;
    if loop_forever:
      time.sleep( loop_interval*60 );
  return;

def plot_history( ansi, stock_symbol ):
  # period: data period to download (either use period parameter or use start and end) 
  #   “1d”, “5d”, “1mo”, “3mo”, “6mo”, “1y”, “2y”, “5y”, “10y”, “ytd”, “max”
  # interval: data interval:
  #   “1m”, “2m”, “5m”, “15m”, “30m”, “60m”, “90m”, “1h”, “1d”, “5d”, “1wk”, “1mo”, “3mo”
  # start: If not using period – in the format (yyyy-mm-dd) or datetime.
  # end: If not using period – in the format (yyyy-mm-dd) or datetime.
  df = yf.download( stock_symbol, period='5y', interval="1mo")
  price_list = [];
  for i in range(0,len(df) ):
    price_list += [ ( df.iloc[i].name, df.iloc[i]["Close"].iloc[0] ) ];
  max_value = max(price_list, key=lambda item: item[1])[1];
  scale = max_value / 70;
  for (each_date, each_price) in price_list:
    txt = str(each_date).split(' ')[0] + ":";
    txt += " "*int( each_price / scale );
    txt = txt + "$%d" % int( each_price );
    print(txt);
  return

def display_line( ansi, stock_info ):
  symbol     = stock_info.info["symbol"];
# name       = stock_info.info["longName"];
  if stock_info.info.get("currentPrice"):
    price_new  = stock_info.info["currentPrice"];
  elif stock_info.info.get("bid"):
    price_new  = stock_info.info["bid"];# ^GSPC doesn't have currentPrice
  else:
    price_new = 0;

  price_old  = stock_info.info["previousClose"];
  price_low  = stock_info.info["fiftyTwoWeekLow"];
  price_high = stock_info.info["fiftyTwoWeekHigh"];
  change = 100.0 * ( 1.00 - ( price_old / price_new ) );
  price_delta = price_new - price_old;

  my_color_reset = ansi['reset'];
  my_bold = "";
  if ( change > 2 ):
    my_color = ansi['fg_grn']+ansi['bold'];
    my_bold  = ansi['bold'];
  elif ( change > 1 ):
    my_color = ansi['fg_grn']+ansi['dim'];
  elif ( change < -2 ):
    my_color = ansi['fg_red']+ansi['bold'];
    my_bold  = ansi['bold'];
  elif ( change < -1 ):
    my_color = ansi['fg_red']+ansi['dim'];
  else:
    my_color = ansi['dim'];

  # Highlight if within 10% of 52wk Low or High
  low_percent  = ( price_new / price_low  );
  high_percent = ( price_new / price_high );

  w52_h = "";
  w52_l = "";
  if ( high_percent > 0.90 ):
    w52_h = ansi['bold']+ansi['fg_grn'];
  else:
    w52_h = ansi['dim'];
  if ( low_percent < 1.10 ):
    w52_l = ansi['bold']+ansi['fg_red'];
  else:
    w52_l = ansi['dim'];

  txt = my_bold;
  txt = txt + symbol.ljust(6);
  txt = txt + " " + ("%.2f" % price_new).rjust(7);
  txt = txt + my_color_reset;
  txt = txt + " [" + w52_l + ("%.0f" % price_low  ).ljust(4) + my_color_reset;
  txt = txt + ansi['dim'] + ":" + w52_h + ("%.0f" % price_high ).rjust(4) + my_color_reset + "]";
  txt = txt + ansi['reset'];
  txt = txt + my_color;
  txt = txt + " " + ("%+.2f" % price_delta).rjust(6);
  txt = txt + " " + ("%+2.1f%%" % change).rjust(6);
  txt = txt + my_color_reset;
  return txt;

def file2list( file_name ):
  file_in  = open( file_name, 'r' );
  file_list = file_in.readlines();
  file_in.close();
  file_list = [ each.strip('\n') for each in file_list ];# list comprehension
  return file_list;

def list2file( file_name, my_list ):
  file_out  = open( file_name, 'w' );
  for each in my_list:
    file_out.write( each + "\n" );
  file_out.close();
  return;

main = main();
