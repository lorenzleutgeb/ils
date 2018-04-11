from sys import argv, exit
from pyeda.inter import *

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
      line = raw.strip(';\n').split(' ')

      # Ignoring optimization constraints for now.
      if line[0] == "*" or line[0] == "min:":
        continue

      ops = ["=", "<=", "<", ">=", ">"]

      cofs = [line[2*i] for i in range(len(line)//2 - 1)]
      vars = [line[2*i+1] for i in range(len(line)//2 - 1)]

      try:
        term = int(line[-1])
      except ValueError:
        print("input malformed at line {}: {} is not an integer coefficient.".format(lno, term))
        exit(1)

      op = line[-2]
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

  return(list(reversed(sorted([(y,x) for (x,y) in coeffs.items()]))), c)

# Assume consecutive keys, starting from 1.
def setBDD(poly, c):

  # v = list(range(1,len(poly) + 1))
  v = list(map(bddvar, range(1,len(poly))))
  return recBDD(v, poly, c, 0)


def recBDD(v, poly, c, i):
  if c < 0:
    return True
  elif i == len(poly):
    return False
  else:
    a, b = poly[i]
    # return "ite({},\n{}{},\n{}{})".format(v[b-1], '\t'*i, recBDD(v,poly, c - a, i + 1), '\t'*i, recBDD(v, poly, c, i + 1))
    return ite(v[b], recBDD(v,poly, c - a, i + 1), recBDD(v, poly, c, i + 1))
