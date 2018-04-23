import pandas as pd
import numpy as np
import urllib3
import certifi
from bs4 import BeautifulSoup
import requests
#
# to handle error: OpenSSL.SSL.SysCallError: (-1, 'Unexpected EOF')
# https://stackoverflow.com/questions/44141655/requests-failing-to-connect-to-a-tls-server/44142250#44142250
#
requests.packages.urllib3.util.ssl_.DEFAULT_CIPHERS = 'DES-CBC3-SHA'
    
def get_table(stock_no, start_date, end_date):

    url = 'https://www.cnyes.com/twstock/ps_historyprice.aspx?code=' + str(stock_no)
    fields = {'ctl00$ContentPlaceHolder1$startText': start_date,
              'ctl00$ContentPlaceHolder1$endText': end_date}

    http = urllib3.PoolManager(
        cert_reqs='CERT_REQUIRED',
        ca_certs=certifi.where()
    )

    http_request = http.request('POST', url, fields)
    soup = BeautifulSoup(http_request.data, 'html.parser')

    # print table data
    data = []
    table = soup.find("table")
    rows = table.find_all('tr')
    
    for row in rows:
        cols = row.find_all('td')
        cols = [ele.text.strip() for ele in cols]
        data.append([ele for ele in cols if ele]) # Get rid of empty values

    print(data)
    return data

get_table(2330, '2018/03/23', '2018/04/23')
