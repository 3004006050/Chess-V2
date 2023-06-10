from math import trunc
from queue import Empty
from tkinter import W
from typing import Counter, Self
from xml.sax.handler import feature_namespace_prefixes
from chessassets.readconfig import read_config
import pygame
import os
import sys
import copy
import time
from stockfish import Stockfish

def resource_path(relative_path):
    try:
    # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

stockfish = Stockfish(resource_path("chessassets\stockfish-11-win\Windows\stockfish_20011801_32bit.exe")) # pass in binary file location
stockfish.update_engine_parameters(read_config())

#piece and screen defining
pygame.init()
PIECE_SIZE = 60
SCREEN_SIZE = [PIECE_SIZE * 8 + 200, PIECE_SIZE * 8]
screen = pygame.display.set_mode(SCREEN_SIZE)
pygame.display.set_caption('Chess')
font = pygame.font.SysFont("comicsans", 64, bold=True)
background_color = (139, 0, 0)
en_passantable = None
# self.black_castle = [True, True]
# self.white_castle = [True, True]

class Timer:
    def __init__(self, minute, second, x, y):
        self.minute = minute
        self.second = second
        self.x = x
        self.y = y

    def countdown(self):
        if self.second == 0:
            self.minute -= 1
            self.second = 59
        else:
            self.second -= 1

    def draw(self, screen):
        timer_label = font.render(f"{self.minute}:{self.second}", 1,
                                  (178, 34, 34))
        screen.blit(timer_label, (self.x, self.y))


class Game:
    #Game defines all pieces's strings and board, along with turning
    def __init__(self):
        self.black_castle = [True, True]
        self.white_castle = [True, True]
        self.last_move_possibilities = []
        self.col_conversion = {0 : "a", 1 : "b", 2 : "c", 3: "d", 4 : "e", 5 : "f", 6 : "g", 7 : "h"}
        self.best_img = pygame.image.load( resource_path(f'{os.getcwd()}\\chessassets\\feedback_icons\\best.png') ).convert_alpha()
        self.best_img = pygame.transform.smoothscale(self.best_img, (100, 100))
        self.good_img = pygame.image.load( resource_path(f'{os.getcwd()}\\chessassets\\feedback_icons\\good.png') ).convert_alpha()
        self.good_img = pygame.transform.smoothscale(self.good_img, (100, 100))
        self.last_move = ""
        self.last_time_recorded = time.time()
        self.curr_time = time.time()
        self.best_move_hist = [] # keeps track of each turn's best move
        self.good_move_hist = [] # keeps track of each turn's 4 best moves
        self.half_move = -1
        self.whole_move = 1
        self.evalw = self.get_evalw()
        self.eval = stockfish.get_evaluation()
        self.board = [
            [
                'Black_Rook', 'Black_Knight', 'Black_Bishop', 'Black_Queen',
                'Black_King', 'Black_Bishop', 'Black_Knight', 'Black_Rook'
            ],
            [
                'Black_Pawn', 'Black_Pawn', 'Black_Pawn', 'Black_Pawn',
                'Black_Pawn', 'Black_Pawn', 'Black_Pawn', 'Black_Pawn'
            ],
            ['', '', '', '', '', '', '', ''],
            ['', '', '', '', '', '', '', ''],
            ['', '', '', '', '', '', '', ''],
            ['', '', '', '', '', '', '', ''],
            [
                'White_Pawn', 'White_Pawn', 'White_Pawn', 'White_Pawn',
                'White_Pawn', 'White_Pawn', 'White_Pawn', 'White_Pawn'
            ],
            [
                'White_Rook', 'White_Knight', 'White_Bishop', 'White_Queen',
                'White_King', 'White_Bishop', 'White_Knight', 'White_Rook'
            ],
        ]
        self.fen_trans = {'Black_Rook':"r", 'Black_Knight':"n", 'Black_Bishop':"b", 'Black_Queen':"q",
                'Black_King':"k",'Black_Pawn':"p", 'White_Pawn':"P",
                'White_Rook':"R", 'White_Knight':"N", 'White_Bishop':"B", 'White_Queen':"Q",
                'White_King':"K"}
        self.turn = 'White'  # white/black
        self.piece_location = {
            'White_Rook', 'White_Knight', 'White_Bishop', 'White_King',
            'White_Queen'
        }
    def count_pieces(self):
        counter = 0
        for row in self.board:
            for square in row:
                if square:
                    counter += 1
        return counter
    def find_pawns(self):
        pawn_board = ""
        for row in self.board:
            for square in row:
                if square[6:] == "Pawn":
                    pawn_board += "p"
                else:
                    pawn_board += " "

        return pawn_board
    def get_evalw(self):
        eval = stockfish.get_evaluation()
        if eval["type"] == "cp":
            if eval["value"] < -2000: 
                return 1
            if eval["value"] > 2000:
                return 99 
            return (eval["value"]+2000)/40
        else: 
            return -1*(48 * eval['value'])/5 + 543/5 if eval['value'] > 0 else -1 * (48 * eval['value'])/5 - 43/5


    def set_fen(self):
        fen = ""
        for row in self.board:
            empty_counter = 0
            for square in row:
                if square != "":
                    if empty_counter != 0:
                        fen += str(empty_counter)
                        empty_counter = 0
                    fen += self.fen_trans[square]
                else:
                    empty_counter += 1
            if empty_counter != 0:
                fen += str(empty_counter)
            fen += "/"
        fen = fen[:-1]


        if self.turn == "White":
            fen += " w "
        else:
            fen += " b "
        can_castle = False

        if self.white_castle[0] and game.board[7][4] == "White_King":
            fen += "K"
            can_castle = True
        if self.white_castle[1] and game.board[7][4] == "White_King":
            fen += "Q"
            can_castle = True
        if self.black_castle[0] and game.board[0][4] == "Black_King":
            fen += "k"
            can_castle = True
        if self.black_castle[1] and game.board[0][4] == "Black_King":
            fen += "q" 
            can_castle = True
        if not can_castle:
            fen += "-"
        fen += " "
        if en_passantable:
            if game.turn == "White":
                fen += self.col_conversion[en_passantable] + "6"
            if game.turn == "Black":
                fen += self.col_conversion[en_passantable] + "3"
        else:
            fen += "-"
        fen += " "
        fen += str(self.half_move)
        fen += " "
        fen += str(self.whole_move )
        #where to write fen
        return fen

