from ClasePrueba import pruebaclase
from ClasePrueba import DivError


try:
    asd = pruebaclase.div(5, 0)
    print(asd)
except DivError:
    print('error')

