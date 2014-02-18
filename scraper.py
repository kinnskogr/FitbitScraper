'''
Data, liberate yo-self! Extract intraday values from the data used to populate fitbit's online panels.

Requires BeautifulSoup and Selenium.
'''

__author__  = 'Emanuel Strauss'
__email__   = 'emanuel.strauss@gmail.com'
__license__ = 'GPL'
__version__ = '0.1'

from BeautifulSoup import BeautifulSoup, SoupStrainer
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from datetime import datetime, timedelta
import sys
import re
import numpy as np

def fitbitLogin(email, password):
    '''
    Find the login form, fill the fields, and authenticate.
    
    Returns the authenticated driver.
    '''
    
    browser = webdriver.Firefox()
    
    browser.get('https://www.fitbit.com/login')
    
    elem_login = browser.find_element_by_id('loginForm')
    
    elem_email = elem_login.find_element_by_name('email')
    elem_email.send_keys(email)
    
    elem_passwd = elem_login.find_element_by_name('password')
    elem_passwd.send_keys(password)
    
    elem_login.submit()

    return browser

def pullIntradayData(browser, day, month, year=2014, activity='Steps'):
    '''
    Get the source code containing the intraday activity chart data
    Activity can be Steps, Floors, or CaloriesBurned
    
    Returns the source code in UTF-8.
    '''

    url = 'http://www.fitbit.com/activities/%d/%02d/%02d#intraday%sChar' % (year, month, day, activity)
    browser.get(url)
    s = browser.page_source
    
    return s

def scrapeIntradayData(html):
    '''
    Pull the datapoints out of an activity chart (Steps, Floors, Calories Burned).
    
    Returns the counts as a list, and the activity type.
    '''
    
    strain_intraday_data = SoupStrainer(name='section', attrs={'class':'chart selected', 'id':re.compile('intraday.*Chart')})
    strain_data_point    = SoupStrainer(name='rect'   , attrs={'width':'1'})
    
    soup = BeautifulSoup(html, parseOnlyThese=strain_intraday_data)
    # I think there should only ever be one chart selected
    if len(soup.contents) > 1:
        print 'This should not have happened!'
        print soup
        assert(len(soup.contents) == 1)   
    soup = soup.contents[0]

    data_points = soup.findAll(strain_data_point)
    data_points = np.array([(int(i.get('x')), int(i.get('height'))) for i in data_points])
    
    return data_points, soup.get('id')[:-5]

def pullSleepData(browser, day, month, year=2014): 
    '''
    URL will look like this:
    view-source:http://www.fitbit.com/graph/getGraphData?userId=27VWVX&type=intradaySleep&arg=100280114&period=1d&dataVersion=990&version=amchart&dateTo=2014-01-24&chart_type=column2d&amp;data_file=&amp;preloader_color=#999999&amp;chart_id=sleepPatternObject100280114
    '''
    pass

def scrapeSleepData(xml):
    '''
    Pull the sleep datapoints out of the XML.
    
    Returns the counts as a list
    '''
    
    strain_sleep_data  = SoupStrainer(name='data')
    strain_data_graph  = SoupStrainer(name='graph', attrs={'gid':'0'})
    strain_data_points = SoupStrainer(name='value')
    
    soup = BeautifulSoup(xml, parseOnlyThese=strain_sleep_data)
    assert(len(soup.contents) == 1)
    soup = soup.contents[0]
    
    data_points = soup.findAll(strain_data_graph)
    assert(len(data_points) == 1)
    data_points = data_points[0].findAll(strain_data_points)

    mapper = {'asleep'   : 0,
              'resltess' : 1,
              'awake'    : 2,
              }
    output = []
    for d in data_points:
        print d
        val = d.get('description').split(' ')
        output.append((mapper[val[0]], val[2]))
    #data_points = np.array([(mapper[i.get('description').split(' ')[0]], int(i.get('xid'))) for i in data_points])
    return output

def writeSeries(data, source, day, month, year=2014, out_dir='data'):
    '''
    Convert data to time series and write to csv. Output will be
    written to the 'out_dir', and file names will be constructed using
    the date and activity type.
    
    TODO -- Hook to dump to a DB.
    '''
    
    origin = datetime(year,month,day)
    steps = timedelta(seconds=int(60*5))

    date = [origin + (i*steps) for i in xrange(len(data))]
    
    ofile = open('%s/%s %d-%02d-%02d.csv' % (out_dir, source, year, month, day), 'w')
    for d in zip(date, data[:,1]):
        ofile.write('%s,%d\n' % d)

def checkLastDL(source, out_dir='data'):
    '''
    Check the date of the last download matching the data source name.
    '''
    
    import os
    
    dates = [fname.split(' ')[1].split('.')[0] for fname in os.listdir(out_dir) if source in fname]
    try:
        year, month, day = [int(d) for d in dates[-1].split('-')]
    except:
        print 'Could not find previous data, please enter the record start date.'
        print 'year:',
        year = int(raw_input())
        print 'month:',
        month = int(raw_input())
        print 'day:',
        day = int(raw_input())
    
    return year, month, day
    
def getDateRange(start_year, start_month, start_day,
                 end_year, end_month, end_day,
                 source, out_dir = 'data'):
    '''
    Utility function to srape the data over a given range of dates.
    '''

    from time import sleep
    from random import random

    cur  = datetime(start_year, start_month, start_day)
    end  = datetime(end_year, end_month, end_day)
    step = timedelta(1)
    while cur <= end:
        print cur.day, cur.month, cur.year
        html = pullIntradayData(browser, cur.day, cur.month, cur.year)
        data_points, source = scrapeIntradayData(html)
        if len(data_points) > 0:
            writeSeries(data_points, source, cur.day, cur.month, cur.year, out_dir)
        sleep (5*random())
        cur += step

def getLatestData(start_year, start_month, start_day,
                  source, out_dir = 'data'):
    '''
    Utility wrapper funciton to get data from a given date to the current date.
    '''

    from datetime import datetime
    
    now = datetime.now()
    
    getDateRange(start_year, start_month, start_day,
                 now.year, now.month, now.day,
                 source, out_dir)

if __name__ == '__main__':
    import sys
    source = 'Steps' if len(sys.argv) < 2 else sys.argv[1]

    import getpass
    print 'Login email: ',
    email = raw_input()
    passwd = getpass.getpass()

    year, month, day = checkLastDL(source)

    browser = fitbitLogin(email, passwd)
    getLatestData(year, month, day, source)

