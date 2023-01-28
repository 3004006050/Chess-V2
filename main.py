import pygame
import sys
import copy
import datetime
import time
#piece and screen defining
pygame.init()
PIECE_SIZE = 60
SCREEN_SIZE = [PIECE_SIZE * 8 + 200, PIECE_SIZE * 8]
screen = pygame.display.set_mode(SCREEN_SIZE)
pygame.display.set_caption('Chess')
font = pygame.font.SysFont("comicsans", 64, bold = True)
background_color = "0x8b0000"
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
    timer_label = font.render(f"{self.minute}:{self.second}",1,"0xB22222")
    screen.blit(timer_label, (self.x, self.y))
    
    
class Game:
    #Game defines all pieces's strings and board, along with turning
    def __init__(self):
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
        self.turn = 'White'  # white/black
        self.piece_location = {
            'White_Rook', 'White_Knight', 'White_Bishop', 'White_King',
            'White_Queen'
        }


# making game object
game = Game()
black_castle = [True, True]
white_castle = [True, True]

#images loading
images = {}
for color in ['Black', 'White']:
    for piece in ['King', 'Queen', 'Knight', 'Bishop', 'Rook', 'Pawn']:
        name = color + '_' + piece
        images[name] = pygame.image.load('pieces/' + name + '.png')


