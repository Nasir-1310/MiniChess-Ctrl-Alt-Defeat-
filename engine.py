class GameState():

    def __init__(self) -> None:
        self.board = [
            ['b_R', 'b_N', 'b_B', 'b_Q', 'b_K'],
            ['b_P', 'b_P', 'b_P', 'b_P', 'b_P'],
            ['--', '--', '--', '--', '--'],
            ['--', '--', '--', '--', '--'],
            ['w_P', 'w_P', 'w_P', 'w_P', 'w_P'],
            ['w_K', 'w_Q', 'w_B', 'w_N', 'w_R'],
        ]

        self.moveFunctions = {'P': self.getPawnMoves, 'R': self.getRookMoves,
                              'N': self.getKnightMoves, 'B': self.getBishopMoves,
                              'Q': self.getQueenMoves, 'K': self.getKingMoves}

        self.whiteToMove = True
        self.moveLog = []

        # king location
        self.whiteKingLocation = (5, 4)
        self.blackKingLocation = (0, 4)

        # checkmate and stalemate
        self.checkMate = False
        self.staleMate = False

    # makes moves except castling, en passant, pawn promotion
    def makeMove(self, move):
        self.board[move.startRow][move.startCol] = "--"
        self.board[move.endRow][move.endCol] = move.pieceMoved
        self.moveLog.append(move)
        self.whiteToMove = not self.whiteToMove
        # update the king's loaction if moved
        if move.pieceMoved == 'b_K':
            self.blackKingLocation = (move.endRow, move.endCol)
        elif move.pieceMoved == 'w_K':
            self.whiteKingLocation = (move.endRow, move.endCol)

        # pawn promotion
        if move.isPawnPromotion:
            # selectedPiece = input("Promote to Q, R, B, or N: ") # this can be done in UI later
            # eikhane pore selectePiece dewa jabe
            self.board[move.endRow][move.endCol] = move.pieceMoved[0] + '_Q'

    def undoMove(self, mode=0):
        if mode == 'all':
            while len(self.moveLog) != 0:
                move = self.moveLog.pop()
                self.board[move.startRow][move.startCol] = move.pieceMoved
                self.board[move.endRow][move.endCol] = move.pieceCaptured
                self.whiteToMove = not self.whiteToMove

            # reset the king's location to initial after undo all
            # this means a new game
            # king location
            self.whiteKingLocation = (5, 4)
            self.blackKingLocation = (0, 4)

        elif mode > 0:
            for i in range(int(mode)):
                move = self.moveLog.pop()
                self.board[move.startRow][move.startCol] = move.pieceMoved
                self.board[move.endRow][move.endCol] = move.pieceCaptured
                self.whiteToMove = not self.whiteToMove
                # update the king's loaction if moved
                if move.pieceMoved == 'b_K':
                    self.blackKingLocation = (move.startRow, move.startCol)
                elif move.pieceMoved == 'w_K':
                    self.whiteKingLocation = (move.startRow, move.startCol)

        elif len(self.moveLog) != 0:

            move = self.moveLog.pop()
            self.board[move.startRow][move.startCol] = move.pieceMoved
            self.board[move.endRow][move.endCol] = move.pieceCaptured
            self.whiteToMove = not self.whiteToMove
            # update the king's loaction if moved
            if move.pieceMoved == 'b_K':
                self.blackKingLocation = (move.startRow, move.startCol)
            elif move.pieceMoved == 'w_K':
                self.whiteKingLocation = (move.startRow, move.startCol)

        return move

    # >>>>>>>>>>>>   Move Generation Section <<<<<<<<<<<<<<<<<<

    # all moves with considering checks

    def getValidMoves(self):
        # >>> the following algorithm is naive and
        # is implemented concerning the checks <<<

        # step-1: generate all possible moves
        moves = self.getAllPossibleMoves()

        # step-2: for each move make the move
        for i in range(len(moves) - 1, -1, -1):  # when removing from list we go backward
            self.makeMove(moves[i])
            # step-3: generate all opponent's move
            # step-4: for each of opponent's move, see if the attact your king
            self.whiteToMove = not self.whiteToMove
            if self.inCheck():
                # step-5: if they attack your king, it's not a valid move
                moves.remove(moves[i])
            self.whiteToMove = not self.whiteToMove
            self.undoMove()

        # checking for - CheckMate / StaleMate
        if len(moves) == 0:
            if self.inCheck():
                self.checkMate = True
            else:
                self.staleMate = True
        else:
            self.checkMate = False
            self.staleMate = False

        return moves

    '''Determine if the current player in check'''

    def inCheck(self):
        if self.whiteToMove:
            return self.squareUnderAttack(self.whiteKingLocation[0], self.whiteKingLocation[1])
        else:
            return self.squareUnderAttack(self.blackKingLocation[0], self.blackKingLocation[1])

    '''Determine if the enemy can attack the square(r, c)'''

    def squareUnderAttack(self, r, c):
        self.whiteToMove = not self.whiteToMove  # switch to opponent's move
        oppMoves = self.getAllPossibleMoves()
        self.whiteToMove = not self.whiteToMove  # switch turns back
        for move in oppMoves:
            if move.endRow == r and move.endCol == c:  # square under attack
                return True
        return False

    # all moves without considering checks

    def getAllPossibleMoves(self):
        moves = []
        for r in range(len(self.board)):
            for c in range(len(self.board[r])):
                turn = self.board[r][c][0]
                if (turn == 'w' and self.whiteToMove) or (turn == 'b' and not self.whiteToMove):
                    piece = self.board[r][c][2]
                    # calls the appropriate move function based on piece
                    self.moveFunctions[piece](r, c, moves)

        return moves

    '''
    Get all the pawn moves for a pawn located at row, column and add these moves to list
    '''

    def getPawnMoves(self, r, c, moves):
        if self.whiteToMove:  # white pawn moves
            if r > 0:  # row index checking
                if self.board[r - 1][c] == "--":  # 1 square pawn advance
                    moves.append(Move((r, c), (r - 1, c), self.board))  # samne jabe
                if c - 1 > -1:
                    # left corner enemy piece to capture
                    if self.board[r - 1][c - 1][0] == 'b':
                        moves.append(Move((r, c), (r - 1, c - 1), self.board))  # left corner e khabe
                if c + 1 < 5:
                    # right corner enemy piece to capture
                    if self.board[r - 1][c + 1][0] == 'b':
                        moves.append(Move((r, c), (r - 1, c + 1), self.board)) # right corner e khabe

        else:  # black pawn moves ,, black eo white er motoi
            if r < 5:  # row index checking
                if self.board[r + 1][c] == "--":  # 1 square pawn advance
                    moves.append(Move((r, c), (r + 1, c), self.board))
                if c - 1 > -1:
                    # right corner enemy piece to capture
                    if self.board[r + 1][c - 1][0] == 'w':
                        moves.append(Move((r, c), (r + 1, c - 1), self.board))
                if c + 1 < 5:
                    # left corner enemy piece to capture
                    if self.board[r + 1][c + 1][0] == 'w':
                        moves.append(Move((r, c), (r + 1, c + 1), self.board))

    '''
    Get all the rook moves for a rook located at row, column and add these moves to list
    '''

    def getRookMoves(self, r, c, moves):
        directions = ((-1, 0), (0, -1), (1, 0), (0, 1))  # up, left, down right
        enemyColor = 'b' if self.whiteToMove else 'w'

        for d in directions:
            for i in range(1, 6):
                endRow = r + d[0] * i
                endCol = c + d[1] * i

                if 0 <= endRow < 6 and 0 <= endCol < 5:  # check on board
                    endPiece = self.board[endRow][endCol]
                    if endPiece == '--':  # empty space so valid
                        moves.append(
                            Move((r, c), (endRow, endCol), self.board))
                    elif endPiece[0] == enemyColor:
                        moves.append(
                            Move((r, c), (endRow, endCol), self.board))
                        break
                    else:  # friendly piece (own piece)
                        break
                else:  # off board
                    break

    '''
    Get all the knight moves for a knight located at row, column and add these moves to list
    '''

    def getKnightMoves(self, r, c, moves):
        knightMoves = ((-2, -1), (-2, 1), (-1, -2), (-1, 2),
                       (1, -2), (1, 2), (2, -1), (2, 1))
        allyColor = 'w' if self.whiteToMove else 'b'

        for m in knightMoves:
            endRow = r + m[0]
            endCol = c + m[1]
            if 0 <= endRow < 6 and 0 <= endCol < 5:  # check on board
                endPiece = self.board[endRow][endCol]
                if endPiece[0] != allyColor:
                    moves.append(Move((r, c), (endRow, endCol), self.board))

    '''
    Get all the bishop moves for a bishop located at row, column and add these moves to list
    '''

    def getBishopMoves(self, r, c, moves):
        directions = ((-1, -1), (-1, 1), (1, -1), (1, 1))  # all 4 diagonals
        enemyColor = 'b' if self.whiteToMove else 'w'

        for d in directions:
            for i in range(1, 5):  # a bishop can move maximum 4 diagonal squares
                endRow = r + d[0] * i
                endCol = c + d[1] * i

                if 0 <= endRow < 6 and 0 <= endCol < 5:  # check on board
                    endPiece = self.board[endRow][endCol]
                    if endPiece == '--':  # empty space so valid
                        moves.append(
                            Move((r, c), (endRow, endCol), self.board))
                    elif endPiece[0] == enemyColor:
                        moves.append(
                            Move((r, c), (endRow, endCol), self.board))
                        break
                    else:  # friendly piece (own piece)
                        break
                else:  # off board
                    break

    '''
    Get all the queen moves for a queen located at row, column and add these moves to list
    '''

    def getQueenMoves(self, r, c, moves):
        self.getRookMoves(r, c, moves)
        self.getBishopMoves(r, c, moves)

    '''
    Get all the king moves for a king located at row, column and add these moves to list
    '''

    def getKingMoves(self, r, c, moves):
        kingMoves = ((-1, -1), (-1, 0), (-1, 1), (0, -1),
                     (0, 1), (1, -1), (1, 0), (1, 1))
        allyColor = 'w' if self.whiteToMove else 'b'
        for i in range(len(kingMoves)):
            endRow = r + kingMoves[i][0]
            endCol = c + kingMoves[i][1]
            if 0 <= endRow < 6 and 0 <= endCol < 5:  # check on board
                endPiece = self.board[endRow][endCol]
                # not an ally (empty or enemy piece)
                if endPiece[0] != allyColor:
                    moves.append(Move((r, c), (endRow, endCol), self.board))


