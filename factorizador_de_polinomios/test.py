from sympy import Rational, sqrt, root, I, pi, acos, cos, trigsimp, simplify, powsimp, expand


rta = root(-5 + 2 * sqrt(13), 3) + root(-5 - 2 * sqrt(13), 3) + 1

rta = simplify(powsimp(trigsimp(expand(rta))))

print(rta)