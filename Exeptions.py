def divEntier(x: int, y: int) -> int:
    if y==0:
        raise RecursionError
    if x<0:
        raise RecursionError
    if y<0:
        raise RecursionError
    if x < y:
        return 0
    else:
        x = x - y
        return divEntier(x, y) + 1


if __name__ == '__main__':
    try:
        a = float(input("x: "))
        b = float(input("y: "))
        print(divEntier(a, b))
    except ValueError:
        print("met une bonne valeur, genre un chifre")
    except RecursionError:
        print("met une bonne valeur, genre un truc autre que 0 et positife")
