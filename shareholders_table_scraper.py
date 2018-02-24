from tkinter import Tk, Label, Button, Text
from urllib.parse import urlencode
import pandas as pd
import matplotlib
matplotlib.use('WXAgg')
import matplotlib.pyplot as plt
import urllib3
from bs4 import BeautifulSoup
from PyQt5.QtWidgets import (QWidget, QPushButton, QLineEdit, 
    QInputDialog, QApplication)
import sys

#import datetime
#import time
#import csv
# work around for pyinstaller issue conuld not find the Qt platform plugin "windows" in "".
# https://github.com/pyinstaller/pyinstaller/issues/2857


def get_date_list():
    """
    get_date_list

    """
    date_list = []
    url = 'http://www.tdcc.com.tw/smWeb/QryStock.jsp'

    http = urllib3.PoolManager()
    http_request = http.request('GET', url)
    soup = BeautifulSoup(http_request.data, 'html.parser')
    date_options = soup.findAll('option')

    for date in date_options:
        date_list.append(date.get_text())
    return date_list


def get_table(date_list, stock_no):
    '''
    get_table
    '''

    http = urllib3.PoolManager()
    data = []
    # urlencode() decode bug,  %ACd%B8%DF => %25AC%25B8%25DF
    # work around
    for sca_date in date_list:

        encoded_args = urlencode({
            'SCA_DATE':sca_date,
            'SqlMethod':'StockNo',
            'StockNo':stock_no
            })
        url = 'http://www.tdcc.com.tw/smWeb/QryStock.jsp?'+encoded_args+'&sub=%ACd%B8%DF'
        #print(url)

        try:
            http_request = http.request('POST', url)
            soup = BeautifulSoup(http_request.data, 'html.parser')
            # data at second class=mt table
            table = soup.findAll("table", attrs={"class":"mt"})[1]
        except IndexError as index_error:
            print(index_error)
            return None

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
    print(df_400)
    #print(df_400.describe())
    plt.plot(df_400, label='linear')

    plt.ylabel("people who owned above 400,000 shares")
    plt.title(stock_no)
    plt.savefig(str(stock_no)+'.png')
    plt.close()
    #plt.show()


# class MyFirstGUI:
#     def __init__(self, master):
#         self.master = master
#         master.title("shareholder table")

#         self.label1 = Label(master, text="Input stock number")
#         self.label1.pack()

#         self.text = Text(master, cnf={}, width="20", height="1")
#         self.text.pack()

#         self.submit_button = Button(master, text="Submit", command=self.submit)
#         self.submit_button.pack()

#     def submit(self):
#         """Example of docstring on the __init__ method.

#         """
#         # index from start to end
#         stock_no = self.text.get("1.0",'end-1c')
#         self.text.delete('1.0', 'end-1c')

#         data = get_table(get_date_list(), stock_no)
#         df_shares = clear_data(data)
#         draw(df_shares, stock_no)
#         df_shares.to_csv(str(stock_no)+'.csv', sep=',')


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
# root = Tk()
# my_gui = MyFirstGUI(root)
# root.mainloop()

#print(df.head)
#print(df.dtypes)

#export list of lists to csv
# with open('csvfile.csv', "w") as output:
#     writer = csv.writer(output, lineterminator='\n')
#     writer.writerows(data)
