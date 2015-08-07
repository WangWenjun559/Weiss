# Daily Scrapers
  
  This directory contains the 4 scrapers for 4 data sources, including IMDB, GMA, MetaFilter, Zumato. 
  Each scrapers are called by the `dailyScraper.sh` at given frequency as a crontab job. Each scripts 
  are pretty well self documented, but there are still a few notes for using these scrapers.

## IMDB
  
  To use IMDB scraper, please make sure you have `python 2.7` installed and `IMDbPY`. Furthermore, a few
  changes for the `IMDbPY` need to be done in order to support the scraping. The changed file are also
  located in the repo. You can just replace thses file at the proper place of the python package directory.
