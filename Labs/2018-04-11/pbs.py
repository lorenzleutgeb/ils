from sys import argv, exit

def sgn_change(lst):
  return list(map(lambda x: -x, lst))

def get_varkey(lno, var):
  if (var[0] == "x"):
    try:
      key = int(var[1:])
    except ValueError:
      print("input malformed at line {}: {} is not a correct variable.".format(lno,var))
      exit(1)
    return key
  else:
    print("input malformed at line {}: {} is not a correct variable.".format(lno,var))
    exit(1)

def parse(filename):
  """
  :returns: (dict, c) representing sum(l) >= c.
  """
  c = 0
  coeffs = {}

  with open(filename, 'r') as f:
    for lno, raw in enumerate(f):
      line = raw.strip('\n').strip(';').split(' ')

      if line[0] == "*":
        continue

      # Ignoring optimization constraints for now.
      if line[0] == "min:":
        continue

      ops = ["=", "<=", "<", ">=", ">"]

      cofs = [line[2*i] for i in range(len(line)//2 - 1)]
      vars = [line[2*i+1] for i in range(len(line)//2 - 1)]

      term, op = line[-1], line[-2]

      try:
        term = int(term)
      except ValueError:
        print("input malformed at line {}: {} is not an integer coefficient.".format(lno, term))
        exit(1)

      if not (op in ops):
        print("input malformed at line {}: incorrect symbol for (in)equality.".format(lno))
        exit(1)

      if (op == ">"):
        term += 1
      elif op == "<=":
        cofs = sgn_change(cofs)
      elif op == "<":
        cofs = sgn_change(cofs)
        term -= 1

      for (a, x) in zip(cofs,vars):
        try:
          t = int(a)
        except ValueError:
          print("input malformed at line {}: {} is not an integer coefficient.".format(lno, a))
          exit(1)

        key = get_varkey(lno, x[(1 if x[0] == "~" else 0):])
        coeffs.update([(key, coeffs.get(key,0) + (-t if x[0] == "~" else t))])

        term = term - (t if x[0] == "~" else 0)
      
      c += term

  return(coeffs, c)