def get_square_color(row, col):
    """"
    makes board alternate white and grey
  
    :param row: row specifies the row of a given square
  
    :param col: col specifies the column of a given square
  
    :return: returns the color of a given square
    """

    if row % 2 == 0:
        if col % 2 == 0:
            return 'white'
        else:
            return 'gray'
    else:
        if col % 2 == 0:
            return 'gray'
        else:
            return 'white'


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

      checkmate_label = font.render(str(checkmate_string), True, "0xB22222")

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

        if current_piece[:6] == board[new_row][new_col][:6] or "King" == board[new_row][new_col][6:]:
            return False

        return True
    elif current_piece == "Black_Bishop" or current_piece == "White_Bishop":
        if row_change == col_change:
          start_row = old_row 
          start_col = old_col 
          
          while start_row != new_row and start_col != new_col:
            if board [start_row][start_col] != "" and start_row != old_row and start_col != old_col:
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
            if board [start_row][start_col] != "" and start_row != old_row and start_col != old_col:
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
          if new_col == 6 and new_row == 7 and white_castle[1]:
            if board[new_row][new_col] == "" and board[new_row][new_col - 1]  == "":
              temp_board = copy.deepcopy(board)
              temp_board[new_row][new_col - 1] = current_piece
              temp_board[old_row][old_col] = ""
              if evaluate_check(temp_board, current_piece[:5]):
                del temp_board
                return
              del temp_board
              return True
          elif new_col == 2 and new_row == 7 and white_castle[0]:
            if board[new_row][new_col] == "" and board[new_row][new_col - 1] == "" and board[new_row][new_col + 1]  == "":
                temp_board = copy.deepcopy(board)
                temp_board[new_row][new_col + 1] = current_piece
                temp_board[old_row][old_col] = ""
                if evaluate_check(temp_board, current_piece[:5]):
                  del temp_board
                  return
                del temp_board
                return True
        if old_row == 0 and old_col == 4 and current_piece[:5] == "Black":
          if new_col == 6 and new_row == 0 and black_castle[1]:
            if board[new_row][new_col] == "" and board[new_row][new_col - 1]  == "":
              temp_board = copy.deepcopy(board)
              temp_board[new_row][new_col - 1] = current_piece
              temp_board[old_row][old_col] = ""
              if evaluate_check(temp_board, current_piece[:5]):
                del temp_board
                return
              del temp_board
              return True
          elif new_col == 2 and new_row == 0 and black_castle[0]:
            if board[new_row][new_col] == "" and board[new_row][new_col - 1] == "" and board[new_row][new_col + 1]  == "":
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
            if board[new_row + 1][new_col] == board[old_row][old_col]:
                return True
            elif board[new_row][new_col] != "" and new_col != 7 and new_col != 0 and (board[new_row + 1][new_col + 1] == board[old_row][old_col] or board[new_row + 1][new_col - 1 ] == board[old_row][old_col]):
              
                return True
            elif board[new_row][new_col] != "" and new_col == 7 and board[new_row + 1][new_col - 1 ] == board[old_row][old_col]:
              return True
            elif board[new_row][new_col] != "" and new_col == 0 and board[new_row + 1][new_col + 1] == board[old_row][old_col]:
              return True
            # finished adding
            elif board[old_row][old_col] == board[6][
                    old_col] and board[new_row][
                        new_col] == "" and board[new_row + 1][
                            new_col] == "" and row_change == 2 and col_change == 0:
                return True
        else:  # Black Pawn
            if board[new_row -
                          1][new_col] == board[old_row][old_col]:
                return True
            elif board[new_row][new_col] != "" and (
                    board[new_row - 1][new_col - 1]
                    == board[old_row][old_col]
                    or board[new_row - 1][new_col + 1]
                    == board[old_row][old_col]):
                return True
            elif board[old_row][old_col] == board[1][
                    old_col] and board[new_row][
                        new_col] == "" and board[new_row - 1][
                            new_col] == "" and row_change == 2 and col_change == 0:
                return True
        return False
        # if row_change == 1 and col_change == 0 and board[new_col][
        #         new_row] == "":
        #     return True
        # elif row_change == 1 and col_change == 1 and board[new_col][
        #         new_row] != "":
        #     return True
        # elif row_change == 2 and col_change == 0:
        #     if current_piece[:6] == 'White':
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
    if current_piece[6:] == "King":
      if old_row == 7 and old_col == 4 and current_piece[:5] == "White":
        if new_col == 6 and new_row == 7 and white_castle[1]:
          if board[new_row][new_col] == "" and board[new_row][new_col - 1]  == "":
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
        elif new_col == 2 and new_row == 7 and white_castle[0]:
          if board[new_row][new_col] == "" and board[new_row][new_col - 1] == "" and board[new_row][new_col + 1]  == "":
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
      if old_row == 0 and old_col == 4 and current_piece[:5] == "Black":
        if new_col == 6 and new_row == 0 and black_castle[1]:
          if board[new_row][new_col] == "" and board[new_row][new_col - 1]  == "":
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
        elif new_col == 2 and new_row == 0 and black_castle[0]:
          if board[new_row][new_col] == "" and board[new_row][new_col - 1] == "" and board[new_row][new_col + 1]  == "":
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
    if legal_move(current_piece, old_row, old_col, new_row, new_col, board = board)==True:
        # if piece was king, make that color's castles illegal 0 is kingside castling 1 is queenside castling
        if current_piece == "White_King":
          white_castle[0] = False
          white_castle[1] = False
      ### 380-382 covers black king castling.
        elif current_piece == "Black_King":
          black_castle[0] = False
          black_castle[1] = False
      ### the following eight lines make it so that after a rook moves you can no longer castle with it.  It does this by locating each rook and checking if they move, and then marking their respective castle option as false.
        elif current_piece == "White_Rook" and old_row == 7 and old_col == 7:
          white_castle[1] = False
        elif current_piece == "White_Rook" and old_row == 7 and old_col == 0:
          white_castle[0] = False
        elif current_piece == "Black_Rook" and old_row == 0 and old_col == 0:
          black_castle[1] = False
        elif current_piece == "Black_Rook" and old_row == 0 and old_col == 7:
          black_castle[0] = False
        #elif?
        
        
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
    if (choice != "queen" and choice != "rook" and choice != "bishop" and choice != "knight"):
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
            if board[x][y][:5] != color and (board[x][y][6:] == "Queen" or board[x][y][6:] == "Rook"):
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
            if board[x][y][:5] != color and (board[x][y][6:] == "Queen" or board[x][y][6:] == "Bishop"):
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
      if board[space_check[0]][space_check[1]]=="":
        possible_moves.append([space_check[0], space_check[1]])
      elif board[space_check[0]][space_check[1]][:5]== current_piece[:5]:
        break
      else:
        possible_moves.append([space_check[0], space_check[1]])
        break
      space_check[0] -= 1
      space_check[1] -= 1

      
    space_check = [piece_row - 1, piece_column + 1]
    #bishops and queens going northeast
    while space_check[0] >= 0 and space_check[1] <= 7:
      if board[space_check[0]][space_check[1]]=="":
        possible_moves.append([space_check[0], space_check[1]])
      elif board[space_check[0]][space_check[1]][:5]== current_piece[:5]:
        break
      else:
        possible_moves.append([space_check[0], space_check[1]])
        break
      space_check[0] -= 1
      space_check[1] += 1

      
    space_check = [piece_row + 1, piece_column + 1]
    #bishops and queens going southeast
    while space_check[0] <= 7 and space_check[1] <= 7:
      if board[space_check[0]][space_check[1]]=="":
        possible_moves.append([space_check[0], space_check[1]])
      elif board[space_check[0]][space_check[1]][:5]== current_piece[:5]:
        break
      else:
        possible_moves.append([space_check[0], space_check[1]])
        break
      space_check[0] += 1
      space_check[1] += 1

      
    space_check = [piece_row + 1, piece_column - 1]
    #bishops and queens going southwest
    while space_check[0] <= 7 and space_check[1] >= 0:
      if board[space_check[0]][space_check[1]]=="":
        possible_moves.append([space_check[0], space_check[1]])
      elif board[space_check[0]][space_check[1]][:5]== current_piece[:5]:
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
      if board[space_check[0]][space_check[1]]=="":
        possible_moves.append([space_check[0], space_check[1]])
      elif board[space_check[0]][space_check[1]][:5]== current_piece[:5]:
        break
      else:
        possible_moves.append([space_check[0], space_check[1]])
        break
      space_check[1] -= 1

      
    space_check = [piece_row, piece_column + 1]
    #rooks and queens going east
    while space_check[1] <= 7:
      if board[space_check[0]][space_check[1]]=="":
        possible_moves.append([space_check[0], space_check[1]])
      elif board[space_check[0]][space_check[1]][:5]== current_piece[:5]:
        break
      else:
        possible_moves.append([space_check[0], space_check[1]])
        break
      space_check[1] += 1 

      
    space_check = [piece_row - 1, piece_column]
    #rooks and queens going north
    while space_check[0] >= 0:
      if board[space_check[0]][space_check[1]]=="":
        possible_moves.append([space_check[0], space_check[1]])
      elif board[space_check[0]][space_check[1]][:5]== current_piece[:5]:
        break
      else:
        possible_moves.append([space_check[0], space_check[1]])
        break
      space_check[0] -= 1

      
    space_check = [piece_row + 1, piece_column]
    #rooks and queens going south
    while space_check[0] <= 7:
      if board[space_check[0]][space_check[1]]=="":
        possible_moves.append([space_check[0], space_check[1]])
      elif board[space_check[0]][space_check[1]][:5]== current_piece[:5]:
        break
      else:
        possible_moves.append([space_check[0], space_check[1]])
        break
      space_check[0] += 1
  if current_piece[6:] == "Knight":
    space_check = [[piece_row - 2, piece_column - 1], [piece_row - 2, piece_column + 1], [piece_row -  1, piece_column + 2], [piece_row + 1, piece_column + 2], [piece_row + 2, piece_column + 1], [piece_row + 2, piece_column - 1], [piece_row + 1, piece_column - 2], [piece_row - 1, piece_column - 2]]
    for move in space_check:
      if not (0 <= move[0] <= 7 and 0 <= move[1] <= 7):
        continue
      else:
        if board[move[0]][move[1]][:5] == current_piece[:5]:
          continue
        else:
          possible_moves.append([move[0], move[1]])
  if current_piece[6:] == "King":
    space_check = [[piece_row - 1, piece_column], [piece_row - 1, piece_column + 1], [piece_row, piece_column + 1], [piece_row + 1, piece_column + 1], [piece_row + 1, piece_column], [piece_row, piece_column - 1], [piece_row + 1, piece_column - 1], [piece_row - 1, piece_column - 1]]
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
        if board[piece_row + 1][piece_column - 1][:5]=="White":
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
    possible_moves = availible_moves(current_piece = board[space[0]][space[1]], piece_row = space[0], piece_column = space[1], board = board)
    #moves are defined by where the current piece can go
    for current_move in possible_moves:
      new_board = copy.deepcopy(board)
      # the copy copies a board so it scans each move from there
      move(current_piece = new_board[space[0]][space[1]], old_row = space[0], old_col = space[1], new_row = current_move[0], new_col = current_move[1], board = new_board)
      #move==evaluated to see if we are still in check
      if not evaluate_check(board = new_board, color = color):
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
      user_label = font.render(f"{user_text}",1,"0xB22222")
      timer_box = pygame.Rect((PIECE_SIZE * 8 + 200)/2-75, ((PIECE_SIZE * 8)/2)-28, 150, 76)
      screen.fill(background_color)
      color = pygame.Color("#333FFF")
      pygame.draw.rect(screen, color, timer_box, 2)
      screen.blit(user_label, (((PIECE_SIZE * 8 + 200)-user_label.get_width())/2, (((PIECE_SIZE * 8)/2)-user_label.get_height()/2)))
      instruction_label = font.render("Pick a control", 1, "0xB22222")
      screen.blit(instruction_label, (((PIECE_SIZE * 8 + 200)-instruction_label.get_width())/2, (((PIECE_SIZE * 8)/2)-user_label.get_height()/2)-instruction_label.get_height()))
      pygame.display.update()

