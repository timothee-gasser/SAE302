n = "tot.txt"
def fich(n):
    fichier = open(n, "r")
    lignes = fichier.readlines()
    for ligne in lignes:
        ligne = ligne.rstrip()
        print(ligne)
    fichier.close()

def fichw(n):
    with open(n, 'r') as f:
        for l in f:
            l = l.rstrip("\n\r")
            print(l)

try:
    fich(n)
    fichw(n)
except FileNotFoundError:
    print("le fichier n'existe pas")

except IOError:
    print("erreur de lecture ou d'écriture")

except FileExistsError:
    print("le fichier existe deja")
except PermissionError:
    print("permision reqise sur le fichier")
