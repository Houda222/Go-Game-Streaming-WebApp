import numpy as np
import cv2


class GoVisual:
    """
    class GoVisual: 
    creates a board given an sgf file provided by the GoSgf class
    can navigate through the game using methods such as previous or next
    """

    def __init__(self, game):
        """"
        Constructor method for GoBoard.

        Parameters:
        -----------
        sgf_url : str
            directory of the sgf file
        """
        self.game = game
        self.moves = self.get_moves()
        self.total_number_of_moves  = len(self.moves)
        self.board_size = 19
        self.current_number_of_moves = self.total_number_of_moves
        self.last_move = None
        self.deleted_moves = []

    def get_stones(self, moves):
        self.nb_black_stones = 0
        self.nb_white_stones = 0
        self.black_stones = []
        self.white_stones = []
        for move in moves:
            # Extract the stone vector at the current position
            row, col, color = move.get_x(), move.get_y(), move.get_stone().name
            # Check the color of the stone
            if color == "BLACK":  # Black stone
                self.nb_black_stones += 1
                self.black_stones.append((row, col))
            elif color == "WHITE":  # White stone
                self.nb_white_stones += 1
                self.white_stones.append((row, col))
    
    
    def update_moves(self, board, moves):
        # Filter out moves that are not present on the board
        valid_moves = []

        for move in moves:
            row, col, color = move.get_x(), move.get_y(), move.get_stone().name
            if ((board[row][col] == [1, 0]).all() or (board[row][col] == [0, 1]).all()):
                valid_moves.append(move)

        return valid_moves
    

    def initialize_param(self, nb_moves=0):
       
        self.get_stones(self.update_moves(self.game.numpy(["black_stones", "white_stones"]), self.get_moves()))

        if nb_moves<0:
            # if nb_moves == -len(self.game.get_sequence())+1:
            #     self.deleted_moves = self.moves[nb_moves:] + self.deleted_moves
            #     self.game.step_up(-nb_moves)
            #     self.moves = self.game.get_sequence()
            #     self.board = self.game.numpy(["black_stones", "white_stones"])
            #     self.get_stones(self.update_moves(self.board, self.game.get_sequence()))
 
            self.deleted_moves = self.moves[nb_moves:] + self.deleted_moves
            self.unique_deleted_moves = []
            for move in self.deleted_moves:
                if move not in self.unique_deleted_moves:
                    self.unique_deleted_moves.append(move)

            self.game.step_up(-nb_moves)
            self.moves = self.get_moves()
            self.board = self.game.numpy(["black_stones", "white_stones"])
            self.get_stones(self.update_moves(self.board, self.get_moves()))

        elif nb_moves>0:
            if len(self.deleted_moves) != 0 :

                while nb_moves > 0:
                    move = self.deleted_moves.pop(0)
                    x, y, color = move.get_x()+1, move.get_y()+1, move.get_stone().name
                    self.game.play(x,y)
                    nb_moves -= 1

                self.board = self.game.numpy(["black_stones", "white_stones"])
                self.moves = self.get_moves()
                self.get_stones(self.update_moves(self.board, self.moves))

        if self.get_moves() != []:
            self.last_move = self.get_moves()[-1]
    
    
    def get_moves(self):
        moves = []
        for move in self.game.get_sequence():
            if move.get_x() == 19 and move.get_y() == 19:
                continue
            moves.append(move)
        return moves
    

    def drawBoard(self):
        """
        Draw the board up to a certain number of moves

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
            cv2.putText(board, str(20-i), (5, square_size*i), fontFace=cv2.FONT_HERSHEY_SIMPLEX, fontScale=0.5, color=(0, 0, 0), thickness=1)
            cv2.putText(board, str(20-i), (580, square_size*i), fontFace=cv2.FONT_HERSHEY_SIMPLEX, fontScale=0.5, color=(0, 0, 0), thickness=1)

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

    
    
    def initial_position(self):
        """
        Display the initial position with the first move

        Returns:
        --------
        numpy array
            The resulted board drawn with only the first played move
        """
        self.initialize_param(-len(self.get_moves())+1)
        return self.drawBoard()

    def final_position(self):
        """
        Display the final position 

        Returns:
        --------
        numpy array
            The resulted board drawn with all the played moves 
        """
        nb_moves = len(self.moves) + len(self.deleted_moves)
        self.initialize_param(nb_moves)
        return self.drawBoard()

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
        elif self.last_move[2].get_stone().name == 'BLACK' or self.current_number_of_moves == 0:
            return 'BLACK'
        
    def previous(self):
        """
        Display the previous position

        Returns:
        --------
        numpy array
            The board one move before the displayed position
        """
        self.initialize_param(-1)
        return self.drawBoard()

    def next(self):
        """
        Display the next position

        Returns:
        --------
        numpy array
            The board one move after the displayed position
        """
        self.initialize_param(1)
        return self.drawBoard()




# # %%
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



# # %%
# board = GoVisual(g)
# res = board.final_position()
# cv2.imshow("result", res)
# cv2.waitKey(0)
# cv2.destroyAllWindows()



# # %%
# previous = board.previous()
# cv2.imshow("result", previous)

# cv2.waitKey(0)


# cv2.destroyAllWindows()



# #%%
# next = board.next()
# cv2.imshow("result", next)
# cv2.waitKey(0)
# cv2.destroyAllWindows()


# #%%
# next = board.next()
# cv2.imshow("result", next)
# cv2.waitKey(0)
# cv2.destroyAllWindows()

# # %%
# init = board.initial_position()
# cv2.imshow("result", init)
# cv2.waitKey(0)
# cv2.destroyAllWindows()

# # %%
# next = board.next()
# cv2.imshow("result", next)



# cv2.waitKey(0)
# cv2.destroyAllWindows()
# # %%
# res = board.final_position()
# cv2.imshow("result", res)
# cv2.waitKey(0)

# cv2.destroyAllWindows()
# # %%

# %%
