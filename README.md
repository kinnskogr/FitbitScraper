FitbitScraper
=============

Data, liberate yo-self! Extract intraday values from the data used to populate fitbit's online panels.

## Usage:
* Initial setup:
  mkdir data

* Download the latest data:

  python scraper.py
  
  > Login email: \<email for fitbit login>
  
  > Password: \<password for fitbit login>
  
  > Could not find previous data, please enter the record start date.
  
  > year: \<year to start collecting>
  
  > month: \<month to start collecting>
  
  > day: \<day to start collecting>

* Subsequent downloads will start from the date of the latest download
  
## External dependencies:

    BeautifulSoup 
      \-BeautifulSoup (scraper)
      \-SoupStrainer (scraper)
    numpy (scraper)
    selenium 
      \-webdriver (scraper)
