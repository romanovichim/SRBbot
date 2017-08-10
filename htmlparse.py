import requests
from bs4 import BeautifulSoup
import re 

r = requests.get('http://data.sberbank.ru/moscow/ru/quotes/currencies/?base=beta')
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
string = "USD(Доллар США):\n Покупка:" + usdbuy +"\n Продажа:"+ usdsell +" \nEUR(Евро):\n Покупка:"+ eurbuy +"\n Продажа:"+ eursell
print(string)

