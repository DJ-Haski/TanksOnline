import random
# Генератор рандомных карт--------------------------------------------------------------------
def map():
    f = open('TanksRss/Maps/map2.txt', 'w')
    w = 20 # перепутал w и  h
    h = 36
    i = 0
    j = 0
    counter = 0
    while i < w:
        while j < h:
            if random.randint(1,5) != 5:
                if counter<2 and random.randint(1,100) == 10:
                    print("P", end="")
                    f.write('P')
                    counter=counter+1
                else:
                    print(" ",end="")
                    f.write(' ')
            else:
                print("W",end="")
                f.write('W')
            j=j+1
        i=i+1
        print()
        f.write('\n')
        j=0
    f.close()
map()