# making game object
game = Game()


#images loading
images = {}
for color in ['Black', 'White']:
    for piece in ['King', 'Queen', 'Knight', 'Bishop', 'Rook', 'Pawn']:
        name = color + '_' + piece
        images[name] = pygame.image.load(resource_path('chessassets/pieces/' + name + '.png'))


def get_square_color(row, col):
    """"
    makes board alternate white and grey
  
    :param row: row specifies the row of a given square
  
    :param col: col specifies the column of a given square
  
    :return: returns the color of a given square
    """

    if row % 2 == 0:
        if col % 2 == 0:
            return (255, 255, 255)
        else:
            return (169, 169, 169)
    else:
        if col % 2 == 0:
            return (169, 169, 169)
        else:
            return (255, 255, 255)


def draw_board(board_to_draw):
    """
    draw board draws the board 
    row in range defines how many availible rows
    col in range defines how many availible columns
    piece color defines if the piece==white or black
    piece x and y define space on plane
  
   :param board_to_draw: gives it the board that needs to be drawn
    """
    for row in range(8):
        for col in range(8):
            current_piece = board_to_draw[row][col]
            piece_color = get_square_color(row, col)

            piece_x = col * PIECE_SIZE
            piece_y = row * PIECE_SIZE

            pygame.draw.rect(screen, piece_color,
                             [piece_x, piece_y, PIECE_SIZE, PIECE_SIZE])

            if current_piece != '':
                screen.blit(images[current_piece], [piece_x, piece_y])
    if game_over:

        checkmate_string = game.turn + "lost"

        checkmate_label = font.render(str(checkmate_string), True, (178, 34, 34))

        screen.blit(checkmate_label, (200, 250))


#to do: add checks for pins


