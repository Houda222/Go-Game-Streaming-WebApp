import threading
import copy
import traceback
from ultralytics import YOLO
from GoGame import *
from GoBoard import *
from GoVisual import *
from flask import Flask, jsonify, render_template, Response , request
import cv2
import base64
from time import sleep


app = Flask(__name__, static_url_path='/static')



app.secret_key = 'your_secret_key'  # Assurez-vous de définir une clé secrète sécurisée

camera = cv2.VideoCapture(1,cv2.CAP_DSHOW)  # Le numéro 0 indique la caméra par défaut, mais vous pouvez spécifier le numéro de port approprié.

# game_plot = np.ones((600, 600, 3), dtype=np.uint8) * 255
message = "Il n'y a pas d'erreur "
message_affiche = message


model = YOLO('model.pt')
game = sente.Game()
go_visual = GoVisual(game)
go_board = GoBoard(model)
game = GoGame(game, go_board, go_visual)

blank_image = np.ones((300, 300, 3), dtype=np.uint8) * 255
game_plot = blank_image
ProcessFrame = None
Process = True
affichage = "dernier"
game_plot_modified = False

def processing_thread():
    
    global ProcessFrame, Process, game_plot, message,game_plot_modified
    initialized = False

    while Process:
        if not ProcessFrame is None:
            try:
                if not initialized:
                    game_plot = game.initialize_game(ProcessFrame)
                    initialized = True
                else:
                    # game_plot, sgf_text = game.main_loop(ProcessFrame)
                    if not game_plot_modified:
                        game_plot = game.main_loop(ProcessFrame) #je n'oublie pas le txt

                    
                ############ WA SMA3NI MZZZZN DB.  game_plot HYA LA VARIABLE LLI FIHA L'IMAGE DESSINé
                ############ B LE CODE DYAL HOUDA;
                ############ O sgf_filename HOWA LE NOM DYAL LE FICHER SGF LLI T ENREGISTRA 
                ############ QUI CORRESPOND A game_plot
                    # game_plot = game.main_loop(ProcessFrame).final_position #je n'oublie pas le txt
                    
                    else :
                        if affichage== "dernier":
                            game_plot = game.go_visual.final_position()
                            game_plot_modified = False
                        elif affichage == "precedent":
                            game_plot = game.go_visual.previous()
                            game_plot_modified = True

                            
                    # elif affichage == "suivant":
                    #     game_plot = game_plot.next()
                    # elif affichage == "premier":
                    #     game_plot = game_plot.initial_position()
                # game_plot, sgf_filename = show_board(model, ProcessFrame)
                # cv2.imshow("master", game_plot)
                # cv2.imshow("annotated", game.board_detect.annotated_frame)
                # cv2.imshow("transformed", game.board_detect.transformed_image)
                
                
            except Exception as e:
                message = "L'erreur est "+str(e)
                
                
            


# Route pour afficher la page HTML
@app.route('/')
def index():
    global message

    return render_template('index.html',disabled_button = 'start-button')

# @app.route('/msg')
# def afficher_message():
#     global message
    
#     return render_template('index.html', message=message)

def generate_plot():
    # width, height = 640, 480

    # # Création d'une image noire
    # game_plot = np.zeros((height, width, 3), dtype=np.uint8)

    # # Taille des carrés du damier
    # square_size = 50

    # # Dessiner le damier en couleur
    # for i in range(0, width, square_size * 2):
    #     for j in range(0, height, square_size * 2):
    #         game_plot[j:j+square_size, i:i+square_size] = [0, 255, 0]  # Vert
    #         game_plot[j+square_size:j+2*square_size, i+square_size:i+2*square_size] = [0, 255, 0]  # Vert
    _, img_encoded = cv2.imencode('.jpg', game_plot)
    img_base64 = base64.b64encode(img_encoded).decode('utf-8')
    return img_base64

@app.route('/update')
def afficher_message():
    return {'message': message, 'image' : generate_plot()}


# # Route pour obtenir le message en JSON
# @app.route('/get_message')
# def get_message():
#     global message
#     return jsonify({'message': message})

def generate_frames():
    global ProcessFrame
    while True:        
        success, frame = camera.read()  # Lire une image depuis la caméra
        if not success:
            break
        else:
            ProcessFrame = copy.deepcopy(frame)

            _, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                    b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
            # sleep(0)
    
@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')



# @app.route('/get_plot')
# def get_plot():
#     return generate_plot()

@app.route('/', methods=['POST'])
def getval():
    global Process, camera, affichage
    # k = request.form['psw1']
    
    # if k == '0':
    #     camera = cv2.VideoCapture(1,cv2.CAP_DSHOW)
    #     Process = True
    #     disabled_button = 'start-button'  # Définir l'ID du bouton à désactiver
    # elif k == '1':
    #     camera.release()
    #     Process = False
    #     disabled_button = 'stop-button'  # Définir l'ID du bouton à désactiver
    # else:
    #     disabled_button = None
    disabled_button = None
    i = request.form['psw2']
    if i =='2':
        affichage = "premier"
    elif i == '3':
        affichage = "precedent"
    elif i == '4':
        affichage = "suivant"
    elif i == '5':
        affichage = "dernier"
            
        
    return render_template('index.html', disabled_button=disabled_button)



@app.route('/sommaire')
def sommaire():
    camera.release()
    return render_template('Sommaire.html')
@app.route('/index')
def index2():
    return render_template('index.html')

@app.route('/credit')
def credit():
    return render_template("credits.html")

@app.route('/historique')
def historique():
    return render_template("Historique.html")



if __name__ == '__main__':
    
    process_thread = threading.Thread(target=processing_thread, args=())
    process_thread.start()
    app.run(debug=False)

# cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)

# while cap.isOpened():
#     ret, frame = cap.read()
#     if not ret:
#         break
    
#     ########################## frame HYA LA VARIABLE LLI FIHA CHAQUE IMAGE DYAL STREAM
#     ########################## YA3NI LE FLUX DE VIDEO QUI DOIT ETRE STREAMé
#     ProcessFrame = copy.deepcopy(frame)
    
#     cv2.imshow('Video Stream', frame)
    
#     key_pressed = cv2.waitKey(1) & 0xFF
    
#     # if key_pressed == ord('p'):
#     #     print("button pressed")
    
#     if key_pressed == ord('q'):
#         Process = False
#         break 

# cap.release()
# cv2.destroyAllWindows()