import threading
import copy
from ultralytics import YOLO
from GoGame import *
from GoBoard import *
from GoVisual import *
from flask import Flask, render_template, Response , request
import cv2
import base64



app = Flask(__name__, static_url_path='/static')
app.secret_key = 'your_secret_key'  
camera = cv2.VideoCapture(1,cv2.CAP_DSHOW) 


model = YOLO('model.pt')
game = sente.Game()
go_visual = GoVisual(game)
go_board = GoBoard(model)
game = GoGame(game, go_board, go_visual)

game_plot = np.ones((100, 100, 3), dtype=np.uint8) * 255
usual_message = "camera is well fixed and everything is okay"
message = "Il n'y a pas d'erreur "
disabled_button = 'start-button'
rules_applied ="True"

ProcessFrame = None
Process = True
initialized = False
sgf_text = None


def processing_thread():
    """
        Process the detection algorithm
        
        Update:
            game_plot, sgf_text
        Send error to message if there is one
        """
    
    global ProcessFrame, Process, game_plot, message,initialized,sgf_text

    while Process:
        if not ProcessFrame is None:
            try:
                if not initialized:
                    game_plot = game.initialize_game(ProcessFrame)
                    initialized = True
                    message = usual_message

                else:                    
                    game_plot, sgf_text = game.main_loop(ProcessFrame)
                    message = usual_message

            except Exception as e:
                message = "L'erreur est "+str(e)
                
def generate_plot():
    """
        Generate a plot representing the game
        
        Returns:
            Image
        """
    global game_plot
    
    _, img_encoded = cv2.imencode('.jpg', game.go_visual.current_position())
    img_base64 = base64.b64encode(img_encoded).decode('utf-8')

    return img_base64

@app.route('/')
def index():
    """Route to display HTML page"""
    
    return render_template('index.html', disabled_button=disabled_button, check =rules_applied )


@app.route('/update')
def afficher_message():
    """
        Route to update the image and the message to display 
        
        Returns:
            message
            image
        """
    return {'message': message, 'image' : generate_plot()}

def generate_frames():
    """
        Generate an image from the video stream
        
        Returns:
            Image
        """
    global ProcessFrame
    while True:  
              
        success, frame = camera.read()  # Read the image from the camera
        if not success:
            break
        
        else:
            ProcessFrame = copy.deepcopy(frame)
            _, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                    b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
    
@app.route('/video_feed')
def video_feed():
    """
        Route to send the video stream 
        """
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/', methods=['POST'])
def getval():
    """
        Route to send the video stream 
        """
    global Process, camera,disabled_button
    k = request.form['psw1']
    
    if k == '0':
        camera = cv2.VideoCapture(1,cv2.CAP_DSHOW)
        Process = True
        disabled_button = 'start-button'  # Define the ID of the button to desactivate
    elif k == '1':
        camera.release()
        Process = False
        disabled_button = 'stop-button'   # Define the ID of the button to desactivate
   
        
    return render_template('index.html', disabled_button=disabled_button, check =rules_applied )

@app.route('/game', methods=['POST'])
def getval2():
    """
        Change the current move
        """
    global Process, camera
    i = request.form['psw2']
    if i =='2':
        game.go_visual.initial_position()
    elif i == '3':
        game.go_visual.previous()
    elif i == '4':
        game.go_visual.next()
    elif i == '5':
        game.go_visual.final_position()    
    return render_template('index.html', disabled_button=disabled_button, check =rules_applied )

@app.route('/rules', methods=['POST'])
def handle_rules():
    """
        Check if we want to apply rules, still not implemented
        """
    global rules_applied
    rules_applied = request.form['psw3']
    return render_template('index.html', disabled_button=disabled_button, check =rules_applied )

@app.route('/change_place', methods=['POST'])
def change_place():
    """
        Route to get the piece that we want to change its position
        """
    old_pos = request.form['input1']
    new_pos = request.form['input2']
    print("###################")
    game.correct_stone(old_pos,new_pos)
    return render_template('index.html', disabled_button=disabled_button, check =rules_applied )

@app.route('/get_file_content')
def get_file_content():
    """
        Route which returns the sgf text to be uploaded
        """
    global sgf_text
    return sgf_text

@app.route('/process', methods=['POST'])
def process():
    """
        Route which enables us to save the sgf text
        """
    file = request.files['file']
    file.save('C:/Users/asent/Desktop/projet_16_go/livrables/' + file.filename)
    return "Fichier traité avec succès"

@app.route('/Sommaire')
def sommaire():
    """
        Route to get to the summary page
        """
    camera.release()
    return render_template('Sommaire.html')
@app.route('/index')
def index2():
    """
        Route to get to the index page
        """
    return render_template('index.html', disabled_button=disabled_button, check =rules_applied )

@app.route('/credit')
def credit():
    """
        Route to get to the credit page
        """
    return render_template("credits.html")

@app.route('/Historique')
def historique():
    """
        Route to get to the summary page
        """
    return render_template("Historique.html")

if __name__ == '__main__':
    process_thread = threading.Thread(target=processing_thread, args=())
    process_thread.start()
    app.run(debug=False)