def legal_move(current_piece, old_row, old_col, new_row, new_col, board):
    """
    legal move defined as a way to make sure pieces    can move properly and within the board.
  
    current_piece makes the piece selected use the code to find where the piece can move
    old_row and old_col partner to show the coordinate of the piece
    new_row and new_col partner to show the coordinate of the desired square to be moved to
  
    new_row and new_col conditional makes it so pieces cannot move outside the board because the move will be marked illegal.
    elif statements define how each piece can move by using row_change and col_change which define how much a piece can move before being returned as False.
    return True and False mean legal and illegal, respectively
    """
    global en_passantable
    if new_row < 0 or new_row > 7 or new_col < 0 or new_col > 7:

        return False
    elif new_row - old_row == 0 and new_col - old_col == 0:
        return False

    row_change = abs(new_row - old_row)
    col_change = abs(new_col - old_col)

    if current_piece == "Black_Rook" or current_piece == "White_Rook":
        if not (old_row == new_row or old_col == new_col):
            return False
        start_row = min(old_row, new_row)
        start_col = min(old_col, new_col)
        for r in range(1, row_change):
            if board[start_row + r][old_col] != "":
                return False
        for c in range(1, col_change):
            if board[old_row][start_col + c] != "":
                return False

        if current_piece[:6] == board[new_row][new_col][:6] or "King" == board[
                new_row][new_col][6:]:
            return False

        return True
    elif current_piece == "Black_Bishop" or current_piece == "White_Bishop":
        if row_change == col_change:
            start_row = old_row
            start_col = old_col

            while start_row != new_row and start_col != new_col:
                if board[start_row][
                        start_col] != "" and start_row != old_row and start_col != old_col:
                    return False
                if new_row - old_row < 0:
                    start_row -= 1
                else:
                    start_row += 1
                if new_col - old_col < 0:
                    start_col -= 1
                else:
                    start_col += 1
            return True

        else:
            return False
    elif current_piece == "Black_Queen" or current_piece == "White_Queen":
        if row_change == col_change:
            start_row = old_row
            start_col = old_col

            while start_row != new_row and start_col != new_col:
                if board[start_row][
                        start_col] != "" and start_row != old_row and start_col != old_col:
                    return False
                if new_row - old_row < 0:
                    start_row -= 1
                else:
                    start_row += 1
                if new_col - old_col < 0:
                    start_col -= 1
                else:
                    start_col += 1
            return True
        elif old_row == new_row or old_col == new_col:
            start_row = min(old_row, new_row)
            start_col = min(old_col, new_col)
            for r in range(1, row_change):
                if board[start_row + r][old_col] != "":
                    return False
            for c in range(1, col_change):
                if board[old_row][start_col + c] != "":
                    return False
            return True
        return row_change == col_change or old_row == new_row or old_col == new_col
    elif current_piece == "Black_King" or current_piece == "White_King":
        if old_row == 7 and old_col == 4 and current_piece[:5] == "White":
            if new_col == 6 and new_row == 7 and game.white_castle[1]:
                if board[new_row][new_col] == "" and board[new_row][new_col -
                                                                    1] == "":
                    temp_board = copy.deepcopy(board)
                    temp_board[new_row][new_col - 1] = current_piece
                    temp_board[old_row][old_col] = ""
                    if evaluate_check(temp_board, current_piece[:5]):
                        del temp_board
                        return
                    del temp_board
                    return True
            elif new_col == 2 and new_row == 7 and game.white_castle[0]:
                if board[new_row][new_col] == "" and board[new_row][
                        new_col - 1] == "" and board[new_row][new_col +
                                                              1] == "":
                    temp_board = copy.deepcopy(board)
                    temp_board[new_row][new_col + 1] = current_piece
                    temp_board[old_row][old_col] = ""
                    if evaluate_check(temp_board, current_piece[:5]):
                        del temp_board
                        return
                    del temp_board
                    return True
        if old_row == 0 and old_col == 4 and current_piece[:5] == "Black":
            if new_col == 6 and new_row == 0 and game.black_castle[1]:
                if board[new_row][new_col] == "" and board[new_row][new_col -
                                                                    1] == "":
                    temp_board = copy.deepcopy(board)
                    temp_board[new_row][new_col - 1] = current_piece
                    temp_board[old_row][old_col] = ""
                    if evaluate_check(temp_board, current_piece[:5]):
                        del temp_board
                        return
                    del temp_board
                    return True
            elif new_col == 2 and new_row == 0 and game.black_castle[0]:
                if board[new_row][new_col] == "" and board[new_row][
                        new_col - 1] == "" and board[new_row][new_col +
                                                              1] == "":
                    temp_board = copy.deepcopy(board)
                    temp_board[new_row][new_col + 1] = current_piece
                    temp_board[old_row][old_col] = ""
                    if evaluate_check(temp_board, current_piece[:5]):
                        del temp_board
                        return
                    del temp_board
                    return True
        return (row_change == 1 and col_change == 1) or (
            row_change == 1 and col_change == 0) or (row_change == 0
                                                     and col_change == 1)
    elif current_piece == "Black_Knight" or current_piece == "White_Knight":
        return (row_change == 2 and col_change == 1) or (row_change == 1
                                                         and col_change == 2)
    elif current_piece[6:] == "Pawn":
        if current_piece[:5] == 'White':
            if board[new_row][new_col] != "" and col_change != 1:
                return False
            if board[new_row][
                    new_col] == "" and new_row == old_row - 1 and col_change == 0:
                return True
            if board[new_row][
                    new_col] != "" and new_col != 7 and new_col != 0 and (
                        board[new_row + 1][new_col + 1] != ""
                        or board[new_row + 1][new_col - 1] != ""
                    ):  # taking diagonally while not on edge
                return True
            elif board[new_row][new_col] != "" and new_col == 7 and board[
                    new_row + 1][new_col - 1] == board[old_row][old_col]:
                return True
            elif board[new_row][new_col] != "" and new_col == 0 and board[
                    new_row + 1][new_col + 1] == board[old_row][old_col]:
                return True
            # finished adding
            elif board[old_row][old_col] == board[6][old_col] and board[
                    new_row][new_col] == "" and board[new_row + 1][
                        new_col] == "" and row_change == 2 and col_change == 0:
                en_passantable = new_col
                return True
            # white en passant
            elif en_passantable is not None and abs(
                    en_passantable - old_col
            ) == 1 and old_row == 3 and new_row == 2 and new_col == en_passantable:
                board[old_row][en_passantable] = ""
                return True
        else:  # Black Pawn
            if board[new_row][new_col] != "" and col_change != 1:
                return False
            if board[new_row][
                    new_col] == "" and new_row == old_row + 1 and col_change == 0:
                return True
            elif board[new_row][new_col] != "" and (
                    board[new_row - 1][new_col - 1] == board[old_row][old_col]
                    or board[new_row - 1][new_col + 1]
                    == board[old_row][old_col]):
                return True
            elif board[old_row][old_col] == board[1][old_col] and board[
                    new_row][new_col] == "" and board[new_row - 1][
                        new_col] == "" and row_change == 2 and col_change == 0:
                en_passantable = new_col
                return True
            # black en passant
            elif en_passantable is not None and abs(
                    en_passantable - old_col
            ) == 1 and old_row == 4 and new_row == 5 and new_col == en_passantable:
                board[old_row][en_passantable] = ""
                return True
        return False
        # if row_change == 1 and col_change == 0 and board[new_col][
        #         new_row] == "":
        #     return True
        # elif row_change == 1 and col_change == 1 and board[new_col][
        #         new_row] != "":
        #     return True
        # elif row_change == 2 and col_change == 0:
        #     if current_piece[f] == 'White':
        #         return board[new_col][
        #             new_row - 1] == board[new_col][new_row] == ""
        #     else:
        #         return board[new_col][
        #             new_row + 1] == board[new_col][new_row] == ""


