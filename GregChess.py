
#GregChess!
#Author Greg Hamel
#Simple python chess game

""" Version 1.12
Game currently supports basic chess games bewteen two human players. Current version
supports basic castling. Does not check for check or checkmate, so it is possible to move into check and castle through check.
You must actually capture the king to win.

v1.12 updates- Game now supports castling. You cannot castle with a king/rook that has previously been moved, but you can castle through check.
"""

rules = """
Make moves by typing in the piece you want to move and its coordinates followed
by a space and the coordinats of the square that you want to move to.
For example, as the White(capital letters) player, if you have a pawn at a2 and
you want to move it up to a3, you would type "Pa2 a3."
"""

import copy

#Create an 8x8 2D array with space representing white squares and X's representing black squares.
base_board_row = [" " if space%2==0 else "X" for space in range(8)]
base_board = [copy.deepcopy(base_board_row) if row%2 == 0 else copy.deepcopy(base_board_row)[::-1] for row in range(8)]

#Dictionaries mapping chess row/column letters/numbers to array index values
column_indexes = {k:v for k,v in zip("abcdefgh",range(8))}
row_indexes = {k:v for k,v in zip("87654321",range(8))}


#Creates a list of pieces at starting board positions.
#Ra1 -> white rook at a1.  pb7 -> black pawn at b7   King=G
starting_piece_positions = [''.join(p) for p in list(zip("rkbqgbkr","abcdefgh","8"*8))+list(zip("p"*8,"abcdefgh","7"*8))\
                          +list(zip("P"*8,"abcdefgh","2"*8))+list(zip("RKBQGBKR","abcdefgh","1"*8))]

#Create variables for tracking piece positions and the board as the game progresses
current_piece_positions = copy.deepcopy(starting_piece_positions)
current_board = copy.deepcopy(base_board)
captured_pieces = {"White(capitals)": [], "Black(lowercase)": []}  #Tracks captured pieces
move_list = []             #Tracks all moves made during the game.

#Takes a piece/position and returns its index values in the board array
# Ra1 -> (7,0) : White rook is in row[7], column[0]
def piece_coords(piece):
    return (row_indexes[piece[2]],column_indexes[piece[1]])

#Takes a position on the board and returns the piece at that position, " " or "X" if empty
def piece_at(position):
    position_coords = row_indexes[position[1]],column_indexes[position[0]]
    return current_board[position_coords[0]][position_coords[1]]


#Takes a lits of piece positions and redraws the board given those positions
def update_board(piece_positions):
    new_board = copy.deepcopy(base_board)
    for piece in piece_positions:
        x, y = piece_coords(piece)
        new_board[x][y] = piece
    return new_board

#Takes a board and prints a representation for the player with a-h,1-8 chess coords
def display_board(board):
    top = "  | a | b | c | d | e | f | g | h |"
    divider = "  |___|___|___|___|___|___|___|___|"
    print(top)
    print(divider)
    for row in enumerate(board):
        num = str(8-row[0])
        for space in row[1]:
            num+=" | "+space[0]
        num+=" |"
        print (num)
        print(divider)

#Takes a piece and a destination space and updates current piece positions with the new positon.
#If the desination space already contains a piece, that piece is removed and added to the captured pieces dictionary.
#Piece format = Ra1 (white rook at a1) Desination format = a5 (space a5)
def move_piece(piece, destination):
    if not valid_move(piece, destination):
        print ("Invalid Move")
        return False
    for p in current_piece_positions:
        if p[1:] == destination:
            if p[0] in "RKBQGP":
                if piece[0] in "RKBQGP":  #Invalid move, can't capture your own piece
                    print("Invalid move, can't capture your own piece!")
                    return False
                else:
                    captured_pieces["White(capitals)"]+=[p]
            else:
                if piece[0] in "rkbqgp":
                    print("Invalid move, can't capture your own piece!")
                    return False
                else:
                    captured_pieces["Black(lowercase)"]+=[p]
            current_piece_positions.remove(p)

    current_piece_positions.remove(piece)
    new_piece_position = piece[0]+destination

    #Handle Pawn Promotion
    if piece[0] in "Pp":
        if destination[1] in "18":
            new_piece = "XXX"
            while new_piece not in "rkbqpRKBQP":
                new_piece = input("Promote your pawn. Enter the letter of the piece type you wish to use.")
                if new_piece not in "rkbqpRKBQP":
                    print("Invalid piece type. Please select again.")
            if piece[0] == "P":
                new_piece = new_piece.upper()
            else:
                new_piece = new_piece.lower()
            new_piece_position = new_piece+destination

    move_list.append((piece, destination))
    current_piece_positions.append(new_piece_position)
    return True


