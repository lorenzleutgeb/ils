from sys import exit

def parse(f):
  for lno, raw in enumerate(f):
    line = raw.split(' ')

    if line[0] == "*":
      continue

    # Ignoring optimization constraints for now.
    if line[0] == "min:":
      continue

    ops = ["=", "<=", "<", ">=", ">"]

    coeff = [line[2*i] for i in range(len(line)//2 - 1)]
    vars = [line[2*i+1] for i in range(len(line)//2 - 1)]

    op, term = line[:-2], line[:-1]

    if not (op in ops):
      print("input malformed at line {}: incorrect symbol for (in)equality.".format(lno))
      exit(1)
    
    # for (a, x) in zip(coeff,var):
    #  if not ()

    # for (a,b) in zip(coeff,var):
    #   if a in ops:
    #     if a == ">=" or a == "=":
    #       continue
    #     if a == ">":
    #       fst[:-1] = ">="
    #       snd[:-1] -= 1
    #     if a == "<=":
    #       for i in range(len(fst)-1):
    #         fst[i] *= -1
    #     if a == "<":
    #       fst = 


