import requests
from bs4 import BeautifulSoup
import re 

r = requests.get('http://data.sberbank.ru/moscow/ru/quotes/metal/?utm_source=ep&qid190=28/?base=beta?utm_source=ep&qid190=28')
data = r.text
soup = BeautifulSoup(data, "html.parser")
tables = soup.findChildren('table')
# This will get the first (and only) table. Your page may have more.
my_table = tables[0]
# You can find children with multiple tags by passing a list of strings
rows = my_table.findChildren(['th', 'tr'])
i = 0
for row in rows:
    if i==4:
        break
    else:
        cells = row.findChildren('td')
        for cell in cells:
            value = cell.string
            if  value is not None:
                i=i+1
                if i==1:
                    usdbuy=re.sub(r'\s', '', value)
                elif i==2:
                    usdsell=re.sub(r'\s', '', value)
                elif i==3:
                    eurbuy=re.sub(r'\s', '', value)
                elif i==4:
                    eursell=re.sub(r'\s', '', value)
stringmetal = "Золото:\n Покупка:" + usdbuy +"\n Продажа:"+ usdsell +" \nСеребро:\n Покупка:"+ eurbuy +"\n Продажа:"+ eursell

r = requests.get('http://ru.investing.com/commodities/brent-oil')
data = r.text
soup = BeautifulSoup(data, "html.parser")
time = soup.find("span",{"class":"bold pid-8833-time"})
value = soup.find("span",{"id":"last_last"})
change = soup.find("span",{"class":"pid-8833-pc"})
changeproc = soup.find("span",{"class":"pid-8833-pcp"})
stringBrent = "Нефть на "+ str(time.text) +" \n"+ "Brent: " +str(value.text)+" "+str(change.text)+" "+str(changeproc.text)
r = requests.get('http://ru.investing.com/commodities/crude-oil')
data = r.text
soup = BeautifulSoup(data, "html.parser")
valuewti = soup.find("span",{"id":"last_last"})
changewti = soup.find("span",{"class":"pid-8849-pc"})
changeprocwti = soup.find("span",{"class":"pid-8849-pcp"})
stringWTI = "WTI: " +str(valuewti.text) +" "+str(changewti.text)+" "+str(changeprocwti.text)
stringOil = stringBrent+"\n"+stringWTI
stringkot= stringmetal+"\n"+stringOil
print(str(stringkot))