def move(current_piece, old_row, old_col, new_row, new_col, board):
    """ 
    move defines what move was made and makes sure that the old coordinate==empty and the new coordinate has the piece selected
  
    current piece==used in move as the piece that==currently selected
    new_row and new_col verify that current_piece moved there
    old_row and old_col verify that the current_piece left that coordinate, as when a piece moves from a coordinate, another piece cannot be there.
    board makes sure that the other params have a plane to work on, additionally being changed by move
    from 318 onward covers castling
    """
    black_castlet = "not_set"
    white_castlet = "not_set"
    if current_piece[6:] == "King":
        if old_row == 7 and old_col == 4 and current_piece[:5] == "White":
            if new_col == 6 and new_row == 7 and game.white_castle[1]:
                if board[new_row][new_col] == "" and board[new_row][new_col -
                                                                    1] == "":
                    #this makes sure nothing is in the way between the king and the rook for kingside
                    temp_board = copy.deepcopy(board)
                    temp_board[new_row][new_col - 1] = current_piece
                    temp_board[old_row][old_col] = ""
                    if evaluate_check(temp_board, current_piece[:5]):
                        del temp_board
                        return
                    del temp_board
                    board[new_row][new_col] = current_piece
                    board[old_row][old_col] = ""
                    board[new_row][new_col - 1] = "White_Rook"
                    board[new_row][new_col + 1] = ""
                    white_castlet = False
            elif new_col == 2 and new_row == 7 and game.white_castle[0]:
                if board[new_row][new_col] == "" and board[new_row][
                        new_col - 1] == "" and board[new_row][new_col +
                                                              1] == "":
                    temp_board = copy.deepcopy(board)
                    temp_board[new_row][new_col + 1] = current_piece
                    temp_board[old_row][old_col] = ""
                    if evaluate_check(temp_board, current_piece[:5]):
                        del temp_board
                        return
                    del temp_board
                    board[new_row][new_col] = current_piece
                    board[old_row][old_col] = ""
                    board[new_row][new_col + 1] = "White_Rook"
                    board[new_row][new_col - 2] = ""
                    white_castlet = False
        if old_row == 0 and old_col == 4 and current_piece[:5] == "Black":
            if new_col == 6 and new_row == 0 and game.black_castle[1]:
                if board[new_row][new_col] == "" and board[new_row][new_col -
                                                                    1] == "":
                    temp_board = copy.deepcopy(board)
                    temp_board[new_row][new_col - 1] = current_piece
                    temp_board[old_row][old_col] = ""
                    if evaluate_check(temp_board, current_piece[:5]):
                        del temp_board
                        return
                    del temp_board
                    board[new_row][new_col] = current_piece
                    board[old_row][old_col] = ""
                    board[new_row][new_col - 1] = "Black_Rook"
                    board[new_row][new_col + 1] = ""
                    black_castlet = False
            elif new_col == 2 and new_row == 0 and game.black_castle[0]:
                if board[new_row][new_col] == "" and board[new_row][
                        new_col - 1] == "" and board[new_row][new_col +
                                                              1] == "":
                    temp_board = copy.deepcopy(board)
                    temp_board[new_row][new_col + 1] = current_piece
                    temp_board[old_row][old_col] = ""
                    if evaluate_check(temp_board, current_piece[:5]):
                        del temp_board
                        return
                    del temp_board
                    board[new_row][new_col] = current_piece
                    board[old_row][old_col] = ""
                    board[new_row][new_col + 1] = "Black_Rook"
                    board[new_row][new_col - 2] = ""
                    black_castlet = False
    if legal_move(current_piece,
                  old_row,
                  old_col,
                  new_row,
                  new_col,
                  board=board) == True:
        if len(game.last_move_possibilities) > 3:
            game.last_move_possibilities = []
        # game.last_move_possibilities.append(f"{game.col_conversion[old_col]}{8 - (old_row+1)+1}{game.col_conversion[new_col]}{8-(new_row+1)+1}")
        # print(f"old col {game.col_conversion[old_col]} old row {8 - (old_row+1) + 1} new col {game.col_conversion[new_col]} new row {8-(new_row+1) + 1}")
        print(game.last_move_possibilities)
        # game.last_move = game.last_move_possibilities[0]
        
        # print("last move: "+game.last_move)
        game.best_move_hist.append(stockfish.get_best_move())
        game.good_move_hist.append(stockfish.get_top_moves(4))
        if not white_castlet:
        
            game.white_castle[0] = False
            game.white_castle[1] = False
        if not black_castlet:
            game.black_castle[0] = False
            game.black_castle[1] = False
        # if piece was king, make that color's castles illegal 0 is kingside castling 1 is queenside castling
        if current_piece == "White_King":
            game.white_castle[0] = False
            game.white_castle[1] = False
    ### 380-382 covers black king castling.
        elif current_piece == "Black_King":
            game.black_castle[0] = False
            game.black_castle[1] = False
    ### the following eight lines make it so that after a rook moves you can no longer castle with it.  It does this by locating each rook and checking if they move, and then marking their respective castle option as false.
        elif current_piece == "White_Rook" and old_row == 7 and old_col == 7:
            game.white_castle[1] = False
        elif current_piece == "White_Rook" and old_row == 7 and old_col == 0:
            game.white_castle[0] = False
        elif current_piece == "Black_Rook" and old_row == 0 and old_col == 0:
            game.black_castle[1] = False
        elif current_piece == "Black_Rook" and old_row == 0 and old_col == 7:
            game.black_castle[0] = False
        #if current_piece[6:] == "Pawn":
            #game.half_move = -1

        # only re-write the piece normally if it is not pawn promotion
        board[new_row][new_col] = current_piece
        board[old_row][old_col] = ""


