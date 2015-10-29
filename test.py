day = 29
detail = 'casa'
category = 'restaurants/bar'
amount = 50,4
currency = 'ars'

col = ['B', 'C', 'D', 'E', 'F']
colnm = [day, detail.title(), category.title(), amount, currency.upper()]

for j in range(len(col)):
        print('{} {}'.format(col[j] + str(2), colnm[j]))

expenses = [(29,10,'algo','otra cosa',10,'ars'),(30,10,'algo mas','mas cosas',20,'usd')]

print(expenses[0][0])

for e in range(len(expenses)):
    print(e)
    for i in range(len(expenses[e])):
        print(str(e) + str(i))
        day = expenses[e][i]
        msheet = expenses[e][i]
        detail = expenses[e][i]
        category = expenses[e][i]
        amount = expenses[e][i]
        currency = expenses[e][i]

    print(day, msheet, detail, category, amount, currency)

