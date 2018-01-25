"""Example Google style docstrings.

This module demonstrates documentation as specified by the `Google Python
Style Guide`_. Docstrings may extend over multiple lines. Sections are created
with a section header and a colon followed by a block of indented text.

Example:
    Examples can be given using either the ``Example`` or ``Examples``
    sections. Sections support any reStructuredText formatting, including
    literal blocks::

        $ python example_google.py

Section breaks are created by resuming unindented text. Section breaks
are also implicitly created anytime a new section starts.

Attributes:
    module_level_variable1 (int): Module level variables may be documented in
        either the ``Attributes`` section of the module docstring, or in an
        inline docstring immediately following the variable.

        Either form is acceptable, but the two should not be mixed. Choose
        one convention to document module level variables and be consistent
        with it.

Todo:
    * web scraper of http://www.tdcc.com.tw/smWeb/QryStock.jsp
    * user enter stock number, the module will get shareholders table within a year.
    * output a csv file within a year.
    * output a png file for above 400,000 sharesholder changes within a year.

"""
from tkinter import Tk, Label, Button, Text
from urllib.parse import urlencode
import pandas as pd
import matplotlib
matplotlib.use('WXAgg')
import matplotlib.pyplot as plt
import urllib3
from bs4 import BeautifulSoup
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


class MyFirstGUI:
    """The summary line for a class docstring should fit on one line.

    If the class has public attributes, they may be documented here
    in an ``Attributes`` section and follow the same formatting as a
    function's ``Args`` section. Alternatively, attributes may be documented
    inline with the attribute's declaration (see __init__ method below).

    Properties created with the ``@property`` decorator should be documented
    in the property's getter method.

    Attributes:
        attr1 (str): Description of `attr1`.
        attr2 (:obj:`int`, optional): Description of `attr2`.

    """
    def __init__(self, master):
        """Example of docstring on the __init__ method.

        The __init__ method may be documented in either the class level
        docstring, or as a docstring on the __init__ method itself.

        Either form is acceptable, but the two should not be mixed. Choose one
        convention to document the __init__ method and be consistent with it.

        Note:
            Do not include the `self` parameter in the ``Args`` section.

        Args:
            param1 (str): Description of `param1`.
            param2 (:obj:`int`, optional): Description of `param2`. Multiple
                lines are supported.
            param3 (:obj:`list` of :obj:`str`): Description of `param3`.

        """
        self.master = master
        master.title("shareholder table")

        self.label1 = Label(master, text="Input stock number")
        self.label1.pack()

        self.text = Text(master, cnf={}, width="20", height="1")
        self.text.pack()

        self.submit_button = Button(master, text="Submit", command=self.submit)
        self.submit_button.pack()

    def submit(self):
        """Example of docstring on the __init__ method.

        """
        # index from start to end
        stock_no = self.text.get("1.0",'end-1c')
        self.text.delete('1.0', 'end-1c')

        data = get_table(get_date_list(), stock_no)
        df_shares = clear_data(data)
        draw(df_shares, stock_no)
        df_shares.to_csv(str(stock_no)+'.csv', sep=',')


root = Tk()
my_gui = MyFirstGUI(root)
root.mainloop()

#print(df.head)
#print(df.dtypes)

#export list of lists to csv
# with open('csvfile.csv', "w") as output:
#     writer = csv.writer(output, lineterminator='\n')
#     writer.writerows(data)
