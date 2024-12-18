import sente
from sente import sgf
import numpy as np
from sgf_to_numpy import *
import itertools

"""
On a une liste de tableaux numpy représentant les états de la partie. L'idée de base est de retrouver les cops en regaradnt les différneces
entre deux états consécutifs.

On suppose que c'est à blanc de jouer.

Cas N° 1.1 (principal) : 
pierres_noires_ajoutées : 0 
pierres_noires_retirées : 0
pierres_blanches_ajoutées : +1
pierres_blanches_retirées : 0

Correction : Entre 2 états, on ajoute une pierre de la bonne couleur. Dans ce cas, on ajoute le coup à la liste de coups.

Cas N° 1.2 : 2 coups rapides 
pierres_noires_ajoutées : +1 
pierres_noires_retirées : 0
pierres_blanches_ajoutées : +1
pierres_blanches_retirées : 0

Correction : On interprète ça comme un coup joué rapidement. On ajoute les 2 coups dans la liste des coups.


Cas N° 1.3 : + de 2 coups rapides 
pierres_noires_ajoutées : +(x-1) 
pierres_noires_retirées : 0
pierres_blanches_ajoutées : +x, x>1
pierres_blanches_retirées : 0

Correction : On interprète ça comme plusieurs coup joués rapidement ou bien une ocultation du plateau. 
On utilise l'IA pour reconstituer si on peut, sinon on ajoute les coups au hasard et on SIGNALE.


Cas N° 2.1 : joueur qui joue plusieurs coup de suite
pierres_noires_ajoutées : 0 
pierres_noires_retirées : 0
pierres_blanches_ajoutées : y, y>1 
pierres_blanches_retirées : 0

Correction : On ne peut l'interpréter que comme une violation des règles : Blanc a joué plusieurs fois de suite
BLOCAGE!!!!!! -> Attendre de revenir dans un des autres cas pour agir (regarder les frames suivantes)

Cas N° 2.2 : joueur qui joue plusieurs coup de suite
pierres_noires_ajoutées : +x 
pierres_noires_retirées : 0
pierres_blanches_ajoutées : 0 
pierres_blanches_retirées : 0

Correction : On ne peut l'interpréter que comme une violation des règles : Noir a joué plusieurs fois de suite
BLOCAGE!!!!!! -> Attendre de revenir dans un des autres cas pour agir (regarder les frames suivantes)

Cas N° 3 : déplacement de pierres
pierres_noires_ajoutées : +x
pierres_noires_retirées : -x
pierres_blanches_ajoutées : +y 
pierres_blanches_retirées : -y

Correction : On interprète cette variation comme le fait que des pierres noires ou blanches ont été déplacées.
Cas x=1 : on modifie le coup dans la liste des coups
Cas x>1 : IA ou bien pas de modification ou bien modifications au hasard de la liste des coups. À signaler !!! 
Idem pour y.


Cas N° 4.1 : capture de pierres
pierres_noires_ajoutées : 0 
pierres_noires_retirées : -x
pierres_blanches_ajoutées : 0 
pierres_blanches_retirées : -y

Correction : On interprète cette variation comme la capture d'un groupe de pierres noires/ de pierres blanches. Pas de modification de la liste
des coups.

Cas N° 4.2 : capture de pierres et 1 coup rapide
pierres_noires_ajoutées : 0 
pierres_noires_retirées : 0
pierres_blanches_ajoutées : +1 
pierres_blanches_retirées : -y

Correction : On interprète cette variation comme la capture d'un groupe de pierres blanches avec un coup rapide. On ajoute le coup à la liste des 
coups.

Cas N° 4.3 : capture de pierres et 2 coups rapides
pierres_noires_ajoutées : +1 
pierres_noires_retirées : -x
pierres_blanches_ajoutées : +1 
pierres_blanches_retirées : -y

Correction : On interprète cette variation comme la capture d'un groupe de pierres blanches avec 2 coups rapide. On ajoute les 2 coups à la liste des 
coups.

Cas N° 4.4 : capture de pierres et + de 2 coups rapides
pierres_noires_ajoutées : + (z-1) 
pierres_noires_retirées : -x
pierres_blanches_ajoutées : + z , z>1
pierres_blanches_retirées : -y

Correction : On interprète ça comme plusieurs coup joués rapidement ou bien une ocultation du plateau. 
On utilise l'IA pour reconstituer is on peut, sinon on ajoute les coups au hasard et on SIGNALE.

"""

def differences(tab1,tab2):
    """
        Reourne les listes des pierres ajoutées et retirées entre 2 états du plateau
    """
    pierres_noires_ajoutées=[]
    pierres_noires_retirées=[]
    pierres_blanches_ajoutées=[]
    pierres_blanches_retirées=[]
    nb_ajouts=0
    for ligne in range(19):
        for col in range(19):
            if tab2[ligne,col]==1 and tab1[ligne,col] ==0:
                pierres_noires_ajoutées.append((ligne,col,1))
                nb_ajouts+=1
            
            if tab2[ligne,col]==0 and tab1[ligne,col] ==1:
                pierres_noires_retirées.append((ligne,col,1))
            
            if tab2[ligne,col]==2 and tab1[ligne,col] ==0:
                pierres_blanches_ajoutées.append((ligne,col,2))
                nb_ajouts+=1
            
            if tab2[ligne,col]==0 and tab1[ligne,col] ==2:
                pierres_blanches_retirées.append((ligne,col,2))
           
            if tab2[ligne,col]==2 and tab1[ligne,col] ==1:
                pierres_noires_retirées.append((ligne,col,1))
                pierres_blanches_ajoutées.append((ligne,col,2))
                nb_ajouts+=1
            
            if tab2[ligne,col]==1 and tab1[ligne,col] ==2:
                pierres_blanches_retirées.append((ligne,col,2))
                pierres_noires_ajoutées.append((ligne,col,1))
                nb_ajouts+=1
    return {1 : {"ajout" : pierres_noires_ajoutées, "retire" : pierres_noires_retirées}, 
            2 : {"ajout" :pierres_blanches_ajoutées, "retire" : pierres_blanches_retirées}}, nb_ajouts



