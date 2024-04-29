def put_in_array():
    readed = []
    final = []
    with open('queuecopy.txt', 'r') as f:
        data = [line.strip() for line in f]

    with open('queue.txt', 'r') as f:
        data2 = [line.strip() for line in f]

    for line in data:
        print(data2.index(line))
        print(data2[data2.index(line)-1])
        final.append(data2[data2.index(line)-1] + " - " + data2[data2.index(line)])
        data2.remove(data2[data2.index(line)-1])
        data2.remove(data2[data2.index(line)])
    
    print(final)

