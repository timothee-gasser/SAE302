try:
    n = "toto.txt"
    fichier = open(n, "r")
    lignes = fichier.readlines()
    for ligne in lignes:
        ligne = ligne.rstrip()
        print(ligne)
    fichier.close()

except FileNotFoundError:
    print("le fichier n'existe pas")

except IOError:
    print("erreur de lecture ou d'écriture")

except FileExistsError:
    print("le fichier existe deja")
except PermissionError:
    print("permision reqise sur le fichier")
