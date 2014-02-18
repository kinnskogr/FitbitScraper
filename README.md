FitbitScraper
=============

Data, liberate yo-self! Extract intraday values from the data used to populate fitbit's online panels.

## Usage:
* Initial setup:
  mkdir data

* Download the latest data:
  python scraper.py Steps
  >> Login email: ...
  >> Password: ...
  >> Could not find previous data, please enter the record start date.
  >> year: ...
  >> month: ...
  >> day: ...

* Subsequent downloads will start from the date of the latest download
  
## External dependencies:

    BeautifulSoup 
      \-BeautifulSoup (scraper)
      \-SoupStrainer (scraper)
    numpy (scraper)
    selenium 
      \-webdriver (scraper)
