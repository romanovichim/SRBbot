from pymongo import MongoClient
from pprint import pprint

import datetime

client = MongoClient()

db = client.trylogbotmessage

cursor = db.trylogbotmessage.find()
#По Мише
#cursor = db.trylogbotmessage.find({"id": 47265295})
#cursor = db.trylogbotmessage.find({"id": 47265295},{'_id': False,"id" : 1,'text' : 1,'first_name' : 1 ,'last_name' : 1})

#По Владиславу
#cursor = db.trylogbotmessage.find({"id": 244710945})
#По Сергею Москалеву
#cursor = db.trylogbotmessage.find({"id": 263913859})

#По Сергею Романовичу

#cursor = db.trylogbotmessage.find({"id": 247102782},{'_id': False,'first_name' : 1,'last_name' : 1,'text' : 1,'date':1})
for document in cursor:
    #print(document.get("date"))
    print(datetime.datetime.fromtimestamp(int(document.get("date"))).strftime('%Y-%m-%d %H:%M:%S'))
    print(document)
    
#for document in cursor:
    #print(document)
    
'''
print(
    datetime.datetime.fromtimestamp(
        int("1284101485")
    ).strftime('%Y-%m-%d %H:%M:%S')
)
'''
