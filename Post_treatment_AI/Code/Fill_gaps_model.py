#Imports
import numpy as np
from keras.models import load_model
import os
import numpy as np
import sgf


# Get the absolute path of the current script
script_dir = os.path.dirname(os.path.abspath(__file__))

# Construct the absolute path to the model file
model_path = os.path.join(script_dir, "modelCNN.keras")


#Load the model
model=load_model(model_path)

#UTILS
def sgf_coords_to_indices(coord, board_size):
    """Convert SGF coordinates (e.g., 'pd') to array indices."""
    col, row = ord(coord[0]) - ord('a'), ord(coord[1]) - ord('a')
    return board_size - row - 1, col
def sgf_to_sequence(sgf_file, board_size=19):
    """
    Convert an SGF file to a sequence of Go board states.
    
    Args:
        sgf_file (str): Path to the SGF file.
        board_size (int): Size of the Go board.
    
    Returns:
        sequence (list of np.array): Sequence of board states.
    """
    with open(sgf_file, 'r') as f:
        sgf_content = f.read()    
    collection = sgf.parse(sgf_content)
    game = collection[0]  # Assume a single game
    board = np.zeros((board_size, board_size), dtype=int)
    sequence = [board.copy()]
    
    for node in game.rest:
        move = node.properties
        if 'B' in move:  # Black move
            x, y = sgf_coords_to_indices(move['B'][0], board_size)
            board[x, y] = 1
        elif 'W' in move:  # White move
            x, y = sgf_coords_to_indices(move['W'][0], board_size)
            board[x, y] = 2
        sequence.append(board.copy())
    
    return sequence

def sequence_to_sgf(sequence, board_size=19):
    """
    Convert a sequence of Go board states back to SGF format.
    
    Args:
        sequence (list of np.array): Sequence of board states.
        board_size (int): Size of the Go board.
    
    Returns:
        sgf_string (str): SGF representation of the game.
    """
    sgf_moves = []
    prev_board = np.zeros_like(sequence[0])
    
    for board in sequence[1:]:
        diff = board - prev_board
        move = np.where(diff > 0)
        if len(move[0]) > 0:  # There is a move
            x, y = move[0][0], move[1][0]
            color = 'B' if board[x, y] == 1 else 'W'
            sgf_moves.append(f";{color}[{indices_to_sgf_coords(x, y, board_size)}]")
        prev_board = board
    
    sgf_string = f"(;GM[1]SZ[{board_size}]" + "".join(sgf_moves) + ")"
    return sgf_string

def indices_to_sgf_coords(x, y, board_size):
    """Convert array indices to SGF coordinates."""
    return f"{chr(y + ord('a'))}{chr(board_size - x - 1 + ord('a'))}"

def save_sgf_to_file(sgf_string, file_path):
    """
    Save an SGF string to a file.
    
    Args:
        sgf_string (str): SGF content to save.
        file_path (str): Path to save the SGF file.
    """
    with open(file_path, 'w') as f:
        f.write(sgf_string)
    print(f"SGF saved to {file_path}")
def delete_states(sequence, start, end):
    """
    Replace states with zeros to create gaps.
    
    Args:
        sequence (list of np.array): Original sequence of Go board states.
        start (int): Starting index of the gap.
        end (int): Ending index of the gap (exclusive).
    
    Returns:
        modified_sequence (list of np.array): Sequence with states replaced by zeros.
    """
    board_shape = sequence[0].shape
    for i in range(start, end):
        sequence[i] = np.zeros(board_shape, dtype=int)
    return sequence

def get_possible_moves(initial_state, final_state):
    """
    Get possible moves in a gap by subtracting the final state from the initial state.
    
    Args:
        initial_state (np.array): The initial board state.
        final_state (np.array): The final board state.
    Returns:
        black_moves (list of tuple): List of moves made by black.
        white_moves (list of tuple): List of moves made by white.
    """
    # Calculate the difference between states
    difference = final_state - initial_state
    
    # Find all black moves (difference == 1)
    black_moves = np.argwhere(difference == 1)
    black_moves = [tuple(move) for move in black_moves]
    
    # Find all white moves (difference == 2)
    white_moves = np.argwhere(difference == 2)
    white_moves = [tuple(move) for move in white_moves]
    
    return black_moves, white_moves


#FILL GAPS FUNCTION

def fill_gaps(model, sequence_with_gap, gap_start, gap_end, black_possible_moves, white_possible_moves):
    """
    Fill the gaps in the sequence with the best moves chosen from the list of possible moves.

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

    # Determine the current player based on the difference between the last two states before the gap
    state_before_gap_1 = sequence_with_gap[gap_start - 1]
    state_before_gap_2 = sequence_with_gap[gap_start - 2]

    # Subtract the two states to find the last move
    difference = state_before_gap_1 - state_before_gap_2
    current_player = 2 if np.any(difference == 1) else 2  # 1 for black, 2 for white

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
