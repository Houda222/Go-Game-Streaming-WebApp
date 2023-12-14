#%%
import numpy as np
import cv2


class GoVisual:
    """
    class GoVisual: 
    creates a go game visual representation given a Sente game provided by the Sente class
    can navigate through the game using methods such as previous or next while managing the game's logic
    The same instance of Sente is used in the GoGame class, which means it gets automatically updated each move 
    and the attributes of the class get updated via the initialize_param function
    """

    def __init__(self, game):
        """
        Constructor method for GoBoard.

        Parameters:
        -----------
        game : Sente
            the game instance created by Sente and updated by GoGame 
        """
        self.game = game
        self.board_size = 19
        self.last_move = None
        self.cursor = len(self.get_moves())
        self.track_progress = True

    def get_stones(self, board):
        """
        Count and collect positions of the stones on the board.

        Parameters:
        -----------
        moves : list
            A Sequence of moves provided by Sente

        """
        self.black_stones = []
        self.white_stones = []
        for i in range(board.shape[0]):
            for j in range(board.shape[1]):
                if np.array_equal(board[i, j], [1, 0]):  # Black stone
                    self.black_stones.append((i, j))
                elif np.array_equal(board[i, j], [0, 1]):  # White stone
                    self.white_stones.append((i, j))
    

    def update_param(self):
        """
        Initialize parameters of the GoBoard based on the specified number of moves.
        The method should keep track of all the "lost" or deleted moves while using the self.previous method 
        and ensure we're at the right current number of moves.
        The use of both "moves" and "board" is necessary: moves contains the order of stones, which is crucial since we want to navigate through the game
        while board omit the stones that shouldn't be showed (captured, illegal stones).

        Parameters:
        -----------
        nb_moves : int, optional
            Number of moves to initialize the board with. Default is 0.
            Can be positive (used in self.next()) or negative (self.previous()).

        Returns:
        -----------
            None
        """
        deleted_moves = []
        if self.cursor - len(self.get_moves()) != 0:
            deleted_moves = self.get_moves()[self.cursor - len(self.get_moves()):]
        self.game.step_up(len(self.get_moves()) - self.cursor)
        self.get_stones(self.game.numpy(["black_stones", "white_stones"]))        
        
        if self.get_moves() != []:
            self.last_move = self.get_moves()[-1]

        for move in deleted_moves:
                x, y, color = move.get_x()+1, move.get_y()+1, move.get_stone().name
                self.game.play(x,y)

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
    
    def initial_position(self):
        """
        Display the initial position with the first move

        Returns:
        --------
        numpy array
            The resulted board drawn with only the first played move
        """
        self.track_progress = False
        self.cursor = 1

    def final_position(self):
        """
        Display the final position 

        Returns:
        --------
        numpy array
            The resulted board drawn with all the played moves 
        """
        self.track_progress = True
 

    def current_turn(self):
        """
        Display whose turn to play

        Returns:
        --------
        string
            The color of the current turn
        """
        if self.last_move[2].get_stone().name == 'BLACK':
            return 'WHITE' 
        elif self.last_move[2].get_stone().name == 'WHITE' or self.cursor == 0:
            return 'BLACK'
        
    def previous(self):
        """
        Display the previous position

        Returns:
        --------
        numpy array
            The board one move before the displayed position
        """
        self.track_progress = False
        if self.cursor > 1:
            self.cursor -= 1


    def next(self):
        """
        Display the next position

        Returns:
        --------
        numpy array
            The board one move after the displayed position
        """
        self.track_progress = False
        if self.cursor < len(self.get_moves()):
            self.cursor +=1
        
        if self.cursor == len(self.get_moves()):
            self.track_progress = True

    def current_position(self):
        """
        Display the current position

        Returns:
        --------
        numpy array
            The board
        """
        if self.track_progress:
            self.cursor = len(self.get_moves())
        # print("cursor", self.cursor)
        # print("total", len(self.get_moves()))
        self.update_param()
        return self.drawBoard()


    def drawBoard(self):
        """
        Draw the board of the Go game

        Parameters:
        -----------
        number_of_moves_to_show : int
            Define moves we want to plot on the board

        Returns:
        --------
        numpy array
            The resulted board 
        """
    
        square_size = 30
        circle_radius = 12
        
        #set up the board's background
        board =np.full(((self.board_size+1)*square_size, (self.board_size+1)*square_size, 3), (69, 166, 245), dtype=np.uint8)
        board2 = np.zeros((self.board_size, self.board_size))
        
        # Draw lines for the board grid
        
        # for i in range(board_size):
        #     ax.plot([i, i], [0, board_size - 1], color='k', linewidth = 0.7)
        #     ax.plot([0, board_size - 1], [i, i], color='k', linewidth = 0.7)
        
        for i in range(1, self.board_size+1):
            # Vertical lines and letters
            cv2.line(board, (square_size*i, square_size), (square_size*i, square_size*(self.board_size)), (0, 0, 0), thickness=1)
            #plt.text(i, -0.8, chr(97 + i), fontsize=8, color='black')    
            cv2.putText(board, chr(ord('A') + i-1), (square_size*i, 15), fontFace=cv2.FONT_HERSHEY_SIMPLEX, fontScale=0.5, color=(0, 0, 0), thickness=1)
            cv2.putText(board, chr(ord('A') + i-1), (square_size*i, 585), fontFace=cv2.FONT_HERSHEY_SIMPLEX, fontScale=0.5, color=(0, 0, 0), thickness=1)

            # Horizontal lines and letters
            cv2.line(board, (square_size, square_size*i), (square_size*(self.board_size), square_size*i), (0, 0, 0), thickness=1)
            #plt.text(-0.8, i, chr(97 + i), fontsize=8, color='black')  
            cv2.putText(board, str(i), (5, square_size*i), fontFace=cv2.FONT_HERSHEY_SIMPLEX, fontScale=0.5, color=(0, 0, 0), thickness=1)
            cv2.putText(board, str(i), (580, square_size*i), fontFace=cv2.FONT_HERSHEY_SIMPLEX, fontScale=0.5, color=(0, 0, 0), thickness=1)

        # Draw stones
        for stone in self.black_stones:
            row, col = stone
            board2[row, col] = 1
            cv2.circle(board, ((row+1)*square_size, (col+1)*square_size), circle_radius, color=(66, 66, 66), thickness=2) # draw the edge
            cv2.circle(board, ((row+1)*square_size, (col+1)*square_size), circle_radius, color=(0, 0, 0), thickness=-1) # draw the stone

        for stone in self.white_stones:
            row, col = stone
            board2[row, col] = 1
            cv2.circle(board, ((row+1)*square_size, (col+1)*square_size), circle_radius, color=(66, 66, 66), thickness=2) # draw the edge
            cv2.circle(board, ((row+1)*square_size, (col+1)*square_size), circle_radius, color=(255, 255, 255), thickness=-1) # draw the stone
        
        #setting the contour of the last move to a different color
        if not self.last_move is None:
            row, col, color = self.last_move.get_x(), self.last_move.get_y(), self.last_move.get_stone().name
            stone_color = (0, 0, 0) if color == 'BLACK' else (255, 255, 255)
            cv2.circle(board, ((row+1)*square_size, (col+1)*square_size), circle_radius, color=(0,0,255), thickness=2) 
            cv2.circle(board, ((row+1)*square_size, (col+1)*square_size), circle_radius, color=stone_color, thickness=-1) 

        return board

    
    
# # %%
# #Example of usage
# import sente

# g = sente.Game()
# g.play(2,3)
# g.play(2,2)
# g.play(2,4)
# g.play(3,3)
# g.play(3,2)
# g.play(18,18)
# g.play(3,4)
# g.play(17,5)
# g.play(4,3)


# %%
# board = GoVisual(g)
# res = board.current_position()
# cv2.imshow("result", res)
# cv2.waitKey(0)
# cv2.destroyAllWindows()
# #%%
# g.play(4,10)
# #%%
# g.play(10,10)
# # %%
# board.previous()



# # %%
# res = board.current_position()
# cv2.imshow("result", res)
# cv2.waitKey(0)
# cv2.destroyAllWindows()
# # %%
# board.next()


# # %%
# res = board.current_position()
# cv2.imshow("result", res)
# cv2.waitKey(0)
# cv2.destroyAllWindows()
# # %%
# board.final_position()

# # %%
# board.initial_position()
# # %%

# # %%

# %%
