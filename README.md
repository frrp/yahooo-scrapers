
Some Yahoo Finance scrapers.

scripts
-------
* yahoocrawlindex.py -- goes through a massive index of all non-option securities on Yahoo finance. 
                        outputs a list of symbols, checked in as allsyms.txt
* yahoohist.py -- gets historic daily open/high/low/close/volume/adj.close for each symbol
                  writes prices/<sym>.csv
* yahoossi.py -- crawls sector/subsector/industry info for each symbol
* yahoooptions.py -- crawls option series and pricing data
