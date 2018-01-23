from urllib.request import urlopen
from urllib.request import HTTPError
import re
from bs4 import BeautifulSoup

def getTitle(url):
    try:
        html = urlopen(url)
    except HTTPError as e:
        return None
    try:
        bsObj = BeautifulSoup(html.read(), 'html.parser')
        title = bsObj.body.h1
    except AttributeError as e:
        return None
    return title



title = getTitle("http://pythonscraping.com/pages/page1.html")

if title == None:
    print("Title could not be found")
else:
    print(title)



## ch2

html = urlopen("http://www.pythonscraping.com/pages/warandpeace.html")
bsObj = BeautifulSoup(html, 'html.parser')
nameList = bsObj.findAll("span", {"class":"green"})
for name in nameList:
    print(name.get_text())


## ch2.1

html = urlopen("http://www.pythonscraping.com/pages/page3.html")
bsObj = BeautifulSoup(html, 'html.parser')

# for child in bsObj.find("table", {"id": "giftList"}).children:
#     print(child)
images = bsObj.findAll("img", {"src":re.compile("\.\.\/img\/gifts\/img.*\.jpg")})
for image in images:
    print(image["src"])