def promote_pawn(current_piece, new_row, new_col, color, board):
    """
  Asks the user in the console what piece they'd like to promote that pawn to.
  Remove the pawn and replace it with the selected piece on that square.
  """
    while True:

        print(f"{color} pawn on col {new_col} promoted")
        print("Queen, Rook, Bishop, or Knight?")
        choice = input("Input your choice: ")
        choice = choice.lower()
        if (choice != "queen" and choice != "rook" and choice != "bishop"
                and choice != "knight"):
            print("Mistake Made. Please retype.")
            continue
        else:
            break
    if color == "White":
        if choice == "queen":
            board[new_row][new_col] = "White_Queen"
        elif choice == "rook":
            board[new_row][new_col] = "White_Rook"
        elif choice == "bishop":
            board[new_row][new_col] = "White_Bishop"
        elif choice == "knight":
            board[new_row][new_col] = "White_Knight"
    if color == "Black":
        if choice == "queen":
            board[new_row][new_col] = "Black_Queen"
        elif choice == "rook":
            board[new_row][new_col] = "Black_Rook"
        elif choice == "bishop":
            board[new_row][new_col] = "Black_Bishop"
        elif choice == "knight":
            board[new_row][new_col] = "Black_Knight"

        # new_piece = input("Promote to Queen, Rook, Knight, or Bishop? ") # gives error from happening multiple times
    return board
pygame

def evaluate_check(board, color):
    """
    evaluate check defines a board that==changed by finding out when a king==checked by another piece

    board serves the same function as before, being a fluctuating plane that pieces check on
    color makes sure that opposing sides always check opposing kings and not their own

    returning as True tells the game that a king==in check and therefore restricts the player's quantity of moves next turn
    """

    r = 7
    c = 0
    if color == "White":
        found_flag = False
        while r >= 0:
            c = 0
            while c <= 7:
                if board[r][c] == "White_King":
                    found_flag = True
                    break

                c += 1
            if found_flag:
                break
            r -= 1
    else:
        r = 0
        c = 7
        found_flag = False
        while r <= 7:
            c = 7
            while c >= 0:
                if "Black_King" == board[r][c]:
                    found_flag = True
                    break

                c -= 1
            if found_flag:
                break
            r += 1

    if color == "White":
        if r > 0:
            if c > 0 and "Black_Pawn" == board[r - 1][c - 1]:
                return True
            if c < 7 and "Black_Pawn" == board[r - 1][c + 1]:
                return True
    else:
        if r < 7:
            if c > 0 and "White_Pawn" == board[r + 1][c - 1]:
                return True
            if c < 7 and "White_Pawn" == board[r + 1][c + 1]:
                return True

    row_change = [-1, -2, -2, -1, 1, 2, 2, 1]
    col_change = [-2, -1, 1, 2, 2, 1, -1, -2]
    for i in range(8):
        x = (r + row_change[i])
        y = (c + col_change[i])
        if -1 < x < 8 and -1 < y < 8 and board[x][y][:5] != color and board[x][
                y][6:] == "Knight":
            return True

    row_change = [-1, 0, 1, 0]
    col_change = [0, 1, 0, -1]
    for i in range(4):
        x = (r + row_change[i])
        y = (c + col_change[i])
        while -1 < x < 8 and -1 < y < 8:
            if board[x][y][:5] != color and (board[x][y][6:] == "Queen"
                                             or board[x][y][6:] == "Rook"):
                return True
            if board[x][y] != "":
                break
            x += row_change[i]
            y += col_change[i]

    row_change = [-1, 1, 1, -1]
    col_change = [1, 1, -1, -1]
    for i in range(4):
        x = r + row_change[i]
        y = c + col_change[i]
        while -1 < x < 8 and -1 < y < 8:
            if board[x][y][:5] != color and (board[x][y][6:] == "Queen"
                                             or board[x][y][6:] == "Bishop"):
                return True
            if board[x][y] != "":
                break
            x += row_change[i]
            y += col_change[i]


def is_valid(board, color):
    new_board = board