#Checks if given move is valid. The move piece function already ensures that a piece cannot capture a friendly piece.
def valid_move(piece, destination):
    coords = piece_coords(piece)

    if destination[1] not in row_indexes or destination[0] not in column_indexes:
        print("Destination space does not exist!")
        return False

    destination_coords = row_indexes[destination[1]],column_indexes[destination[0]]

    if coords == destination_coords:
        print("Piece cannot move to its own space!")
        return False

    if piece not in current_board[coords[0]]:
        print("That piece does not exist at the specified coordinates!")
        return False

    #Check Rook
    if piece[0]in "Rr":
        return check_rook(piece, destination,coords,destination_coords)

    #Check Knight
    if piece[0]in "Kk":
        move_possibilities = []
        for pos in [(-2,-1),(-2,1),(-1,-2),(-1,2)]:
            move_possibilities.append((coords[0]+pos[0],coords[1]+pos[1]))
            move_possibilities.append((coords[0]-pos[0],coords[1]+pos[1]))
        if destination_coords not in move_possibilities:
            return False
        return True

    #Check Pawn
    if piece[0]== "P":   #Checks for white pawns
        #If pawn has not moved, check if the player is trying to move it two spaces.
        if coords[0] == 6:
            if destination_coords[0] == coords[0]-2:
                if piece_at(destination) not in " X" or current_board[coords[0]-1][coords[1]] not in " X" or destination_coords[1] != coords[1]:
                    return False
                return True
        #Checks pawn moves other than moving two spaces
        if destination_coords[0] != coords[0]-1: #If pawn does not move into the next row, return false
            return False
        #Pawn cannot move anywhere other than the 3 spaces in front of it.
        if abs(destination_coords[1]-coords[1]) > 1:
            return False
        if destination_coords[1] == coords[1]:  #If pawn is moving straight, it cannot capture
            if piece_at(destination) not in " X":
                return False
        if abs(destination_coords[1]-coords[1]) == 1: #If pawn is moving digonally, that space must contain a piece to capture...
            if piece_at(destination) not in " X":
                return True
            #unless capturing en passent. In this case, check the last move in the movelist for a black pawn that moved 2 spaces forward and ended next to the white pawn.
            if piece[2] == "5":                                                                                   #In the same column the pawn is attempting to move into
                if move_list[-1][0][0] == "p" and move_list[-1][0][2] == "7" and move_list[-1][1][1] == "5" and piece_coords(move_list[-1][0])[1] == destination_coords[1]:
                    captured_pieces["Black(lowercase)"]+=move_list[-1][0]
                    current_piece_positions.remove(move_list[-1][0][0]+move_list[-1][1])
                    return True
            return False
        return True

    if piece[0]== "p": #Checks for black pawns
        if coords[0] == 1:
            if destination_coords[0] == coords[0]+2:
                if piece_at(destination) not in " X" or current_board[coords[0]+1][coords[1]] not in " X" or destination_coords[1] != coords[1]:
                    return False
                return True
        #Checks pawn moves other than moving two spaces
        if destination_coords[0] != coords[0]+1: #If pawn does not move into the next row, return false
            return False
        #Pawn cannot move aywhere other than the 3 spaces in front of it.
        if abs(destination_coords[1]-coords[1]) > 1:
            return False
        if destination_coords[1] == coords[1]:  #If pawn is moving straight, it cannot capture
            if piece_at(destination) not in " X":
                return False
        if abs(destination_coords[1]-coords[1]) == 1: #If pawn is moving digonally, it must capture
            if piece_at(destination) not in " X":
                return True
            #unless capturing en passent. In this case, check the last move in the movelist for a black pawn that moved 2 spaces forward and ended next to the white pawn.
            if piece[2] == "4":
                if move_list[-1][0][0] == "P" and move_list[-1][0][2] == "2" and move_list[-1][1][1] == "4" and piece_coords(move_list[-1][0])[1] == destination_coords[1]:
                    captured_pieces["White(capitals)"]+=move_list[-1][0]
                    current_piece_positions.remove(move_list[-1][0][0]+move_list[-1][1])
                    return True
            return False
        return True

    #Check King
    if piece[0]in "Gg":
        if abs(destination_coords[0]-coords[0]) <=1 and abs(destination_coords[1]-coords[1]) <=1:
            return True
        if abs(destination_coords[1]-coords[1]) == 2:   #Castling attempt
            for p, dest in move_list:    #If the king has already moved, it can't castle
                if p[0] == piece[0]:
                    return False
            if (destination_coords[1]-coords[1]) == 2:   #Determine which rook to move...
                if piece[0] == "G":
                    rook = "Rh1"
                    rook_dest = "f1"
                else:
                    rook = "rh8"
                    rook_dest = "e8"
            else:
                if piece[0] == "G":
                    rook = "Ra1"
                    rook_dest = "d1"
                else:
                    rook = "ra8"
                    rook_dest = "c8"
            for p, dest in move_list:  #And check if it has already been moved
                if p == rook:
                    return False
            if not valid_move(rook, piece[1:]): #Rook needs a clear path to the king's current position
                return False
            move_piece(rook, rook_dest) #Move the rook to correct space
            return True
        return False

    #Check Bisop
    if piece[0] in "Bb":
        return check_bishop(piece, destination,coords,destination_coords)

    #Check Queen
    if piece[0] in "Qq":
        return check_rook(piece, destination,coords,destination_coords) or check_bishop(piece, destination,coords,destination_coords)

