import re
import calendar

note = '0212;random;random stuff;100;ars;VISA010212;random;random stuff;100;ars;debito0212;random;random stuff;' \
       '100;ars;master120212;random;random stuff;100;ars;efvo'

expense = re.compile(
    r'(?P<day>\d{2})(?P<month>\d{2});(?P<detail>[^;]*);(?P<category>[^;]*);'
    r'(?P<amount>[^;]*);(?P<currency>\bARS|\bEUR|\bUSD);'
    r'(?P<method>\bEFVO|\bMASTER|\bVISA|\bDEBITO)(?P<paymts>\d{2})?',
    re.I | re.M)

exps = expense.findall(note)

for i in exps:
    if i[7]:
        payments = i[7] if i[7] else False
        if payments:
            for x in range(int(payments)):
                print(x)
