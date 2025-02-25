from ultralytics import YOLO
import sys
import os

sys.path.append("Post_treatment_AI/Code")
from Fill_gaps_model import *
import cv2
from GoBoard import GoBoard
# Get the absolute path of the current script
script_dir = os.path.dirname(os.path.abspath(__file__))

# Construct the absolute path to the model file
model_path = os.path.join(script_dir, "Post_treatment_AI/Code/modelCNN.keras")


#Load the model
model_IA=load_model(model_path)
model = YOLO('model.pt')

def image_to_board_matrix(image_file, model):
    # Create an instance of the GoBoard class
    go_board = GoBoard(model)
    
    # Read the image file
    frame = cv2.imread(image_file)
    
    # Process the frame to detect stones and board state
    go_board.process_frame(frame)
    
    # Convert the state to a 2D board matrix
    return go_board.state_to_array()

def fill_gaps_photo(model, sequence_with_gap, gap_start, gap_end, black_possible_moves, white_possible_moves):
    """
    Fill the gaps in the sequen ce with the best moves chosen from the list of possible moves.

    Args:
        model: The trained model to predict the best move.
        sequence_with_gap (list of np.array): The sequence of board states with gaps (missing moves).
        gap_start (int): The start index of the gap.
        gap_end (int): The end index of the gap.
        black_possible_moves (list of tuple): Possible moves for black.
        white_possible_moves (list of tuple): Possible moves for white.

    Returns:
        filled_sequence (list of np.array): The sequence with the gaps filled.
    """
    filled_sequence = sequence_with_gap.copy()  # Avoid modifying the original sequence
    array1 = sequence_with_gap[0]
    # Count the number of 1s and 2s
    count_1 = np.count_nonzero(array1 == 1)  # Counts the number of 1s
    count_2 = np.count_nonzero(array1 == 2)  # Counts the number of 2s

    # Determine player_turn
    if count_1 == count_2:
        current_player = 1
    else:
        current_player = 2

    # Copy possible moves to avoid mutating the original lists
    black_moves = black_possible_moves.copy()
    white_moves = white_possible_moves.copy()

    # Iterate over each gap in the sequence
    for gap_index in range(gap_start, gap_end):
        # Extract the current state of the board at this gap
        current_board_state = filled_sequence[gap_index - 1]

        # Choose the appropriate move list based on the current player
        possible_moves = black_moves if current_player == 1 else white_moves

        # Recalculate valid moves for the current board state
        valid_moves = [
            move for move in possible_moves
            if current_board_state[move[0], move[1]] == 0
        ]

        # Initialize a list to store the candidate boards
        candidate_boards = []
        candidate_moves = []

        # For each valid move, simulate placing a stone and prepare the candidate board
        for move in valid_moves:
            x, y = move
            candidate_board = current_board_state.copy()
            candidate_board[x, y] = current_player  # Place current player's stone
            candidate_boards.append(candidate_board)
            candidate_moves.append(move)  # Keep track of the valid move

        # If no valid candidate boards, continue (no valid move)
        if not candidate_boards:
            print(f"No valid moves for gap index {gap_index}, skipping.")
            continue

        # Convert candidate_boards to a numpy array
        candidate_boards = np.array(candidate_boards)

        # Ensure the correct shape for the model (add the channel dimension)
        candidate_boards = np.expand_dims(candidate_boards, axis=-1)  # Shape: (batch_size, 19, 19, 1)
        candidate_boards = candidate_boards.astype(np.float32)

        # Predict the probabilities for each candidate board
        probabilities = model.predict(candidate_boards)

        # Get the index of the best move based on the highest probability
        best_move_idx = np.argmax(probabilities[:, current_player - 1])  # Current player determines the index
        best_move = candidate_moves[best_move_idx]

        # Update the board state with the best move
        x, y = best_move
        filled_sequence[gap_index] = current_board_state.copy()
        filled_sequence[gap_index][x, y] = current_player  # Place current player's stone

        # Remove the chosen move from the appropriate possible_moves list
        if current_player == 1:
            black_moves.remove(best_move)
        else:
            white_moves.remove(best_move)
            
        # Switch player for the next move (alternate between 1 and 2)
        current_player = 3 - current_player  # If 1 (black), becomes 2 (white), and vice versa

        print(f"Filling gap index {gap_index} with move {best_move} by player {current_player}")

    return filled_sequence



def fill_photo(img1,img2):
    
    array1= image_to_board_matrix(img1,model)
    array2= image_to_board_matrix(img2,model)
    
    possible_moves_black, possible_moves_white = get_possible_moves(array1, array2) 

    gap_size=len(possible_moves_black) + len(possible_moves_white) 
    #creating a sequence with a gap of size gap_size
    sequence_with_gap = [array1] + [np.zeros((19, 19), dtype=int) for _ in range(gap_size)] + [array2]
    
    filled_sequence = fill_gaps_photo(model_IA ,sequence_with_gap, 1, gap_size+1, possible_moves_black, possible_moves_white)
    return sgf_to_sequence( filled_sequence)