#Helper function for checking bishop moves
def check_bishop(piece, destination,coords,destination_coords):
    if destination_coords[0] != coords[0] and destination_coords[1] != coords[1]: #Bishop can't end in the same row or column after moving
        if coords[0]-destination_coords[0] <0:                             #number of rows moved
            spaces_moved = abs(coords[0]-destination_coords[0])
        else:
            spaces_moved = abs(destination_coords[0]-coords[0])            #number of rows moved
        if coords[1]-destination_coords[1] <0:
            c_moved = abs(coords[1]-destination_coords[1])                 #number of columns moved
        else:
            c_moved = abs(destination_coords[1]-coords[1])          #number of columns moved
        if spaces_moved != c_moved:                   #The number of columns moved must match the number of rows moved for diagonal movement
            return False

        if destination_coords[0]-coords[0] <0 and destination_coords[1] - coords[1] <0: #Moving up and to the left
            for x in range(1,spaces_moved):
                if current_board[coords[0]-x][coords[1]-x] not in " X":
                    return False
            return True
        if destination_coords[0]-coords[0] <0 and destination_coords[1] - coords[1] >0: #Moving up and to the right
            for x in range(1,spaces_moved):
                if current_board[coords[0]-x][coords[1]+x] not in " X":
                    return False
            return True
        if destination_coords[0]-coords[0] >0 and destination_coords[1] - coords[1] <0: #Moving down and to the left
            for x in range(1,spaces_moved):
                if current_board[coords[0]+x][coords[1]-x] not in " X":
                    return False
            return True
        if destination_coords[0]-coords[0] >0 and destination_coords[1] - coords[1] >0: #Moving down and to the right
            for x in range(1,spaces_moved):
                if current_board[coords[0]+x][coords[1]+x] not in " X":
                    return False
            return True
    return False

#Helper function for checking rook moves
def check_rook(piece, destination,coords,destination_coords):
    if coords[0] != destination_coords[0] and coords[1] != destination_coords[1]:
        return False
    if coords[0] != destination_coords[0]:  #Piece is moving in column
        if coords[0] > destination_coords[0]:  #Piece is moving up
            for space in range(destination_coords[0]+1,coords[0]):
                if current_board[space][coords[1]] not in " X":
                    return False
            return True
        else:                                  #Piece is moving down
            for space in range(coords[0]+1,destination_coords[0]):
                if current_board[space][coords[1]] not in " X":
                    return False
            return True

    else:                                      #Piece is moving in row
        if coords[1] > destination_coords[1]:  #Piece is moving left
            for space in range(destination_coords[1]+1,coords[1]):
                if current_board[coords[0]][space] not in " X":
                    return False
            return True
        else:                                  #Piece is moving right
            for space in range(coords[1]+1,destination_coords[1]):
                if current_board[coords[0]][space] not in " X":
                    return False
            return True


#Main game loop
def greg_chess():
    print (rules)
    player = "White"
    while True:
        #Need to manipulate the global current_board
        global current_board
        current_board = update_board(current_piece_positions)
        print ("It's the %(player)s player's Turn"%{'player':player})
        display_board(current_board)

        #Get input from the user in the form "piece destination" --> "Pa2 a4"
        #Selects pawn at a2 and moves it to a4.
        next_move = input("%(player)s player, enter your next move"%{'player':player})

        #Player can type q or quit to end the game
        if next_move in "QUITquit":
            print("Thanks for playing")
            break

        #Player can check the log of moves made.
        if next_move == "moves":
            print(move_list)
            continue

        #Player can type "captured" to check the list of captured pieces
        if next_move == "captured":
            print(captured_pieces)
            continue

        #Moves the specified piece to the specified destination if the move is valid.
        #Otherwise, the player is asked for a new move.
        next_move = next_move.split()
        if player == "White" and next_move[0][0] not in "PRKBQG":
            print("Invalid piece for White player!")
            continue
        if player == "Black" and next_move[0][0] not in "prkbqg":
            print("Invalid piece for Black player!")
            continue
        if move_piece(next_move[0], next_move[1]):
            if player == "White":
                player = "Black"
            else:
                player = "White"

        #Check to see if King has been captured. If so, the game ends.
        game_over = False
        for p in captured_pieces['White(capitals)']:
            if p[0]== "G":
                print ("Black wins")
                game_over = True
                break
        for p in captured_pieces['Black(lowercase)']:
            if p[0]== "g":
                print ("White wins")
                game_over = True
                break
        if game_over == True:
            print("Thanks for playing!")
            break


if __name__ == "__main__":
    greg_chess()







