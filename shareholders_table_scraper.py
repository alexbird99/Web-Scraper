import pandas as pd
import matplotlib.pyplot as plt
import urllib3
from urllib.parse import urlencode
from bs4 import BeautifulSoup
from PyQt5.QtWidgets import QWidget, QPushButton, QLineEdit, QInputDialog, QApplication
import sys
import ast

def get_date_list():
    """
    get_date_list

    """
    
    date_list = []
    url = 'http://www.tdcc.com.tw/smWeb/QryStockAjax.do?REQ_OPR=qrySelScaDates'

    http = urllib3.PoolManager()
    http_request = http.request('POST', url)

    if http_request.status == 200:
        soup = BeautifulSoup(http_request.data, 'html.parser')
        # convert string list to list
        date_list = ast.literal_eval(soup.text)
            
    return date_list


def get_table(date_list, stock_no):
    '''
    get_table
    '''    

    http = urllib3.PoolManager()
    data = []

    for sca_date in date_list:        
        # encoded_args = urlencode({
        #     'scaDates':sca_date,
        #     'scaDate':sca_date,
        #     'SqlMethod':'StockNo',
        #     'StockNo':stock_no,
        #     'radioStockNo':stock_no,
        #     'StockName':'',
        #     'REQ_QPR':'SELECT',
        #     'clkStockNo':stock_no,
        #     'clkStockName':''
        #     })
                        
        #url = 'http://www.tdcc.com.tw/smWeb/QryStockAjax.do?scaDates=20180316&scaDate=20180316&SqlMethod=StockNo&StockNo=1234&radioStockNo=1234&StockName=&REQ_OPR=SELECT&clkStockNo=1234&clkStockName='
        url = 'http://www.tdcc.com.tw/smWeb/QryStockAjax.do?scaDates=%s&scaDate=%s&SqlMethod=StockNo&StockNo=%s&radioStockNo=%s&StockName=&REQ_OPR=SELECT&clkStockNo=%s&clkStockName=' % (sca_date, sca_date, stock_no, stock_no, stock_no)
                
        http_request = http.request('POST', url)
        if http_request.status != 200:
            continue
        soup = BeautifulSoup(http_request.data, 'html.parser')            
        # data at second class=mt table
        table = soup.findAll("table", attrs={"class":"mt"})[1]

        table_body = table.find('tbody')
        rows = table_body.find_all('tr')

        for row in rows:
            cols = row.find_all('td')
            cols = [ele.text.strip() for ele in cols]
            #data.append([ele for ele in cols if ele]) # Get rid of empty values
            data.append([sca_date] + [ele for ele in cols])
    
    return data

def clear_data(data):
    '''
    clear_data
    '''
    df_shares = pd.DataFrame(data)
    df_shares.columns = ["date", "level", "shares", "people", "shares_per_people", "proportion"]

    df_shares['level'] = pd.to_numeric(df_shares['level'], errors='coerce', downcast='unsigned')
    df_shares = df_shares[(df_shares.level <= 15) & (df_shares.level >= 1)]

    #  remove ',' in string, then transfer to numeric
    removed_spp = df_shares['shares_per_people'].str.replace(',', '')
    removed_people = df_shares['people'].str.replace(',', '')

    df_shares['date'] = pd.to_datetime(df_shares['date'], errors='raise')
    df_shares['shares_per_people'] = pd.to_numeric(removed_spp, errors='raise', downcast='unsigned')
    df_shares['people'] = pd.to_numeric(removed_people, errors='raise', downcast='unsigned')
    df_shares['proportion'] = pd.to_numeric(df_shares['proportion'], downcast='float')

    return df_shares

def draw(df_shares, stock_no):
    df_400 = df_shares[df_shares.level >= 12].groupby('date')['people'].sum()
    plt.plot(df_400, label='linear')

    plt.ylabel("people who owned above 400,000 shares")
    plt.title(stock_no)
    plt.savefig(str(stock_no)+'.png')
    plt.close()    

class Example(QWidget):
    
    def __init__(self):
        super().__init__()
        
        self.initUI()
        
        
    def initUI(self):      

        self.btn = QPushButton('Submit', self)
        self.btn.move(160, 20)
        self.btn.clicked.connect(self.getStockNo)
        
        self.le = QLineEdit(self)
        self.le.move(20, 20)
        
        self.setGeometry(300, 300, 240, 60)
        self.setWindowTitle('input stock number')
        self.show()
        
        
    def getStockNo(self):        
        stock_no = self.le.text()
        self.le.clear()

        data = get_table(get_date_list(), stock_no)
        df_shares = clear_data(data)
        draw(df_shares, stock_no)
        df_shares.to_csv(str(stock_no)+'.csv', sep=',')            
        
if __name__ == '__main__':        
    app = QApplication(sys.argv)
    ex = Example()
    sys.exit(app.exec_())

# stock_no = '1234'
# date_list = get_date_list()
# get_table(date_list, stock_no)

#export list of lists to csv
# with open('csvfile.csv', "w") as output:
#     writer = csv.writer(output, lineterminator='\n')
#     writer.writerows(data)