def availible_moves(current_piece, piece_row, piece_column, board):
    possible_moves = []
    if current_piece[6:] == "Bishop" or current_piece[6:] == "Queen":

        space_check = [piece_row - 1, piece_column - 1]
        #bishops and queens going northwest
        while space_check[0] >= 0 and space_check[1] >= 0:
            if board[space_check[0]][space_check[1]] == "":
                possible_moves.append([space_check[0], space_check[1]])
            elif board[space_check[0]][
                    space_check[1]][:5] == current_piece[:5]:
                break
            else:
                possible_moves.append([space_check[0], space_check[1]])
                break
            space_check[0] -= 1
            space_check[1] -= 1

        space_check = [piece_row - 1, piece_column + 1]
        #bishops and queens going northeast
        while space_check[0] >= 0 and space_check[1] <= 7:
            if board[space_check[0]][space_check[1]] == "":
                possible_moves.append([space_check[0], space_check[1]])
            elif board[space_check[0]][
                    space_check[1]][:5] == current_piece[:5]:
                break
            else:
                possible_moves.append([space_check[0], space_check[1]])
                break
            space_check[0] -= 1
            space_check[1] += 1

        space_check = [piece_row + 1, piece_column + 1]
        #bishops and queens going southeast
        while space_check[0] <= 7 and space_check[1] <= 7:
            if board[space_check[0]][space_check[1]] == "":
                possible_moves.append([space_check[0], space_check[1]])
            elif board[space_check[0]][
                    space_check[1]][:5] == current_piece[:5]:
                break
            else:
                possible_moves.append([space_check[0], space_check[1]])
                break
            space_check[0] += 1
            space_check[1] += 1

        space_check = [piece_row + 1, piece_column - 1]
        #bishops and queens going southwest
        while space_check[0] <= 7 and space_check[1] >= 0:
            if board[space_check[0]][space_check[1]] == "":
                possible_moves.append([space_check[0], space_check[1]])
            elif board[space_check[0]][
                    space_check[1]][:5] == current_piece[:5]:
                break
            else:
                possible_moves.append([space_check[0], space_check[1]])
                break
            space_check[0] += 1
            space_check[1] -= 1

    if current_piece[6:] == "Rook" or current_piece[6:] == "Queen":
        space_check = [piece_row, piece_column - 1]
        #rooks and queens going west
        while space_check[1] >= 0:
            if board[space_check[0]][space_check[1]] == "":
                possible_moves.append([space_check[0], space_check[1]])
            elif board[space_check[0]][
                    space_check[1]][:5] == current_piece[:5]:
                break
            else:
                possible_moves.append([space_check[0], space_check[1]])
                break
            space_check[1] -= 1

        space_check = [piece_row, piece_column + 1]
        #rooks and queens going east
        while space_check[1] <= 7:
            if board[space_check[0]][space_check[1]] == "":
                possible_moves.append([space_check[0], space_check[1]])
            elif board[space_check[0]][
                    space_check[1]][:5] == current_piece[:5]:
                break
            else:
                possible_moves.append([space_check[0], space_check[1]])
                break
            space_check[1] += 1

        space_check = [piece_row - 1, piece_column]
        #rooks and queens going north
        while space_check[0] >= 0:
            if board[space_check[0]][space_check[1]] == "":
                possible_moves.append([space_check[0], space_check[1]])
            elif board[space_check[0]][
                    space_check[1]][:5] == current_piece[:5]:
                break
            else:
                possible_moves.append([space_check[0], space_check[1]])
                break
            space_check[0] -= 1

        space_check = [piece_row + 1, piece_column]
        #rooks and queens going south
        while space_check[0] <= 7:
            if board[space_check[0]][space_check[1]] == "":
                possible_moves.append([space_check[0], space_check[1]])
            elif board[space_check[0]][
                    space_check[1]][:5] == current_piece[:5]:
                break
            else:
                possible_moves.append([space_check[0], space_check[1]])
                break
            space_check[0] += 1
    if current_piece[6:] == "Knight":
        space_check = [[piece_row - 2, piece_column - 1],
                       [piece_row - 2, piece_column + 1],
                       [piece_row - 1, piece_column + 2],
                       [piece_row + 1, piece_column + 2],
                       [piece_row + 2, piece_column + 1],
                       [piece_row + 2, piece_column - 1],
                       [piece_row + 1, piece_column - 2],
                       [piece_row - 1, piece_column - 2]]
        for move in space_check:
            if not (0 <= move[0] <= 7 and 0 <= move[1] <= 7):
                continue
            else:
                if board[move[0]][move[1]][:5] == current_piece[:5]:
                    continue
                else:
                    possible_moves.append([move[0], move[1]])
    if current_piece[6:] == "King":
        space_check = [[piece_row - 1, piece_column],
                       [piece_row - 1, piece_column + 1],
                       [piece_row, piece_column + 1],
                       [piece_row + 1, piece_column + 1],
                       [piece_row + 1, piece_column],
                       [piece_row, piece_column - 1],
                       [piece_row + 1, piece_column - 1],
                       [piece_row - 1, piece_column - 1]]
        for move in space_check:
            if not (0 <= move[0] <= 7 and 0 <= move[1] <= 7):
                continue
            else:
                if board[move[0]][move[1]][:5] == current_piece[:5]:
                    continue
                else:
                    possible_moves.append([move[0], move[1]])
    if current_piece[6:] == "Pawn":
        if current_piece[:5] == "White":
            if board[piece_row - 1][piece_column] == "":
                possible_moves.append([piece_row - 1, piece_column])
                if board[piece_row - 2][piece_column] == "":
                    possible_moves.append([piece_row - 2, piece_column])
            try:
                if board[piece_row - 1][piece_column - 1][:5] == "Black":
                    possible_moves.append([piece_row - 1, piece_column - 1])
            except:
                pass
            try:
                if board[piece_row - 1][piece_column + 1][:5] == "Black":
                    possible_moves.append([piece_row - 1, piece_column + 1])
            except:
                pass
        else:
            if board[piece_row + 1][piece_column] == "":
                possible_moves.append([piece_row + 1, piece_column])
                if board[piece_row + 2][piece_column] == "":
                    possible_moves.append([piece_row + 2, piece_column])
            try:
                if board[piece_row + 1][piece_column - 1][:5] == "White":
                    possible_moves.append([piece_row + 1, piece_column - 1])
            except:
                pass
            try:
                if board[piece_row + 1][piece_column + 1][:5] == "White":
                    possible_moves.append([piece_row + 1, piece_column + 1])
            except:
                pass
    return possible_moves


