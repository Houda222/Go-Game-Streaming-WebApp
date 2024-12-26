import sys
sys.path.append("Post_treatment_Algo/Code")
from corrector_noAI import *
from sgf_to_numpy import *

#failing test because of sgf file not found

liste_tableaux=sgf_to_numpy("partie_vs_organos_8k_.sgf")

"""

Test sur un plateau sans erreurs : OK

"""

liste_coups=correctorNoAI(liste_tableaux)
print(liste_coups)
print("\n\n")

"""

Test en supprimant une frame (erreur liée à un coup rapide) : OK

"""

liste_tableaux=np.delete(liste_tableaux,2,0)
liste_coups=correctorNoAI(liste_tableaux)
print(liste_coups)
print("\n\n")

"""

Test en supprimant deux frames (erreur liée à des coup rapide ou a une ocultation) : 
L'ordre des coups perdu remis au hasard, on a une inversion des premiers coups

"""

liste_tableaux=np.delete(liste_tableaux,2,0)

liste_coups=correctorNoAI(liste_tableaux)
print(liste_coups)
print("\n\n")



"""
Test sur le déplacement d'une pierre (on modifie le premier coup de blanc)
La liste des coups retient la dernière position de la pierre déplacée  : (15,4)
OK
"""

liste_tableaux=sgf_to_numpy("partie_vs_organos_8k_.sgf")

tab=np.copy(liste_tableaux[2])
tab[15,3]=0
tab[15,4]=2

liste_tableaux=np.insert(liste_tableaux,3,tab,0)

print(liste_tableaux[2])
print(liste_tableaux[3])

liste_coups=correctorNoAI(liste_tableaux)
print(liste_coups)
print("\n\n")


"""
Test sur le déplacement d'une pierre (on modifie le premier coup de blanc)
La liste des coups retient la dernière position de la pierre déplacée  : (15,4)
OK
"""

liste_tableaux=sgf_to_numpy("partie_vs_organos_8k_.sgf")

tab=np.copy(liste_tableaux[7])

tab[3,16]=0
tab[3,18]=1

tab[15,3]=0
tab[15,4]=2

tab[15,15]=0
tab[15,16]=1

tab[2,14]=0
tab[1,13]=1

liste_tableaux=np.insert(liste_tableaux,8,tab,0)

print("\n")
print(liste_tableaux[7])
print("\n")
print(liste_tableaux[8])
print("\n")
print(liste_tableaux[9])
print("\n")
print(liste_tableaux[10])



liste_coups=correctorNoAI(liste_tableaux)
print(liste_coups)
print("\n\n")




liste=[(17,4,1),(17,16,2),(4,4,1),(4,16,2)]

sgfres=to-sgf(liste)

fichier=open("sgf_test_fonction_to-sgf.sgf", "w")
fichier.write(sgfres)
fichier.close()

"""

game = sgf.load("sgf_test_fonction_to-sgf.sgf", ignore_illegal_properties=True)
game.play_default_sequence()
print(game.get_board())
game.play_default_sequence()
print(game.get_board())
game.play_default_sequence()
print(game.get_board())
game.play_default_sequence()
print(game.get_board())

"""

result=sgf_to_numpy("partie_vs_organos_8k_.sgf")
#print(result[4])