from GoVisual import *
import sente


class GoGame:

    def __init__(self, game, board_detect, go_visual):
        self.moves = []
        self.board_detect = board_detect
        self.go_visual = go_visual
        self.game = game
        self.current_player = None


    def initialize_game(self, frame, current_player="BLACK"): #current_player = "BLACK" or "WHITE"
        # self.moves = []
        # self.current_player = current_player
        
        # self.frame = frame
        # self.board_detect.process_frame(frame)
        # self.populate_game()
        # if not self.game.get_active_player().name == current_player:
        #     self.game.pss()

        # return self.go_visual.final_position()
        return self.main_loop(frame)
    
    
    def main_loop(self, frame):
        self.frame = frame
        self.board_detect.process_frame(frame)
        self.define_new_move()
        
        return self.go_visual.final_position(), self.get_sgf()
    
    def play_move(self, x, y, stone_color):
        color = "white" if stone_color == 2 else "black"
        try:
            
            self.game.play(x, y, sente.stone(stone_color))
            
        except sente.exceptions.IllegalMoveException as e:
            error_message = f"A violation of go game rules has been found in position {x}, {y}\n"
            if "self-capture" in str(e):
                raise Exception(error_message + f" --> {color} stone at this position results in self-capture")
            if "occupied point" in str(e):
                raise Exception(error_message + " --> The Desired move lies on an occupied point")
            if "Ko point" in str(e):
                raise Exception(error_message + " --> The Desired move lies on a Ko point")
            if "turn" in str(e) and "It is not currently" in str(e):
                raise Exception(error_message + f"It is not currently {color}'s turn\n")
            raise Exception(error_message + str(e))
            
    
    def define_new_move(self):
        detected_state = np.transpose(self.board_detect.get_state(), (1, 0, 2))
        current_state = self.game.numpy(["black_stones", "white_stones"])
        
        difference = detected_state - current_state
        black_stone_indices = np.argwhere(difference[:, :, 0] == 1)
        white_stone_indices = np.argwhere(difference[:, :, 1] == 1)
        
        # print("black", np.argwhere(detected_state[:, :, 0] == 1))
        # print("black", np.argwhere(current_state[:, :, 0] == 1))
        # print("white", np.argwhere(detected_state[:, :, 1] == 1))
        # print("white", np.argwhere(current_state[:, :, 1] == 1))
        
        if len(black_stone_indices) + len(white_stone_indices) > 1:
            print("MORE THAN ONE STONE WAS ADDED")
            return
        if len(black_stone_indices) != 0:
            self.play_move(black_stone_indices[0][0] + 1, black_stone_indices[0][1] + 1, 1) # sente.stone(1)/ 1 is black_stone
            self.moves.append(('B', (black_stone_indices[0][0], 18 - black_stone_indices[0][1])))
            return
        if len(white_stone_indices) != 0: 
            self.play_move(white_stone_indices[0][0] + 1, white_stone_indices[0][1] + 1, 2) # sente.stone(2)/ 2 is white_stone
            self.moves.append(('W', (white_stone_indices[0][0], 18 - white_stone_indices[0][1])))
            return
        print("no moves detected")
    
    def populate_game(self):
        detected_state = np.transpose(self.board_detect.get_state(), (1, 0, 2))
        
        black_stone_indices = np.argwhere(detected_state[:, :, 0] == 1)
        white_stone_indices = np.argwhere(detected_state[:, :, 1] == 1)
        
        for stone in black_stone_indices:
            self.play_move(stone[0] + 1, stone[1] + 1, 1)
            self.game.pss()
        
        self.game.pss()
        
        for stone in white_stone_indices:
            self.play_move(stone[0] + 1, stone[1] + 1, 2)
            self.game.pss()
        
        self.game.pss()
            
        
            
    
    def get_sgf(self):
        return sente.sgf.dumps(self.game)
# %%