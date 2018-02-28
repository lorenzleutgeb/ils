def text-2-dimacs(A):
    for i in range(1,9):
        s = ""
        for j in range(1,9):
            for k in range(1,9):
                s += "{}{}{} ".format(i*100, j*10, k)
            s += "0"
            print(s)

    for i in range(1,9):
        for j in range(1,9):
            for k in range(1,9):
                for l in range(k+1,9):
                    print("-{}{}{} -{}{}{} 0".format(i*100,j*10,k,i*100,j*10,l))

    for i in range(1,9):
        for j in range(1,9):
            for k in range(j+1,9):
                for d in range(1,9):
                    print("-{}{}{} -{}{}{} 0".format(i*100,j*10,d,i*100,k*10,d))

    for i in range(1,9):
        for k in range(i+1,9):
            for j in range(1,9):
                for d in range(1,9):
                    print("-{}{}{} -{}{}{} 0".format(i*100,j*10,d,k*100,j*10,d))

    for d in range(1,9):
        for i in range(1,9):
            for j in range(i+1,9):
                for ro in range(3):
                    for co in range(3):
                        print("-{}{}{} -{}{}{}".format((3*ro + i)/ 3,(3*co + i)%3,d,(3*ro + j)/3,(3*co + j)%3,d))

    for i in range(len(A)):
        for j in range(len(A[i])):
            if A[i][j] != 0:
                print("{}{}{} 0".format((i+1)*100, (j+1)*10, A[i][j]))

