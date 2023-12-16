import threading
import copy
from ultralytics import YOLO
from GoGame import *
from GoBoard import *
from GoVisual import *
from flask import Flask, render_template, Response , request
import cv2
import base64

cam_index = 0

app = Flask(__name__, static_url_path='/static')
app.secret_key = 'your_secret_key'  
camera = cv2.VideoCapture(cam_index,cv2.CAP_DSHOW) 


model = YOLO('model.pt')

usual_message = "La caméra est bien fixée et tout est Ok"
message = "Rien n'a encore été lancé "
disabled_button = 'start-button'
# rules_applied ="True"

ProcessFrame = None
Process = True
initialized = False
sgf_text = None
game= None
new_game = True
process_thread = None
camera_running = False


def New_game():
    
    global game,new_game, initialized
    game = sente.Game()
    go_visual = GoVisual(game)
    go_board = GoBoard(model)
    game = GoGame(game, go_board, go_visual, False)
    game_plot = np.ones((100, 100, 3), dtype=np.uint8) * 255
    new_game = True
    initialized = False
    process = True

def processing_thread():
    """
        Process the detection algorithm
        
        Update:
            game_plot, sgf_text
        Send error to message if there is one
        """
    
    global ProcessFrame, Process, game_plot, message,initialized,sgf_text,new_game
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
                message = "Erreur : "+str(e)
                
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

# def end_camera():
#     global process_thread, camera_running, disabled_button
#     if camera_running:
#         process_thread.join()  # Wait for the thread to finish before stopping
#         camera_running = False
#         disabled_button = 'stop-button'   # Define the ID of the button to desactivate

# def open_camera():
#     """Open the camera"""
#     global camera, process_thread, disabled_button, camera_running
#     if not camera_running:
#         camera = cv2.VideoCapture(cam_index, cv2.CAP_DSHOW)
#         process_thread = threading.Thread(target=processing_thread, args=(camera,))
#         process_thread.start()
#         camera_running = True
#         disabled_button = 'start-button'  # Define the ID of the button to desactivate

@app.route('/')
def index():
    """Route to display HTML page"""
    
    return render_template('home.html', disabled_button=disabled_button)



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
    global ProcessFrame,camera
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

def end_camera():
    """stop the camera """
    global camera, Process,disabled_button
    camera.release()
    Process = False
    disabled_button = 'stop-button'   # Define the ID of the button to desactivate

def open_camera():
    """open the camera """
    global camera, Process,disabled_button
    camera = cv2.VideoCapture(1,cv2.CAP_DSHOW)
    Process = True
    disabled_button = 'start-button'  # Define the ID of the button to desactivate

@app.route('/cam', methods=['POST'])
def getval():
    """
        Route to send the video stream 
        """
    k = request.form['psw1']
    if k == '0':
        open_camera()
    elif k == '1':
        end_camera()
        
    return render_template('partie.html', disabled_button=disabled_button)

@app.route('/t', methods=['POST'])
def getvaltransparent():
    """
        Route to send the video stream 
        """
    k = request.form['psw1']
    if k == '0':
        open_camera()
    elif k == '1':
        end_camera()
        
    return render_template('transparent.html', disabled_button=disabled_button)

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
    return render_template('partie.html', disabled_button=disabled_button)

@app.route('/rules', methods=['POST'])
def handle_rules():
    """
        Check if we want to apply rules, still not implemented
        """
    global rules_applied
    
    rules_applied = request.form['psw3']
    if rules_applied == "True":
        game.set_transparent_mode(False)
        rules_applied = "False"
    else : 
        game.set_transparent_mode(True)
        print("########pas de regles")
        rules_applied = "True"
    return render_template('partie.html', disabled_button=disabled_button)

@app.route('/change_place', methods=['POST'])
def change_place():
    """
        Route to get the piece that we want to change its position
        """
    old_pos = request.form['input1']
    new_pos = request.form['input2']
    try:
        game.correct_stone(old_pos,new_pos)
    except Exception as e:
        message = "L'erreur est "+str(e)
    return render_template('partie.html', disabled_button=disabled_button)

@app.route('/save_sgf')
def get_file_content():
    """
        Route which returns the sgf text to be uploaded
        """
    global sgf_text
    return sgf_text

@app.route('/upload', methods=['POST'])
def process():
    """
        Route which enables us to save the sgf text
        """
    global Process
    file = request.files['file']
    file_path = file.filename
    Process = False
    try:
        game.go_visual.load_game_from_sgf(file_path)
        message = "Le fichier a été correctement chargé"
    except Exception as e:
        message = "L'erreur est "+str(e)
    

    return render_template('sgf.html', disabled_button=disabled_button)

@app.route('/Home')
def home():
    """
        Route to get to the home page
        """    
    open_camera()
    return render_template('Home.html', disabled_button=disabled_button)

@app.route('/credit')
def credit():
    """
        Route to get to the credit page
        """
    return render_template("credits.html")

@app.route('/start', methods=['POST'])
def start():
    """
        Route to start a new game
        """
    New_game()
    return render_template('partie.html', disabled_button=disabled_button)

@app.route('/undo', methods=['POST'])
def undo():
    """
    undo last played move
        """
    game.delete_last_move()
    return render_template("partie.html")
    
@app.route('/historique')
def historique():
    """
        Route to get to the summary page
        """
    return render_template("Historique.html")


@app.route('/partie')
def partie():
    """
        Route to get to the streaming page in game mode
        """
    return render_template("partie.html")

@app.route('/transparent')
def transparent():
    """
        Route to get to the streaming page in transparent mode
        """
    game.set_transparent_mode(True)
    return render_template("transparent.html")

@app.route('/sgf')
def sgf():
    """
        Route to get to the streaming page in transparent mode
        """
    return render_template("sgf.html")

@app.route('/transparent')
def appl_transparent_mode():
    """
        activate tranparent mode in the transparent mode page
        """
    game.set_transparent_mode(True)

    return render_template("transparent.html")

if __name__ == '__main__':
    New_game()
    process_thread = threading.Thread(target=processing_thread, args=())
    process_thread.start()
    app.run(debug=False)