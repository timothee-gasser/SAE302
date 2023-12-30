import math

def ln(x):
    try:
        resultat = math.log(x)
        return resultat
    except ValueError:
        if x <= 0:
            print("Entré une valeur positive et diférante de 0.")
    except TypeError:
        if isinstance(x, str):
            print("Entré un nombre et non des lettre.")



def main():
    x = float(input("Entrez une valeur pour calculer ln(x) : "))
    res_ln = ln(x)
    print(f"Ln({x}) = {res_ln}")

if __name__ == "__main__":
    main()
