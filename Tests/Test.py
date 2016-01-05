runs = 700
totTime = 3000

print('{} runs so far. That\'s {} days, {} hours or {} minutes. Real process time {}s'
                               .format(runs, int((((runs*2)/60) + totTime/3600)/24), int(((runs*2)/60) + totTime/3600),
                                       int(runs*2 + totTime/60), int(totTime)))