import calendar

enormal = [('12', '01', 'detalle', 'categ', 'monto', 'currency'), ('13', '02', 'detalle1', 'categ1', 'monto1',
                                                                   'currency1')]
normal = ['B', 'C', 'D', 'E', 'F']

esig = [('SIG', '01', 'detalle', 'monto', 'currency'), ('SIG', '02', 'detalle1', 'monto1', 'currency1')]

signature = ['I', 'J', 'K']

# for data in exp:
#     for i in range(len(data)):
#         print(data[i])


def update_sheet(exp, col):
    lastrow = 3

    for data in exp:
        lastrow += 1
        msheet = calendar.month_name[int(data[1])]
        temp = list(data)
        temp.pop(1)

        if temp[0].upper() == 'SIG':
            temp.pop(0)

        for i in range(len(temp)):
                print('{}{} {} {}'.format(col[i], str(lastrow), temp[i], msheet))


print('NORMAL:')
update_sheet(enormal, normal)

print('SIGNATURE:')
update_sheet(esig, signature)

