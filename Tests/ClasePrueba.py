class pruebaclase:

    @staticmethod
    def div(a, b):

        try:
            res = a//b
        except:
            raise DivError
        return res


class DivError(Exception):
    pass