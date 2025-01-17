from sympy import Rational, sqrt, root, I, pi, acos, cos, trigsimp, simplify

def metodo_ferrari(coeficientes:list):
    print("metodo ferrari")

def metodo_cardano(coeficientes:list):
    res = []
    a = Rational(coeficientes[0])
    b = Rational(coeficientes[1])
    c = Rational(coeficientes[2])
    d = Rational(coeficientes[3])

    p = simplify((3*a*c - b**2)/(3*a**2))
    q = simplify((2*b**3 - 9*a*b*c + 27*d*a**2)/(27*a**3))

    discriminante = simplify(q**2 + (4*p**3)/27)

    if discriminante > 0:
        print("disc pos")
        # una solución real y dos complejas
        u = simplify(root((-q+sqrt(discriminante))/2, 3))
        v = simplify(root((-q-sqrt(discriminante))/2, 3))

        w   = simplify(-Rational(1,2) + (sqrt(3)/ 2)*I)
        w_2 = simplify(-Rational(1,2) - (sqrt(3)/ 2)*I)

        res.append(simplify(u + v     - b/(3*a)))
        res.append(simplify(w*u+w_2*v - b/(3*a)))
        res.append(simplify(w_2*u+w*v - b/(3*a)))

    elif discriminante == 0:
        print("disc nulo")
        res.append(trigsimp( 2 * root(-q/2, 3) - b/(3*a)))
        res.append(trigsimp(   - root(-q/2, 3) - b/(3*a)))
        res.append(trigsimp(   - root(-q/2, 3) - b/(3*a)))
    
    else:
        print("disc neg")
        # tres sol reales
        tita = acos(Rational(3*q,2*p)*sqrt(-3/ p))
        res.append(trigsimp( 2 *sqrt(-p/3)*cos(tita/3)         - b/(3*a)))
        res.append(trigsimp( 2 *sqrt(-p/3)*cos((tita+2*pi)/3)  - b/(3*a)))
        res.append(trigsimp( 2 *sqrt(-p/3)*cos((tita+4*pi)/3)  - b/(3*a)))

    return res

def metodo_resolvente(coeficientes:list):
    res = []
    a = Rational(coeficientes[0])
    b = Rational(coeficientes[1])
    c = Rational(coeficientes[2])

    res.append( (-b + sqrt(b**2 - 4*a*c) )/2*a )
    res.append( (-b - sqrt(b**2 - 4*a*c) )/2*a )
    return res


coeficientes = input("ingrese los coeficientes del polinomio: ").split()
coeficientes = [int(a) for a in coeficientes]



if len(coeficientes) == 5:
    res = metodo_ferrari(coeficientes)
elif len(coeficientes) == 4:
    res = metodo_cardano(coeficientes)
elif len(coeficientes) == 3:
    res = metodo_resolvente(coeficientes)

for i, raiz in enumerate(res):
    print(f"{i+1}: ", raiz)