def checkmate(board, color):
    #checkmate defines the end of the game, by scanning each piece to see if they can move
    x = 0
    y = 0
    cm_piece = []
    while y < 8:
        while x < 8:
            if board[y][x][:5] == color:
                cm_piece.append([y, x])
                #append adds the possible pieces
            x += 1
        x = 0
        y += 1
        #y and x define the reach of the board
    for space in cm_piece:
        possible_moves = availible_moves(
            current_piece=board[space[0]][space[1]],
            piece_row=space[0],
            piece_column=space[1],
            board=board)
        #moves are defined by where the current piece can go
        for current_move in possible_moves:
            new_board = copy.deepcopy(board)
            # the copy copies a board so it scans each move from there
            move(current_piece=new_board[space[0]][space[1]],
                 old_row=space[0],
                 old_col=space[1],
                 new_row=current_move[0],
                 new_col=current_move[1],
                 board=new_board)
            #move==evaluated to see if we are still in check
            if not evaluate_check(board=new_board, color=color):
                return False
            del new_board
            #deleting the board saves memory and a new one==created anyway
    return True


def set_timer():
    user_text = ""
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_BACKSPACE:
                    user_text = user_text[:-1]
                    print(user_text)
                elif event.key == pygame.K_RETURN:
                    if user_text.isdigit():
                        return int(user_text)
                else:
                    if (event.unicode.isdigit()):
                        user_text += event.unicode
                        print(user_text)
            user_label = font.render(f"{user_text}", 1, (172, 34,34))
            timer_box = pygame.Rect((PIECE_SIZE * 8 + 200) / 2 - 75,
                                    ((PIECE_SIZE * 8) / 2) - 28, 150, 76)
            screen.fill(background_color)
            color = pygame.Color(51, 63, 255)
            pygame.draw.rect(screen, color, timer_box, 2)
            screen.blit(
                user_label,
                (((PIECE_SIZE * 8 + 200) - user_label.get_width()) / 2,
                 (((PIECE_SIZE * 8) / 2) - user_label.get_height() / 2)))
            instruction_label = font.render("Pick a control", 1, (178, 34, 34))
            screen.blit(
                instruction_label,
                (((PIECE_SIZE * 8 + 200) - instruction_label.get_width()) / 2,
                 (((PIECE_SIZE * 8) / 2) - user_label.get_height() / 2) -
                 instruction_label.get_height()))
            pygame.display.update()


#black_bishop = pygame.image.load("pieces/Black_Bishop.png")

minutes = set_timer()
game_over = False
selected = (-1, -1)
future_board = copy.deepcopy(game.board)
black_timer = Timer(minute=minutes, second=0, x=490, y=5)
white_timer = Timer(minute=minutes, second=0, x=490, y=440)
start_tick = pygame.time.get_ticks()

