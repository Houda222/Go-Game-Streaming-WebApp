#%%
from GoVisual import *
from GoBoard import *
import sente

import sys
sys.path.append("Post_treatment_Algo/Code")
from corrector_noAI import correctorNoAI
from corrector_withAI import correctorAI
from sgf_to_numpy import to_sgf

sys.path.append("Post_treatment_AI/Code")
from Fill_gaps_model import *



class GoGame:
    """
    GoGame is the class responsible for managing the game, comparing frames and finding the newly played move
    """

    def __init__(self, game, board_detect, go_visual, transparent_mode):
        """
        Constructor method for the GoGame class.

        Parameters:
        -----------
        game : Sente
            The game instance associated with the GoGame.

        board_detect : GoBoard
            The GoBoard instance responsible for board detection.

        go_visual : GoVisual
            The GoVisual instance for visualizing the Go board.

        Attributes:
        -----------
        moves : list
            List to store the moves made in the game.

        board_detect : GoBoard
            GoBoard instance responsible for board detection.

        go_visual : GoVisual
            GoVisual instance for visualizing the Go board.

        game : Sente
            Game instance associated with the GoGame.

        current_player : None
            Placeholder for the current player in the game.
        
        transparent_mode : bool
            Boolean flag to enable or disable transparent mode.
        
        recent_moves_buffer : list
            List to store the recent moves for game mode.
        
        buffer_size : int
            Maximum size of the recent moves buffer.
        
        numpy_board : list
            List to store the numpy representation of the board at each move for post-treatment.

        """
        self.moves = []
        self.board_detect = board_detect
        self.go_visual = go_visual
        self.game = game
        self.current_player = None
        self.transparent_mode = transparent_mode
        self.recent_moves_buffer= []
        self.buffer_size = 5
        self.numpy_board = []
    
    def set_transparent_mode(self, bool_):
        self.transparent_mode = bool_


    def initialize_game(self, frame, current_player="BLACK", endGame=False):
        """
        Initialize the game state based on the provided frame and current player.

        This function resets the moves, sets the current player, processes the frame using the board detection module,
        populates the game based on the detected stones, and adjusts the active player if needed.

        Args:
            frame: The frame to initialize the game.
            current_player (str): The current player to set, either "BLACK" or "WHITE".
            endGame (bool): A boolean flag to determine if the game is ending.

        Returns:
            For game mode:
                Tuple: A tuple containing the current position on the board and the SGF representation of the game.
            For transparent mode:
                Tuple: A tuple containing the transparent mode representation of the board and the post-treatment SGF.
        """
        # Reset moves and set the current player
        self.moves = []
        self.current_player = current_player

        # Set the current frame for the instance
        self.frame = frame

        # Process the frame using the board detection module
        self.board_detect.process_frame(frame)
        
        if self.transparent_mode:
            detected_state = self.transparent_mode_moves()
            return self.go_visual.draw_transparent(detected_state), self.post_treatment(endGame)
        
        else:
            # Populate the game based on the detected stones
            self.auto_play_game_moves()

            # Check and adjust the active player if needed
            if not self.game.get_active_player().name == current_player:
                self.game.pss()

            return self.go_visual.current_position(), self.get_sgf()
    
    
    def main_loop(self, frame, endGame=False):
        """
        Main loop for processing frames and updating the game state.

        This function takes a frame as input, processes it using the board detection module,
        and returns the current position on the board along with the SGF representation of the game.

        Args:
            frame: The frame to be processed.
            endGame (bool): A boolean flag to determine if the game is ending.

        Returns:
            For game mode:
                Tuple: A tuple containing the current position on the board and the SGF representation of the game.
            For transparent mode:
                Tuple: A tuple containing the transparent mode representation of the board and the post-treatment SGF.
        """
        # Set the current frame for the instance
        self.frame = frame

        # Process the frame using the board detection module
        self.board_detect.process_frame(frame)

        if self.transparent_mode:
            detected_state = self.transparent_mode_moves()
            return self.go_visual.draw_transparent(detected_state), self.post_treatment(endGame)
        else:
            self.define_new_move()        
            return self.go_visual.current_position(), self.get_sgf()
    

    def copyBoardToNumpy(self):
        """
        Copy the board state to a numpy array for post-treatment and stock it in
        the numpy_board attribute.
        Black stones are represented by 1, white stones by 2, and empty positions by 0.

        Returns:
            None
        """
        final_board = np.zeros((19, 19), dtype=int)
        final_board[self.board_detect.get_state()[:, :, 0] == 1] = 1  # 1 for black stones
        final_board[self.board_detect.get_state()[:, :, 1] == 1] = 2  # 2 for white stones
           
        if (self.numpy_board == [] or np.any(final_board != self.numpy_board[-1])):
            self.numpy_board.append(final_board)

    def transparent_mode_moves(self):
        """
        This function retrieves the current state of the board in transparent mode and
        copies it for pos-treatment.

        Returns:
            np.array: The current state of the board in transparent mode.
        """

        self.copyBoardToNumpy()
        return np.transpose(self.board_detect.get_state(), (1, 0, 2))
    
    def play_move(self, x, y, stone_color):
        """
        Play a move in the game at the specified position.

        Args:
            x (int): The x-coordinate of the move.
            y (int): The y-coordinate of the move.
            stone_color (int): The color of the stone to be played (1 for black, 2 for white).

        Returns:
            None
        """
        # Determine the color of the stone based on the stone_color parameter
        color = "white" if stone_color == 2 else "black"

        try:
            # Attempt to play the move in the game using sente.stone
            self.game.play(x, y, sente.stone(stone_color))

        except sente.exceptions.IllegalMoveException as e:
            # Handle different types of illegal move exceptions and raise a custom Exception with details
            error_message = f"[GoGame Exception] - A violation of go game rules has been found in position {x}, {y}\n"

            if "self-capture" in str(e):
                raise Exception(error_message + f" --> {color} stone at this position results in self-capture")
            if "occupied point" in str(e):
                raise Exception(error_message + " --> The desired move lies on an occupied point")
            if "Ko point" in str(e):
                raise Exception(error_message + " --> The desired move lies on a Ko point")
            if "turn" in str(e) and "It is not currently" in str(e):
                raise Exception(error_message + f"It is not currently {color}'s turn\n")

            # If the exception doesn't match any specific cases, raise a general exception with the original message
            raise Exception(error_message + str(e))

            
    
    def define_new_move(self):
        """
        Define a new move based on the difference between the current game state and the detected state.
        """
        detected_state = np.transpose(self.board_detect.get_state(), (1, 0, 2))
        current_state = self.game.numpy(["black_stones", "white_stones"])
        difference = detected_state - current_state

        # Identify the indices of newly added black and white stones
        black_stone_indices = np.argwhere(difference[:, :, 0] == 1) #positions [x,y] où l'état présent et l'état passé du goban diffèrent pour noir
        white_stone_indices = np.argwhere(difference[:, :, 1] == 1)
        black_stone_indices_disappeared = np.argwhere(difference[:, :, 0] == -1)
        white_stone_indices_disappeared = np.argwhere(difference[:, :, 1] == -1)

        # Check for more than one stone being added
        if len(black_stone_indices) + len(white_stone_indices) > 1:
            self.process_multiple_moves(black_stone_indices, white_stone_indices)
            return

        # Play a move for a newly added black stone
        if len(black_stone_indices) != 0:
            if len(black_stone_indices)!=0 and len(black_stone_indices_disappeared)!=0: #if one stone has been moved, we adapt the sgf file
                self.game.step_up()
                print("A stone has been moved")
            self.play_move(black_stone_indices[0][0] + 1, black_stone_indices[0][1] + 1, 1)  # 1 is black_stone
            # black_stone_indices[0][0] + 1 : ligne du coup joué, black_stone_indices[0][1] + 1 : colonne du coup joué
            # On ajoute 1 car il n'y a pas de "zéro-ième" ligne
            self.moves.append(('B', (black_stone_indices[0][0], 18 - black_stone_indices[0][1])))
            self.recent_moves_buffer.append({'color': 'B', 'position': black_stone_indices[0]})
            self.trim_buffer()

        # Play a move for a newly added white stone
        if len(white_stone_indices) != 0:
            if len(white_stone_indices)==1 and len(white_stone_indices_disappeared)==1:
                self.game.step_up()
                print("A stone has been moved")
            self.play_move(white_stone_indices[0][0] + 1, white_stone_indices[0][1] + 1, 2)  # 2 is white_stone
            self.moves.append(('W', (white_stone_indices[0][0], 18 - white_stone_indices[0][1])))
            self.recent_moves_buffer.append({'color': 'W', 'position': white_stone_indices[0]})
            self.trim_buffer()

    def trim_buffer(self):
        # Ensure buffer size stays within limit
        if len(self.recent_moves_buffer) > self.buffer_size:
            self.recent_moves_buffer.pop(0)

    def process_multiple_moves(self, black_stones, white_stones):
        for stone in black_stones:
            self.play_move(stone[0] + 1, stone[1] + 1, 1)
            self.moves.append(('B', (stone[0], 18 - stone[1])))

        for stone in white_stones:
            self.play_move(stone[0] + 1, stone[1] + 1, 2)
            self.moves.append(('W', (stone[0], 18 - stone[1])))
    
    def auto_play_game_moves(self):
        """
        Automatically populates the game board with moves based on the detected state.

        This function retrieves the detected state from the board detection module,
        identifies the indices of black and white stones, and plays moves for each player.

        Black stones are represented by player 1, and white stones are represented by player 2.
        After playing all black and white stones, the function passes a turn for each player.

        Returns:
            None
        """
        # Get the detected state from the board detection module
        detected_state = np.transpose(self.board_detect.get_state(), (1, 0, 2))

        # Identify the indices of black and white stones on the board
        black_stone_indices = np.argwhere(detected_state[:, :, 0] == 1)
        white_stone_indices = np.argwhere(detected_state[:, :, 1] == 1)

        # Play moves for black stones
        for stone in black_stone_indices:
            self.play_move(stone[0] + 1, stone[1] + 1, 1)
            self.game.pss()

        # Pass a turn after playing all black stones
        self.game.pss()

        # Play moves for white stones
        for stone in white_stone_indices:
            self.play_move(stone[0] + 1, stone[1] + 1, 2)
            self.game.pss()

        # Pass a turn after playing all white stones
        self.game.pss()

    def correct_stone(self, old_pos, new_pos):
        """
        Manually correct the position of a stone on the board.

        This function corrects the position of a stone on the board by first converting the old and new positions to
        coordinates, checking if the new position is already occupied, and then moving the stone to the new position
        while preserving the order of moves.

        Args:
            old_pos (str): The old position of the stone (e.g., "A1").
            new_pos (str): The new position to correct the stone to (e.g., "S19").

        Returns:
            None
        """
        # Convert old and new positions to coordinates
        old_x = int(ord(str(old_pos[0])) - 64)
        old_y = int(old_pos[1:]) 
        new_x = int(ord(str(new_pos[0])) - 64)
        new_y = int(new_pos[1:]) 

        # Iterate through the moves to check if the new position is already occupied
        for i in range(len(self.get_moves())):
            
            if int(self.get_moves()[i].get_x()+1) == new_x and int(self.get_moves()[i].get_y()+1) == new_y:
                print("This position is already occupied!")
                return
            
            else:
                # If the old position is found, correct the stone's position
                if int(self.get_moves()[i].get_x()+1) == old_x and int(self.get_moves()[i].get_y()+1) == old_y:
                    print("Found!")
                    deleted_moves = self.get_moves()[i - len(self.get_moves()):]
                    self.game.step_up(len(self.get_moves()) - i)
                    self.game.play(new_x, new_y)
                    deleted_moves.pop(0)
                    for move in deleted_moves:
                        x, y, color = move.get_x()+1, move.get_y()+1, move.get_stone().name
                        self.game.play(x,y)

    def delete_last_move(self):
        """
         Delete the last move in the game sequence.

        This function steps up the game to remove the last move from the game sequence.

        Returns:
        None
        """
        
        self.game.step_up()

    def get_moves(self):
        """
        Remove pass move; when we use game.pss(), a move named "u19" is added to the sequence. 

        Returns:
        --------
        moves: List
            Cleaned sequence
        """
        moves = []
        for move in self.game.get_sequence():
            if move.get_x() == 19 and move.get_y() == 19:
                continue
            moves.append(move)
        return moves


    def get_sgf(self):
        """
        Get the SGF (Smart Game Format) representation of the current game.

        Returns:
            str: The SGF representation of the game.
        """
        # Use the sente.sgf.dumps function to convert the game to SGF format
        return sente.sgf.dumps(self.game)
    
    def post_treatment(self, endGame):
        """
        Post-treatment of the game to correct the sequence of moves.
        Use AI and/or algorithms to correct the detection errors.

        Returns:
            str: The SGF representation of the corrected game.
        """
        if endGame:
            liste_coups = correctorAI(self.numpy_board)
            return to_sgf(liste_coups)



# %%
