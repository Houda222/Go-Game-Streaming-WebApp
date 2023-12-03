import threading
import copy
import traceback
from ultralytics import YOLO
import cv2
from GoGame import *
from GoBoard import *
from GoVisual import *


def processing_thread():
    global ProcessFrame, Process
    
    initialized = False
    while Process:
        if not ProcessFrame is None:
            pass
            try:
                if not initialized:
                    game_plot, sgf_text = game.initialize_game(ProcessFrame)
                    initialized = True
                else:
                    
                ############ WA SMA3NI MZZZZN DB.  game_plot HYA LA VARIABLE LLI FIHA L'IMAGE DESSINé
                ############ B LE CODE DYAL HOUDA;
                ############ O sgf_filename HOWA LE NOM DYAL LE FICHER SGF LLI T ENREGISTRA 
                ############ QUI CORRESPOND A game_plot
                    game_plot, sgf_text = game.main_loop(ProcessFrame)
                # game_plot, sgf_filename = show_board(model, ProcessFrame)
                cv2.imshow("master", game_plot)
                # cv2.imshow("annotated", game.annotated_frame)
                # cv2.imshow("transformed", game.board_detect.transformed_image)
                
            # except OverflowError as e:
            #     print(f"Overflow Error: {e}")
                
            except Exception as e:
                # print('empty frame', type(e), e.args, e)
                traceback.print_exc()
                # exception_info = {
                #     'exception_type': type(e).__name__,
                #     'exception_message': str(e),
                #     'traceback': traceback.format_exc()
                # }

                # # Save the frame along with the exception information
                # cv2.imwrite('error_logs/error_frame.jpg', ProcessFrame)
                # cv2.imwrite('error_logs/error_annotated_frame.jpg', game.annotated_frame)
                
                
                # # Optionally, you can save the exception information to a file or log it
                # with open('error_logs/error_log.txt', 'w') as log_file:
                #     log_file.write(str(exception_info))
                # cv2.imwrite(f"{e}.jpg", ProcessFrame)
        

        key_pressed = cv2.waitKey(1) & 0xFF
        
        if key_pressed == ord('p'):
            print("button pressed")

        if key_pressed == ord('q'):
            Process = False
            break  # Break the loop if 'q' is pressed


model = YOLO('model.pt')
game = sente.Game()
go_visual = GoVisual(game)
go_board = GoBoard(model)
game = GoGame(game, go_board, go_visual)

ProcessFrame = None
Process = True

process_thread = threading.Thread(target=processing_thread, args=())
process_thread.start()

cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break
    
    ########################## frame HYA LA VARIABLE LLI FIHA CHAQUE IMAGE DYAL STREAM
    ########################## YA3NI LE FLUX DE VIDEO QUI DOIT ETRE STREAMé
    ProcessFrame = copy.deepcopy(frame)
    
    cv2.imshow('Video Stream', frame)
    
    key_pressed = cv2.waitKey(1) & 0xFF
    
    # if key_pressed == ord('p'):
    #     print("button pressed")
    
    if key_pressed == ord('q'):
        Process = False
        break 

cap.release()
cv2.destroyAllWindows()