#start of game_loop
milliseconds = 0.0
last_turn = "white"
last_pawns = game.find_pawns()
game.best_move_hist += [stockfish.get_best_move(), stockfish.get_best_move()]
game.good_move_hist += [stockfish.get_top_moves(4), stockfish.get_top_moves(4)]
last_num_pieces = 32
while not game_over:
    if game.turn != last_turn:
        stockfish.set_fen_position(game.set_fen())
        game.half_move += 1
        last_turn = game.turn
    if game.count_pieces() != last_num_pieces:
        game.half_move = 0
        last_num_pieces = game.count_pieces()
    if game.find_pawns() != last_pawns:
        game.half_move = 0
        last_pawns = game.find_pawns()
    

    milliseconds = pygame.time.get_ticks() - start_tick
    if game.turn == 'Black' and milliseconds >= 1000:
        black_timer.countdown()
        start_tick = pygame.time.get_ticks()
    if game.turn == 'White' and milliseconds >= 1000:
        white_timer.countdown()
        start_tick = pygame.time.get_ticks()
    for event in pygame.event.get():
        if event.type == pygame.MOUSEBUTTONDOWN:
            if (future_board == game.board):
                print("boards are still the same")
            if pygame.mouse.get_pos()[0] < PIECE_SIZE * 8:
                pos = pygame.mouse.get_pos()
                row_clicked = int(pos[1] / PIECE_SIZE)
                col_clicked = int(pos[0] / PIECE_SIZE)
                if selected == (-1, -1):
                    if game.turn in game.board[row_clicked][col_clicked]:
                        selected = (row_clicked, col_clicked)
                        print(
                            f"You have selected Row: {row_clicked} Col: {col_clicked}"
                        )
                    break
                if game.turn in game.board[row_clicked][col_clicked]:
                    selected = (row_clicked, col_clicked)
                    print(
                        f"You have selected Row: {row_clicked} Col: {col_clicked}"
                    )
                    break
                else:
                    if legal_move(current_piece=future_board[selected[0]][
                            selected[1]],
                                  old_row=selected[0],
                                  old_col=selected[1],
                                  new_row=row_clicked,
                                  new_col=col_clicked,
                                  board=future_board
                                  ):  # possible list index out of range?
                        move(current_piece=future_board[selected[0]][
                            selected[1]],
                             old_row=selected[0],
                             old_col=selected[1],
                             new_row=row_clicked,
                             new_col=col_clicked,
                             board=future_board)
                        game.last_move = f"{game.col_conversion[selected[1]]}{8 - (selected[0]+1)+1}{game.col_conversion[col_clicked]}{8-(row_clicked+1)+1}"

                        if abs(row_clicked -
                               selected[0]) != 1 and future_board[selected[0]][
                                   selected[1]][:6] != "Pawn":
                            en_passantable = None

                        print(hex(id(future_board[selected[0]][selected[1]])))
                        print(hex(id(game.board[selected[0]][selected[1]])))
                        if evaluate_check(board=future_board, color=game.turn):

                            print(f"You are in Check {game.turn}")

                            future_board = copy.deepcopy(game.board)
                            selected = (-1, -1)
                            break
                        else:
                            print(f"Good to Go {game.turn}")
                            move(current_piece=game.board[selected[0]][
                                selected[1]],
                                 old_row=selected[0],
                                 old_col=selected[1],
                                 new_row=row_clicked,
                                 new_col=col_clicked,
                                 board=game.board)
                            if game.board[row_clicked][
                                    col_clicked] == "White_Pawn" and row_clicked == 0:  # if white pawn reaches the end
                                game.board = promote_pawn(
                                    game.board[row_clicked][col_clicked],
                                    row_clicked, col_clicked,
                                    game.board[row_clicked][col_clicked][:5],
                                    game.board)

                            elif game.board[row_clicked][
                                    col_clicked] == "Black_Pawn" and row_clicked == 7:  # if white pawn reaches the end
                                game.board = promote_pawn(
                                    game.board[row_clicked][col_clicked],
                                    row_clicked, col_clicked,
                                    game.board[row_clicked][col_clicked][:5],
                                    game.boarstart_tickd)
                            if game.turn == 'White':
                                game.turn = "Black"
                                start_tick = pygame.time.get_ticks()

                            elif game.turn == "Black":
                                game.turn = 'White'
                                start_tick = pygame.time.get_ticks()
                            if checkmate(board=game.board, color=game.turn):

                                game_over = True
                            selected = (-1, -1)
                            break
                    else:
                        print(
                            f"move was not legal cant move to row {row_clicked} col {col_clicked}"
                        )
                # if game.turn not in game.board[row_clicked][col_clicked]:
                   
                #   pass

                #   # if legal_move(-1,-1) ==
                # if game.board[row_clicked][col_clicked] != "":
                #   if game.turn in game.board[row_clicked][col_clicked]:
                #       selected = (row_clicked,col_clicked)

        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    screen.fill(background_color)
    draw_board(game.board)
    black_timer.draw(screen)
    white_timer.draw(screen)
    #eval timer
    
    pygame.draw.rect(screen, (0, 0, 0), pygame.Rect(500, 95, 20, 350))
    game.curr_time = time.time()
    if game.curr_time - game.last_time_recorded > 2.5 or game.turn != last_turn:
        game.last_time_recorded = game.curr_time
        game.evalw = game.get_evalw()
        game.eval = stockfish.get_evaluation()
    
    pygame.draw.rect(screen, (255, 255, 255), pygame.Rect(500, 95, 20, 350 * game.evalw/100))
    # eval = stockfish.get_evaluation()
    # if self.last_move is in the second to last item of self.best_move_hist then blit best_img
    # print("last move: " + game.last_move)
    # os.system('cls')
    # print("best move:", end=" ")
    # print(str(game.best_move_hist[-1])) # used to be -2 not -1
    # print("good moves:")
    # for good_move in game.good_move_hist[-1]:
    #     print (str(good_move))
    # if a move is the best move
    if game.last_move == game.best_move_hist[-1]:
        screen.blit(game.best_img, (550, 250), )
    # else if a move is in the top 4 best moves
    elif game.last_move in [x["Move"] for x in game.good_move_hist[-1] if x["Centipawn"] > 0]:
        screen.blit(game.good_img, (550, 250, ),)
    if game.eval["type"] != "cp":
        moves_til_mate = abs(game.eval['value'])
        mate_text = font.render(f"M{moves_til_mate}", 1, (255, 255, 255))
        screen.blit(mate_text, (530, 240))
    else:
        font = pygame.font.SysFont("comicsans", 32, bold=True)
        evaluationb = font.render(f"{100-game.evalw}", 1, (0, 0, 0))
        evaluationw = font.render(f"{game.evalw}", 1, (255, 255, 255))
        screen.blit(evaluationw, (530, 80))
        screen.blit(evaluationb, (530, 400))

    #screen.blit(black_bishop, (0, 0))
    pygame.display.update()

print(f"Game==over. {game.turn} lost")
"""
if selected -1,-1: piece unselected
then change coords to selected piece

if selected==a piece: piece 

"""
