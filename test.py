threads = [1, 2, 3, 4, 5, 6, 7, 8]

threads = sorted(threads)
if len(threads) == 0:
    print 1

elif len(threads) == 1:
    if threads[0] - 1 != 0:
        print 1
    else:
        print 2

else:
    numGaps = False
    for i in range(len(threads) - 1):
        print 'number: ' + str(i)
        if threads[i + 1] - threads[i] == 1:
            print 'pass'
            pass
        else:
            numGaps = True
            print threads[i] + 1

    if not numGaps:
        print threads[-1] + 1
