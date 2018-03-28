from selenium import webdriver
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from time import sleep
import os
import shutil

def download_xls(stock_no):
    """
    Use selenium to automates browser(Chrome) and download xls file at goodinfo.tw
    
    download Google Chrome Driver from https://www.seleniumhq.org/download/
    chromedriver.exe need in the variable 'PATH'
    
    """

    # options = webdriver.ChromeOptions()
    # options.add_argument("--headless")
    # driver = webdriver.Chrome(chrome_options=options)
    driver = webdriver.Chrome()

    driver.get('https://goodinfo.tw/StockInfo/EquityDistributionClassHis.asp?STOCK_ID=' + str(stock_no))

    try:
        #
        # todo: use id='selEquityDistributionCatHis' replace tag_name='select'
        #
        WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.TAG_NAME, "select"))
        )
    except:
        print('Can not get ' + str(stock_no))
    else:
        select = Select(driver.find_element_by_tag_name("select"))
        select.select_by_visible_text('依持股人數顯示')
        sleep(2)
        driver.find_element_by_css_selector('input[type="button"]').click()
        sleep(2)

        # rename download file
        file_path = 'C:\\Users\\Alex\\Downloads'
        new_file_name = str(stock_no) + '.xls'
        file_name = max(
            [file_path + "\\" + f for f in os.listdir(file_path)], key=os.path.getctime)
        shutil.move(os.path.join(file_path, file_name),
                    os.path.join(file_path, new_file_name))
        print(os.path.join(file_path, new_file_name))

    finally:
        driver.quit()


download_xls(1234)

#
# Add header to avoid '請勿透過網站內容下載軟體查詢本網站'
#
# headers = {'user-agent': 'Mozilla / 5.0 (Windows NT 10.0 Win64 x64) AppleWebKit / 537.36 (KHTML, like Gecko) Chrome / 65.0.3325.181 Safari / 537.36'}
# http_request = http.request('GET', url, headers=headers)
