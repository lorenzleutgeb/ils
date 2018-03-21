def encode(gt,fix,n):
    futo = exprvars('x', (1,n), (1,n), (1,n))
    # Each cell on the board contains a unique value.
    vals = And(*[
             And(*[
                 OneHot(*[futo[row,col,val]
                     for val in range(1,n)])
                 for col in range(1,n)])
             for row in range(1,n)])
    # For each row, all cells have distinct values.
    rows = And(*[
             And(*[
                 OneHot(*[futo[row,col,val]
                     for col in range(1,n)])
                 for val in range(1,n)])
             for row in range(1,n)])
    # For each column, all cells have distinct values.
    cols = And(*[
             And(*[
                 OneHot(*[futo[row,col,val]
                     for row in range(1,n)])
                 for val in range(1,n)])
             for col in range(1,n)])
    ineqs = And(*[
              Or(*[
                Or(*[
                    And(futo[r1,c1,i],futo[r2,c2,j])
                    for i in range(j+1,n)])
                for j in range(1,n)])
              for ((r1,c1),(r2,c2)) in gt])
    fixes = And(*[futo(row,col,val) for (row,col,val) in fix])

    sol = And(vals,rows,cols,ineqs,fixes)

    return sol

def solve(grid):
    return grid.satisfy_one()

                       

