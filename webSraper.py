import pandas as pd
import urllib3
from urllib.parse import urlencode
from bs4 import BeautifulSoup
import datetime
import time
import csv
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from tkinter import Tk, Label, Button, Text

# urlencode() decode bug,  %ACd%B8%DF => %25AC%25B8%25DF
# work around

def getDateList():
    dateList = []
    url = 'http://www.tdcc.com.tw/smWeb/QryStock.jsp'

    http = urllib3.PoolManager()    
    r = http.request('GET', url)
    soup = BeautifulSoup(r.data, 'html.parser')
    dateOptions = soup.findAll('option')
    
    for date in dateOptions:
        dateList.append(date.get_text())
    return dateList


def getTable(dateList, stockNo):        
    
    http = urllib3.PoolManager()
    data=[]                

    for sca_date in dateList:

        encoded_args = urlencode({            
            #'SCA_DATE':sca_date.strftime("%Y%m%d"),
            'SCA_DATE':sca_date,
            'SqlMethod':'StockNo',
            'StockNo':stockNo
            })    

        url = 'http://www.tdcc.com.tw/smWeb/QryStock.jsp?'+encoded_args+'&sub=%ACd%B8%DF'
        #print(url)                

        try:
            r = http.request('POST', url)
            soup = BeautifulSoup(r.data, 'html.parser')
            # data at second class=mt table
            table = soup.findAll("table", attrs={"class":"mt"})[1]
        except IndexError as e:
            print(e)                        
            return None

        
        table_body = table.find('tbody')        
        rows = table_body.find_all('tr')        

        for row in rows:
            
            cols = row.find_all('td')
            cols = [ele.text.strip() for ele in cols]
            #data.append([ele for ele in cols if ele]) # Get rid of empty values                        
            data.append([sca_date] + [ele for ele in cols])
                    
    return data

def clearData(data):
    df = pd.DataFrame(data)
    df.columns= ["date", "level", "shares", "people", "shares_per_people", "proportion"]

    df['level'] = pd.to_numeric(df['level'], errors='coerce', downcast='unsigned')
    df = df[(df.level <= 15) & (df.level >= 1)]

    df['date'] = pd.to_datetime(df['date'], errors='raise')
    #  remove ',' in string, then transfer to numeric
    df['shares_per_people'] = pd.to_numeric(df['shares_per_people'].str.replace(',', ''), errors='raise', downcast='unsigned')
    df['people'] = pd.to_numeric(df['people'].str.replace(',', ''), errors='raise', downcast='unsigned')
    df['proportion'] = pd.to_numeric(df['proportion'], errors='raise', downcast='float')

    return df
    

def draw(df, stockNo):
    df_400 = df[df.level >= 12].groupby('date')['people'].sum()
    print(df_400)
    #print(df_400.describe())
    plt.plot(df_400, label='linear')
    
    plt.ylabel("people who owned above 400,000 shares")
    plt.title(stockNo)
    plt.savefig(str(stockNo)+'.png')
    plt.close()
    #plt.show()


class MyFirstGUI:
    def __init__(self, master):
        self.master = master
        master.title("A simple GUI")

        self.text = Text(master, cnf={}, width="30", height="1")
        self.text.pack()

        self.submit_button = Button(master, text="Submit", command=self.submit)
        self.submit_button.pack()

    def submit(self):
        stockNo = self.text.get("1.0",'end-1c')
        #self.text.
            
        data = getTable(getDateList(), stockNo)
        df = clearData(data)
        draw(df, stockNo)        
        df.to_csv(str(stockNo)+'.csv', sep=',')


root = Tk()
my_gui = MyFirstGUI(root)
root.mainloop()

#print(df.head)
#print(df.dtypes)

#export list of lists to csv
# with open('csvfile.csv', "w") as output:
#     writer = csv.writer(output, lineterminator='\n')  
#     writer.writerows(data)
