from sente import sgf
import sente
"""
game = sgf.load("Go-Game-Streaming-WebApp/partie_vs_organos _8k_.sgf", ignore_illegal_properties=True)
game.play_default_sequence()
#print(game) # the board is empty but the SGF file is loaded
"""

game = sgf.load("Go-Game-Streaming-WebApp/partie_test2.sgf", ignore_illegal_properties=True)
tab_coups=game.numpy(["black_stones", "white_stones"])
tab_coups_noir=game.numpy(["black_stones"])
tab_coups_blanc=game.numpy(["white_stones"])
#print(tab_coups)
liste= game.get_all_sequences()
print(liste)

"""

Méthode de modification d'un sgf : transformer le sgf en tableau numpy via la librairie sente.
Exemple : 
game = sgf.load("Go-Game-Streaming-WebApp/partie_test2.sgf", ignore_illegal_properties=True)
tab_coups=game.numpy(["black_stones", "white_stones"])
tab_coups_noir=game.numpy(["black_stones"])
tab_coups_blanc=game.numpy(["white_stones"])
#tab_coups_noir est un tableau 19x19 contenant 1 à une position où noir a joué et 0 où il n'a pas joué 
#tab_coups_blanc est un tableau 19x19 contenant 1 à une position où blanc a joué et 0 où il n'a pas joué 
Attention, ça ne coresopnd qu'à une position. Pour avoir toutes les positions de la partie, utiliser par exemple la fonction game.step.up() pour 
revenir la game en arrière.

"""


"""
Erreur type 1 : dernière pierre jouée déplacée:
Conséquence dans le sgf : on va observer un joueur 2 fois de suite 
Correction : Supprimer le premier coup

Problème : La répartition des tâchespose problème. Car si on doit générer un sgf d'abord PUIS corriger les erreurs via un post traitement, 
comment récupérer le sgf ? La problématique est alors comment libérer le mode Partie pour faire en sorte qu'il ne bugue pas.
Peut-être qu'il faut envisager de stocker les informations sous une autre forme que le sgf
EX : liste de tableaux numpy représentant les états du plateau. On peut alors tout stocker correctement.

Erreur type 1 : même façon a peu près pour corriger si on reçoit des tableaux numpy et pas un sgf

Erreur type 2 (si non corrigée via sente) : non supression de l'état où on capture une pierre
RQ : cette erreur ne se pose pas si on stocke sous forme de sgf en ayant utilisé sente 

PROBLEME DU FORMAT :
Avantage format sgf : c'est ce qui va resortir de la librairie sente, et les règles du go seront déjà implémentées, ce qui facilitera grandement
le travail de post-traitement.
Inconvénient : Il faut trouver un moyen de signaler des erreurs à corriger par IA; sinon on a AUCUN moyen de savoir quand l'utiliser. Et comment 
adapter sente pour enregistrer plusieurs coups en même temps en cas de coups rapides/ocultation du goban ? (idée : on choisit au hasard l'ordre
des coups puis on rajoute un message dans le sgf du genre "entre les coups X et Y, le plateau a été modifié, il faut utiliser l'IA pour
reconstituer le bout de partie manquant"  ????)

Avantage format numpy : on peut plus facilement utiliser l'IA si on voit qu'il manque des frames (les coups ont été joués trop rapidement ou 
le plateau a été masqué un temps). Il n'y a pas besoin de signaler qu'il faut l'utiliser en pré-traitement contrairement à l'autre format.
Inconvénient : sente va buguer s'il y a trop de coups illégaux, notamment s'il manque plusieurs coups d'affilée. 

Il faudra trouver un moyen de le faire continuer à enregistrer des frames même s'il manque des coups ou bien ne 
pas l'utiliser... Mais si on choisit d'ignorer la librairie sente et d'enregistrer uniquement ce qu'on voit, 
on va se rajouter BEAUCOUP DE TRAVAIL en post-traitement pour réimplémenter les règles du go, surtout sur la capture 
de pierre qui va nécessiter de modifier/suprimer beaucoup de frames.

Erreur de type 3 : confusion au moment de la capture d'un gros groupe (cas où format=sgf)
NE PEUT SE CORRIGER QU'EN PRÉTRAITEMENT : en effet, la seule manière que je vois pour corriger le problème est d'attendre que l'on
retrouve l'état où les pierres sont capturées avant de rajouter des frames avec de nouveaux coups (sur GoGame.py : on attend que 
detected_state = current_state sur la fonction define_new_move avant de réaliser un play_move OU BIEN PLUTOT on attend que les pierres capturées soient
capturées avant de faire un play_move (cette solution présentant le problème qu'il faut repérer les pierres capturées))


"""

print(help(sente.Game))