def get_last_index(L,e):
    index=-1
    for i in range (len(L)):
        if L[i]==e:
            index=i
    return index


def distance(liste_ajouts, liste_retraits):
    return sum(abs(liste_ajouts[i][0]-liste_retraits[i][0])+abs(liste_ajouts[i][1]-liste_retraits[i][1]) for i in range(len(liste_ajouts)))

def opt_permutation(liste_ajouts,liste_retraits):
    d_opt=np.inf
    liste_ajouts_permut_opt=liste_ajouts
    for liste_ajouts_permut in list(itertools.permutations(liste_ajouts)):
       if distance(liste_ajouts_permut,liste_retraits)<d_opt:
           liste_ajouts_permut_opt=liste_ajouts_permut
           d_opt=distance(liste_ajouts_permut,liste_retraits)
    return liste_ajouts_permut_opt
    

"""
def voisinage(x_ajout,y_ajout,liste_pierres_retirees):
    x_opt=liste_pierres_retirees[0]
    y_opt=liste_pierres_retirees[0]
    e=np.inf
    for (x,y) in liste_pierres_retirees:
        if abs(x-x_ajout)+abs(y-y_ajout)<e:
            e=abs(x-x_ajout)+abs(y-y_ajout)
            x_opt=x
            y_opt=y
    return (x,y)
"""


def correctorNoAI(liste_tableaux):
    liste_coups=[]
    #liste[i] contient la position du coup i sous la forme d'un tuple (ligne_coup,colonne_coup,n°pierre) ou n°pierre=1 si c'est noir qui joue et 2
    # si c'est blanc qui joue
    Nb_frames = len(liste_tableaux)

    turn=1 #contient 1 si c'est à noir de jouer, 2 si c'est à blanc de jouer
    notturn=2
    for index in range(1,Nb_frames):
        D,nb_ajouts=differences(liste_tableaux[index-1],liste_tableaux[index])
        #pierres_noires_ajoutées=D[1]["ajout"]
        #pierres_noires_retirées=D[1]["retire"]
        #pierres_blanches_ajoutées=D[2]["ajout"]
        #pierres_blanches_retirées=D[2]["retire"]
        
        
        if nb_ajouts!=0: # s'il il y a des pierres ajoutées, on les cherche pour les mettre dans la liste des coups
            
            # On vérifie que le nombre de pierres ajoutées est cohérent du point de vue du fait que les joueurs jouent à tour de rôle 
            # CAS N°1
            if len(D[turn]["ajout"])-len(D[notturn]["ajout"])==1: 
                liste_coups.append(D[turn]["ajout"][0])
                for k in range(len(D[notturn]["ajout"])):
                    liste_coups.append(D[notturn]["ajout"][k])
                    liste_coups.append(D[turn]["ajout"][k+1])
                temp=turn # On change le tour du joueur pour la prochaine iteration
                turn=notturn
                notturn=temp
            if len(D[turn]["ajout"])-len(D[notturn]["ajout"])==0 and len(D[turn]["ajout"])>=1: 
                print(index)
                for k in range(len(D[notturn]["ajout"])):
                    liste_coups.append(D[turn]["ajout"][k])
                    liste_coups.append(D[notturn]["ajout"][k])
     
            else:
                #On traite le cas où une seule pierre a été déplacée en modifiant la liste des coups
                # CAS N°3

                """
                if len(D[turn]["ajout"])==len(D[turn]["retire"]) and len(D[turn]["ajout"])==1:
                    (x,y,c)=D[turn]["retire"][0]
                    index=get_last_index(liste_coups,(x,y,c))
                    if index!=-1:
                        liste_coups[index]=D[turn]["ajout"][0]
                
                if len(D[notturn]["ajout"])==len(D[notturn]["retire"]) and len(D[notturn]["ajout"])==1:
                    (x,y,c)=D[notturn]["retire"][0]
                    index=get_last_index(liste_coups,(x,y,c))
                    if index!=-1:
                        liste_coups[index]=D[notturn]["ajout"][0]
                """
                #Cas du déplacement de plusieurs pierres
                if len(D[turn]["ajout"])==len(D[turn]["retire"]):
                    liste_retraits=D[turn]["retire"]
                    liste_ajouts=D[turn]["ajout"]

                    liste_ajout_opt_permut=opt_permutation(liste_ajouts,liste_retraits) #Identification du déplacement de pierres le plus probable

                    for i in range(len(liste_ajout_opt_permut)):
                        (x,y,c)=liste_retraits[i]
                        index=get_last_index(liste_coups,(x,y,c))
                        if index!=-1:
                            liste_coups[index]=liste_ajout_opt_permut[i]

                if len(D[notturn]["ajout"])==len(D[notturn]["retire"]):
                    liste_retraits=D[notturn]["retire"]
                    liste_ajouts=D[notturn]["ajout"]
                    print("LISTES :  ",liste_retraits,liste_ajouts)
                    liste_ajout_opt_permut=opt_permutation(liste_ajouts,liste_retraits) #Identification du déplacement de pierres le plus probable

                    for i in range(len(liste_ajout_opt_permut)):
                        (x,y,c)=liste_retraits[i]
                        index=get_last_index(liste_coups,(x,y,c))
                        if index!=-1:
                            liste_coups[index]=liste_ajout_opt_permut[i]
                
            
          
    return liste_coups

    



                

   

            
            

            

















