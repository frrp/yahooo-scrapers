#!/usr/bin/env python
#

import os
import sys
from datetime import * 
import httplib
import urllib
import time
import re

# PARAMS
delay = 2
output_dir = "options"


def main():
    print >> sys.stderr, "usage: reads 1 symbol per line from ./tickers.txt,"
    print >> sys.stderr, "       loads a bunch of yahoo data (eg http://finance.yahoo.com/q/os?s=MSFT&m=2011-08-19)"
    print >> sys.stderr, "       into folder ./options, parses html and writes a giant file: ./yahoooptions.csv"
 

    # LOAD SYMBOLS
    syms_fname = "tickers.txt"
    syms = []
    with open(syms_fname, "r") as f:
        for line in f:
            syms.append(line.strip().upper())
    print >> sys.stderr, "loaded %d tickers from %s"%(len(syms), syms_fname)

    # LOAD EXPIRATION MONTHS
    # Don't worry about exact, just get a superset of available dates.
    today = date.today()
    exps = []
    for i in range(5):
        month = today.month+i
        year = today.year
        if month > 12:
            month -= 12
            year += 1
        exps.append(date(year, month, 1))
    # Add LEAPs
    exps.append(date(today.year+1, 1, 1))
    exps.append(date(today.year+2, 1, 1))
    exps.append(date(today.year+3, 1, 1))


    print >> sys.stderr, "nuking %s..."%output_dir
    nuke_dir(output_dir)
    print >> sys.stderr, "querying..."
    query_yahoo(syms, exps, output_dir)
    print >> sys.stderr, "parsing..."
    with open('yahoooptions.csv', 'w') as f:
        parse_files(output_dir, f)
    print >> sys.stderr, "done!"



def nuke_dir(output_dir):
    os.system("rm -rf %s"%output_dir)
    os.system("mkdir %s"%output_dir)

def query_yahoo(syms, exps, output_dir):
    # QUERY YAHOO FOR EACH ONE
    for sym in syms:
        for exp in exps:
            # YAHOO API
            host = "finance.yahoo.com"
            usym = urllib.quote_plus(sym)
            url = "/q/os?s=%s&m=%04d-%02d"%(usym, exp.year, exp.month)
            print >> sys.stderr, "QUERYING %s%s"%(host,url)

            # BE NICE
            time.sleep(delay)

            # GET HANDLE ERRORS
            #conn = httplib.HTTPConnection(host)
            #conn.request("GET", usym)
            #resp = conn.getresponse()
            #if resp.status != 200:
            #    print >> sys.stderr, "skipping %s, got error %s"%(url, resp.status)
            #    continue
            #html = resp.read()

            # SAVE, PARSE
            html_fname = "%s/%s_%04d%02d.html"%(output_dir,sym,exp.year,exp.month)
            #with open(html_fname, "w") as f:
            #    f.write(html)
            os.system("wget -O %s http://%s%s"%(html_fname, host, url))

# Takes a path to a directory full of .html files, writes parsed stuff to a file object, comma-delimited
def parse_files(output_dir, f_csv):
    # PARSE
    # Sample row:
    # <tr>
    # <td class="yfnc_tabledata1"><a href="/q?s=MSFT110820C00031000">MSFT110820C00031000</a></td>
    # <td class="yfnc_tabledata1" align="right"><b><span id="yfs_l10_msft110820c00031000">0.01</span></b></td>
    # <td class="yfnc_tabledata1" align="right"><span id="yfs_c10_msft110820c00031000"> <b style="color:#000000;">0.00</b></span></td>
    # <td class="yfnc_tabledata1" align="right">N/A</td>
    # <td class="yfnc_tabledata1" align="right"><span id="yfs_a00_msft110820c00031000">0.04</span></td>
    # <td class="yfnc_tabledata1" align="right"><span id="yfs_v00_msft110820c00031000">55</span></td>
    # <td class="yfnc_tabledata1" align="right">1,989</td>
    # <td class="yfnc_tabledata1" align="right"><b><a href="/q/os?s=MSFT&amp;k=31.000000">31.00</a></b></td>
    # <td class="yfnc_h"><a href="/q?s=MSFT110812P00031000">MSFT110812P00031000</a></td>
    # <td class="yfnc_h" align="right">N/A</td>
    # <td class="yfnc_h" align="right"><span id="yfs_c10_msft110812p00031000"> <b style="color:#000000;">0.00</b></span></td>
    # <td class="yfnc_h" align="right"><span id="yfs_b00_msft110812p00031000">4.75</span></td>
    # <td class="yfnc_h" align="right"><span id="yfs_a00_msft110812p00031000">7.75</span></td>
    # <td class="yfnc_h" align="right"><span id="yfs_v00_msft110812p00031000">0</span></td>
    # <td class="yfnc_h" align="right">0</td>
    # </tr>
    
    columns = ["option_type", "symbol", "last", "bid", "ask", "volume", "open_interest", "strike_price"]
    print >> f_csv, ",".join(columns)

    for fname in os.listdir(output_dir):
        print >> sys.stderr, fname
        if not fname.endswith(".html"):
            continue
        html_fname = os.path.join(output_dir, fname)

        # READ HTML FILE 
        html = ""
        with open(html_fname, "r") as f:
            html = f.read()
        regex = '<tr><td class="yfnc_tabledata1.*?</tr>'
        row_regex = (
            '<tr' + 
            '.*?href="/q\\?s=(?P<call_sym>[^"]*)".*?' +
            '(N/A|(?P<call_last>[0-9]+\\.[0-9][0-9])</span>).*?' +
            '(N/A|(?P<call_bid>[0-9]+\\.[0-9][0-9])</span>).*?' +
            '(N/A|(?P<call_ask>[0-9]+\\.[0-9][0-9])</span>).*?' +
            '">(?P<call_volume>[0-9,]+)</span>.*?' +
            '(?P<call_interest>[0-9,]+)</td>.*?' +

            '(?P<strike_price>[0-9]+\\.[0-9][0-9])</a></b></td>.*?' + 

            'href="/q\\?s=(?P<put_sym>[^"]*)".*?' +
            '(N/A|(?P<put_last>[0-9]+\\.[0-9][0-9])</span>).*?' +
            '(N/A|(?P<put_bid>[0-9]+\\.[0-9][0-9])</span>).*?' +
            '(N/A|(?P<put_ask>[0-9]+\\.[0-9][0-9])</span>).*?' +
            '">(?P<put_volume>[0-9,]+)</span>.*?' +
            '(?P<put_interest>[0-9,]+)</td>.*?' +
            '</tr>')
        for row_html in re.findall(regex,html):
            # row found. parse out fields
            match = re.match(row_regex,row_html)
            if not match:
                print >> sys.stderr, "match failed!"
                continue

            # format, send to csv
            vals_fn = lambda option_type: [
                option_type,
                match.group(option_type+'_sym'),
                float(match.group(option_type+'_last') or 'nan'),
                float(match.group(option_type+'_bid') or 'nan'),
                float(match.group(option_type+'_ask') or 'nan'),
                int(match.group(option_type+'_volume').replace(',','')),
                int(match.group(option_type+'_interest').replace(',','')),
                float(match.group('strike_price'))]
            call_vals = vals_fn('call')
            put_vals = vals_fn('put')
            print >> f_csv, ",".join(map(str, call_vals))
            print >> f_csv, ",".join(map(str, put_vals))

# run it!
main()
