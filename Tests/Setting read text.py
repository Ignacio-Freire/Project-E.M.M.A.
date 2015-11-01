with open('settings.cfg', 'r') as f:
    log_info = f.readlines()

print(log_info[0].strip())
