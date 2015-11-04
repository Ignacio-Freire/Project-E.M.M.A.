from time import strftime, localtime


def timestamp():
    return '[{}]'.format(strftime("%H:%M:%S", localtime()))

print(timestamp())