import re
import calendar

keep = 'Emma2310;Yate 59mts;Random Stuff;10,50;ARS2710;300 Mansiones;Random Stuff;50;USD2910;Algo;Djs;30;USDEdited' \
       ' 7:58 PMDONE'

p = re.compile(r'(?P<day>\d{2})(?P<month>\d{2});(?P<detail>[^;]{0,});(?P<category>[^;]{0,});(?P<amount>\d*.\d*);'
               r'(?P<currency>\w{3})')

print(p.findall(keep)[1])
day = p.match(keep).group('day')
month = p.match(keep).group('month')
detail = p.match(keep).group('detail')
category = p.match(keep).group('category')
amount = p.match(keep).group('amount')
currency = p.match(keep).group('currency')

print('{} {} {} {} {} {}'.format(day, calendar.month_name[int(month)], detail, category, amount, currency))
