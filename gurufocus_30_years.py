from urllib.parse import urlencode
import pandas as pd
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import urllib3
import certifi
from bs4 import BeautifulSoup
import sys
import re
import csv

def get_stock_data(stock_symbol):
    '''
    get_stock_data
    '''
    # https://www.gurufocus.com/financials/NAS:SAFM
    http = urllib3.PoolManager(
        cert_reqs='CERT_REQUIRED',
        ca_certs=certifi.where()
        )      

    url = 'https://www.gurufocus.com/financials/'+stock_symbol
    http_request = http.request('POST', url)
    soup = BeautifulSoup(http_request.data, 'html.parser')        
            
    data = []
    col_name_list = ['Stock Symbol', 'Period Type', 'Fiscal Period']
    col_name_tag = []

    # get column names
    titles = soup.find_all('td', {'title':re.compile("[A-Za-z]+")})

    for title in titles:
        link = title.find('a', {'target': '_blank'})         
        if link != None:    
            col_name_tag.append(link)

    # chr(160) = &nbsp; = \xa0
    for col_name in col_name_tag:        
        col_name_list.append(col_name.getText().replace(chr(160),''))
    
    data.append(col_name_list)

    # get rows: one row stands for one fiscal period
    fiscal_period_list = soup.find_all('th', {'class':['style4', 'style5']})
    fiscal_period_col = []
    fisacl_period_length = len(fiscal_period_list)
    
    for fiscal_period in fiscal_period_list[-10:]:
        fiscal_period_col.append(fiscal_period.get_text())
            
    # save last 10 items
    i = fisacl_period_length - 9
    expression_list = [str(i), str(i+1), str(i+2), str(i+3), 'yesttm$', str(i+4), str(i+5), str(i+6), str(i+7), str(i+8)]

    period_list = []
    for expression in expression_list:
        period_list.append({'class':re.compile('[^-]'+expression+'$')})
    
    for i, period in enumerate(period_list):
        div_period = soup.find_all(['div','font'], period)

        # first 5 annual, last 5 quarter
        if i < 5:
            div_list = [stock_symbol, 'A', fiscal_period_col[i]]
        else:
            div_list = [stock_symbol, 'Q', fiscal_period_col[i]]

        for div in div_period:
            div_list.append(div.get_text())
        data.append(div_list)

    # work around for missing collectd data, should be 202 column     # row: 138+15+33=186
    # print(len(data[0]))
    # print(len(data[1]))
    col_diff = len(data[0]) - len(data[1])
    if col_diff > 0:
        for ls in data[1:]:
            for i in range(0, col_diff):
                ls.append('0')

    return data

def list_to_df(data):
    '''
    list_to_df
    '''
    df = pd.DataFrame(data[1:], columns=data[0])

    # remove duplicated column 
    df = df.loc[:, ~df.columns.duplicated()]
    
    # CARE: dont use df.replace(',', ''), it only find whole match string not char
    for col in df:
        df[col] = df[col].str.replace(',', '')
    
    df.iloc[:,3:] = df.iloc[:,3:].apply(pd.to_numeric, errors='coerce').fillna(0)
            
    #print(df.dtypes)
    
    return df

def non_zero(x):
    #df.B.div(df.A.where(df.A != 0, np.nan))
    return x.where(x!=0, np.nan)

def calculate_ratio(df):    
    df.loc[df['Period Type']=='A', ['PE Ratio']] = df['Month End Stock Price'] / non_zero(df['Earnings per Share (Diluted)'])
    df['Price-to-Owner-Earnings'] = df['Month End Stock Price'] / non_zero(df['Owner Earnings per Share (TTM)'])
    df['PB Ratio'] = df['Month End Stock Price'] / non_zero(df['Book Value per Share'])
    df['Price-to-Tangible-Book'] = df['Month End Stock Price'] / non_zero(df['Tangible Book per Share'])
    df['Price-to-Free-Cash-Flow'] = df['Month End Stock Price'] / non_zero(df['Free Cash Flow per Share'])
    df['Price-to-Operating-Cash-Flow'] = df['Month End Stock Price'] / non_zero(df['Operating Cash Flow per Share'])
    df['PS Ratio'] = df['Month End Stock Price'] / non_zero(df['Revenue per Share'])
    #df['PEG Ratio'] = df['Month End Stock Price'] / df['5-Year EBITDA Growth Rate'] 
    #df['EV-to-Revenue'] = df['Enterprise Value'] / df['Revenue']
    #df['EV-to-EBITDA'] = 
    #df['EV-to-EBIT'] = 
    #df['Earnings Yield (Joel Greenblatt) %'] = 
    #df['Forward Rate of Return (Yacktman) %'] = 
    #df['Shiller PE Ratio'] = 
    #df['Dividend Yield %'] = 
    # df['Market Cap'] = 
    # df['Enterprise Value'] = 
    # df['Total Liabilities'] =  df['Total Liabilities'].replace('2,060', '').apply(pd.to_numeric, errors='ignore')
    # df['Total Assets'] =  df['Total Assets'].apply(pd.to_numeric, errors='ignore')
    
    df['Debt Ratio'] = df['Total Liabilities'] / non_zero(df['Total Assets'])
    df['Long Term Funds To Fixed Assets'] = (df['Long-Term Debt'] + df['Total Equity']) / non_zero(df['Property, Plant and Equipment'])
    df['Current Ratio'] = df['Total Current Assets'] / non_zero(df['Total Current Liabilities'])
    df['Quick Ratio'] = (df['Total Current Assets'] - df['Total Inventories']) / non_zero(df['Total Current Liabilities'])
    df['Interest Coverage'] = -1 * df['Operating Income'] / non_zero(df['Interest Expense'])
    df['Net-Net Working Capital'] = (df['Cash And Cash Equivalents'] + 0.75 * df['Accounts Receivable'] + 0.5 * df['Total Inventories'] - df['Total Liabilities'] - df['Preferred Stock']) / non_zero(df['Shares Outstanding (Diluted Average)'])

    for col in df.iloc[:,3:]:    
        df[col] = df[col].astype('float')    

    return df


def concat_stock(stock_symbol_list):
    frames = []
    for stock_symbol in stock_symbol_list:
        data = get_stock_data(stock_symbol)
        df = list_to_df(data)
        df = calculate_ratio(df)
        frames.append(df)
    result = pd.concat(frames)

    return result
    
#stock_symbol_list = ['NAS:SAFM', 'PPC', 'TSN']
#stock_symbol_list = ['PPC']
#stock_symbol_list = ['ANFI']
stock_symbol_list = ['LUV', 'JBLU', 'SAVE'] #SAVE has no 'Days Inventory' column, will cause error


df = concat_stock(stock_symbol_list)
csv_name = '_'.join(stock_symbol_list).replace(':','')
df.to_csv('output/'+csv_name+'.csv', float_format='%.2f')
print(csv_name)      
        
#export list of lists to csv
# with open(csv_name+'.csv', "w", encoding = 'utf8') as output:
#     writer = csv.writer(output, lineterminator='\n')
#     writer.writerows(data)
