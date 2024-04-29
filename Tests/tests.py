
def sort_queue():
    block = 1
    aline = -1
    realdata = []
    block = 1
    realdata = []
    # Read the data from the text file into a list
    with open('queue.txt', 'r') as f:
        data = [line.strip() for line in f]
        for line in data:
            aline = aline + 1
            if block == 1:
                block = 0
            elif block == 0:
                print(aline)
                print(line.replace("\n",""))
                realdata.append(int(line.replace("\n","")))
                print(realdata)
                
                block = 1

    realdata.sort(reverse=True)

    # Write the sorted data back to the text file
    with open('queuecopy.txt', 'w') as f:
        for item in realdata:
            f.write(str(item) + '\n')
