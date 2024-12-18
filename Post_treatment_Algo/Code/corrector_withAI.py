#import sgf
import numpy as np
from sgf_to_numpy import *
import itertools
import sys
sys.path.append("Post_treatment_AI/Code")
from Fill_gaps_model import *

sys.path.append('Post_treatment_Algo/Code')
from corrector_noAI import differences
from corrector_noAI import get_last_index


def correctorAI(liste_tableaux):
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
            if len(D[turn]["ajout"])==1 and len(D[notturn]["ajout"])==0: 
                liste_coups.append(D[turn]["ajout"][0])
                print("player ", turn, " played at ", D[turn]["ajout"][0])
                temp=turn # On change le tour du joueur pour la prochaine iteration
                turn=notturn
                notturn=temp
            elif (len(D[turn]["ajout"])==0 and len(D[notturn]["ajout"])==0): 
                continue
            else:
                b,w = get_possible_moves(liste_tableaux[index],liste_tableaux[index-1])
                liste_tableaux=fill_gaps(model,liste_tableaux,index-1,index,b, w).copy()
                index-=1
          
    return liste_coups

    



                

   

            
            

            

















