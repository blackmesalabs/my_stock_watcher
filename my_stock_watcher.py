# Copyright (c) 2024 Kevin M. Hubbard Black Mesa Labs
# Source file: my_stock_watcher.py
# Date:    12.11.24
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
#   https://stackoverflow.com/questions/78166871/ssl-certificate-verify-failed-yahoo-finance-api-python
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
# stock_list.txt is a clear text file of stock symbols that looks like this:
# [stock_list.txt]
# AMD
# INTC
# NVDA

import sys,platform,os,time;
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
# stock_list = file2list( args[1] );
  stock_list = file2list( "stock_list.txt" );

  loop_mode = False;
  for each in sys.argv:
    if "-loop" in each:
      loop_mode = True;

  loop_forever = True;
  while loop_forever:
    for each_stock in stock_list:
      words = " ".join(each_stock.split()).split(' ') + [None] * 4;
      symbol = words[0];
      stock_info = yf.Ticker( symbol );
      print( display_line(ansi, stock_info ) );
    loop_forever = loop_mode;
    time.sleep( 15*60 );
  return;

def display_line( ansi, stock_info ):
  symbol     = stock_info.info["symbol"];
# name       = stock_info.info["longName"];
  if stock_info.info.get("currentPrice"):
    price_new  = stock_info.info["currentPrice"];
  else:
    price_new  = stock_info.info["bid"];# ^GSPC doesn't have currentPrice

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
  low_percent =   ( price_new / price_low  );
  high_percent =  ( price_new / price_high );

  w52_h = "";
  w52_l = "";
  if high_percent > 0.90:
    w52_h = ansi['bold']+ansi['fg_grn'];
  else:
    w52_h = ansi['dim'];
  if low_percent < 1.10:
    w52_l = ansi['bold']+ansi['fg_red'];
  else:
    w52_l = ansi['dim'];

  str = my_bold;
  str = str + symbol.ljust(6);
  str = str + " " + ("%.2f" % price_new).rjust(7);
# str = str + ansi['dim'];
  str = str + " [" + w52_l + ("%.0f" % price_low  ).ljust(4) + my_color_reset;
  str = str + ansi['dim'] + ":" + w52_h + ("%.0f" % price_high ).rjust(4) + my_color_reset + "]";
  str = str + ansi['reset'];
  str = str + my_color;
  str = str + " " + ("%+.2f" % price_delta).rjust(6);
  str = str + " " + ("%+2.1f%%" % change).rjust(6);
  str = str + my_color_reset;
# str = str + "%f %f" % ( low_percent, high_percent );
  return str;

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
