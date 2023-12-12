from GoVisual import *
import sente


class GoGame:
    """
    GoGame is the class responsible for managing the game, comparing frames and finding the newly played move
    """

    def __init__(self, game, board_detect, go_visual):
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

        """
        self.moves = []
        self.board_detect = board_detect
        self.go_visual = go_visual
        self.game = game
        self.current_player = None


    def initialize_game(self, frame, current_player="BLACK"):
        """
        Initialize the game state based on the provided frame and current player.

        This function resets the moves, sets the current player, processes the frame using the board detection module,
        populates the game based on the detected stones, and adjusts the active player if needed.

        Args:
            frame: The frame to initialize the game.
            current_player (str): The current player to set, either "BLACK" or "WHITE".

        Returns:
            Tuple: A tuple containing the current position on the board and the SGF representation of the game.
        """
        # Reset moves and set the current player
        self.moves = []
        self.current_player = current_player

        # Set the current frame for the instance
        self.frame = frame

        # Process the frame using the board detection module
        self.board_detect.process_frame(frame)

        # Populate the game based on the detected stones
        self.auto_play_game_moves()

        # Check and adjust the active player if needed
        if not self.game.get_active_player().name == current_player:
            self.game.pss()

        return self.go_visual.current_position(), self.get_sgf()
        # return self.main_loop(frame)
    
    
    def main_loop(self, frame):
        """
        Main loop for processing frames and updating the game state.

        This function takes a frame as input, processes it using the board detection module,
        and returns the current position on the board along with the SGF representation of the game.

        Args:
            frame: The frame to be processed.

        Returns:
            Tuple: A tuple containing the current position on the board and the SGF representation of the game.
        """
        # Set the current frame for the instance
        self.frame = frame

        # Process the frame using the board detection module
        self.board_detect.process_frame(frame)

        self.define_new_move()
        
        return self.go_visual.current_position(), self.get_sgf()
    
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
            error_message = f"A violation of go game rules has been found in position {x}, {y}\n"

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

        This function compares the current state of the game with the detected state from the board detection module,
        identifies the new black and white stone positions, and plays moves accordingly in the game.

        Returns:
            None
        """
        # Get the detected state from the board detection module
        detected_state = np.transpose(self.board_detect.get_state(), (1, 0, 2))

        # Get the current state of black and white stones in the game
        current_state = self.game.numpy(["black_stones", "white_stones"])

        # Calculate the difference between the detected state and the current state
        difference = detected_state - current_state

        # Identify the indices of newly added black and white stones
        black_stone_indices = np.argwhere(difference[:, :, 0] == 1)
        white_stone_indices = np.argwhere(difference[:, :, 1] == 1)

        # Handle the case where more than one stone was added
        if len(black_stone_indices) + len(white_stone_indices) > 1:
            print("More than one stone was added!")
            return

        # Play a move for a newly added black stone
        if len(black_stone_indices) != 0:
            self.play_move(black_stone_indices[0][0] + 1, black_stone_indices[0][1] + 1, 1)  # 1 is black_stone
            self.moves.append(('B', (black_stone_indices[0][0], 18 - black_stone_indices[0][1])))
            return

        # Play a move for a newly added white stone
        if len(white_stone_indices) != 0:
            self.play_move(white_stone_indices[0][0] + 1, white_stone_indices[0][1] + 1, 2)  # 2 is white_stone
            self.moves.append(('W', (white_stone_indices[0][0], 18 - white_stone_indices[0][1])))
            return

        # Print a message if no moves were detected
        print("No new move detected!")

    
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

            
    def get_sgf(self):
        """
        Get the SGF (Smart Game Format) representation of the current game.

        Returns:
            str: The SGF representation of the game.
        """
        # Use the sente.sgf.dumps function to convert the game to SGF format
        return sente.sgf.dumps(self.game)

# %%