black_bishop = pygame.image.load("pieces/Black_Bishop.png")

minutes = set_timer()
game_over = False
selected = (-1, -1)
future_board = copy.deepcopy(game.board)
black_timer = Timer(minute = minutes, second = 0, x = 490, y = 5)
white_timer = Timer(minute = minutes, second = 0, x = 490, y = 440)
start_tick = pygame.time.get_ticks()



#start of game_loop
milliseconds = 0.0
while not game_over:
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
                    if legal_move(current_piece=future_board[selected[0]][     selected[1]], old_row=selected[0], old_col=selected[1], new_row=row_clicked, new_col=col_clicked, board = future_board):
                        move(current_piece=future_board[selected[0]][selected[1]], old_row=selected[0], old_col=selected[1], new_row=row_clicked, new_col=col_clicked, board=future_board)
                      
                        print(hex(id(future_board[selected[0]][selected[1]])))
                        print(hex(id(game.board[selected[0]][selected[1]])))
                        if evaluate_check(board=future_board, color=game.turn):
                          
                            print(f"You are in Check {game.turn}")

                            future_board = copy.deepcopy(game.board)
                            selected = (-1, -1)
                            break
                        else:
                            print(f"Good to Go {game.turn}")
                            move(current_piece=game.board[selected[0]][selected[1]], old_row=selected[0], old_col=selected[1], new_row=row_clicked, new_col=col_clicked, board=game.board)
                            if game.board[row_clicked][col_clicked] == "White_Pawn" and row_clicked == 0: # if white pawn reaches the end
                              game.board = promote_pawn(game.board[row_clicked][col_clicked], row_clicked, col_clicked, game.board[row_clicked][col_clicked][:5], game.board)
          
                            elif game.board[row_clicked][col_clicked] == "Black_Pawn" and row_clicked == 7: # if white pawn reaches the end
                              game.board = promote_pawn(game.board[row_clicked][col_clicked], row_clicked, col_clicked, game.board[row_clicked][col_clicked][:5], game.board)
                            if game.turn == 'White':
                                game.turn = "Black"
                                start_tick = pygame.time.get_ticks()


                            elif game.turn == "Black":
                                game.turn = 'White'
                                start_tick = pygame.time.get_ticks()
                            if checkmate(board = game.board, color = game.turn):
                              
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
    #screen.blit(black_bishop, (0, 0))
    pygame.display.update()


print(f"Game==over. {game.turn} lost")

"""
if selected -1,-1: piece unselected
then change coords to selected piece

if selected==a piece: piece 

"""