class Move():
    ranksToRows = {
        "1": 5,
        "2": 4,
        "3": 3,
        "4": 2,
        "5": 1,
        "6": 0
    }
    rowsToRanks = {v: k for k, v in ranksToRows.items()}

    filesToCols = {
        "a": 0,
        "b": 1,
        "c": 2,
        "d": 3,
        "e": 4
    }
    colsToFiles = {v: k for k, v in filesToCols.items()}

    def __init__(self, startSq, endSq, board) -> None:
        self.startRow = startSq[0]
        self.startCol = startSq[1]
        self.endRow = endSq[0]
        self.endCol = endSq[1]
        self.pieceMoved = board[self.startRow][self.startCol]
        self.pieceCaptured = board[self.endRow][self.endCol]
        self.isPawnPromotion = (self.pieceMoved == 'w_P' and self.endRow == 0) or (
                self.pieceMoved == 'b_P' and self.endRow == 5)
        self.moveID = self.startRow * 1000 + self.startCol * \
                      100 + self.endRow * 10 + self.endCol

    '''
    Overriding the equals method
    '''

    def __eq__(self, other):
        if isinstance(other, Move):
            return self.moveID == other.moveID
        return False

    def getChessNotation(self):
        return self.getRankFile(self.startRow, self.startCol) + ' >> ' + self.getRankFile(self.endRow, self.endCol)

    def getRankFile(self, r, c):
        return self.colsToFiles[c] + self.rowsToRanks[r]
