import datetime
from collections import Counter

lista=[1,2,3,3,3,4,4,4,4]
powtorzenia = Counter(lista)
# print(powtorzenia.items())
for item in powtorzenia.items():
    print(item)


print(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))