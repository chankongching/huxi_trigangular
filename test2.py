with open('result.txt') as f:
    for line in f:
        if not (line.startswith("Filesystem")):
            content = line.split()
            # print(content,end='')
            if not (content[5].startswith('/snap')):
                print("Device name = ", '{0:10}'.format(content[0]),'|', end='')
                print("Usage = ", '{0:10}'.format(content[4]))

f.closed
