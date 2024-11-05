class GameState:
    def __init__(self):
        # Initialize a simplified 6x5 board for demonstration
        self.board = [
            ['b_R', 'b_N', 'b_B', 'b_Q', 'b_K'],
            ['b_P', 'b_P', 'b_P', 'b_P', 'b_P'],
            ['--', '--', '--', '--', '--'],
            ['--', '--', '--', '--', '--'],
            ['w_P', 'w_P', 'w_P', 'w_P', 'w_P'],
            ['w_R', 'w_N', 'w_B', 'w_Q', 'w_K'],
        ]
        # Mapping pieces to their move functions
        self.moveFunctions = {
            'P': self.getPawnMoves, 'R': self.getRookMoves,
            'N': self.getKnightMoves, 'B': self.getBishopMoves,
            'Q': self.getQueenMoves, 'K': self.getKingMoves
        }
        self.whiteToMove = True
        self.moveLog = []

    def getPawnMoves(self, r, c, moves):
        if self.whiteToMove:  # White pawn moves up
            if r > 0 and self.board[r - 1][c] == '--':
                moves.append((r, c, r - 1, c))  # Single square advance
        else:  # Black pawn moves down
            if r < len(self.board) - 1 and self.board[r + 1][c] == '--':
                moves.append((r, c, r + 1, c))  # Single square advance

    def getRookMoves(self, r, c, moves):
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        for d in directions:
            for i in range(1, len(self.board)):
                endRow, endCol = r + d[0] * i, c + d[1] * i
                if 0 <= endRow < len(self.board) and 0 <= endCol < len(self.board[0]):
                    endPiece = self.board[endRow][endCol]
                    if endPiece == '--':
                        moves.append((r, c, endRow, endCol))
                    elif endPiece[0] == ('w' if self.whiteToMove else 'b'):
                        break
                    else:
                        moves.append((r, c, endRow, endCol))
                        break
                else:
                    break

    def getKnightMoves(self, r, c, moves):
        knightMoves = [(-2, -1), (-1, -2), (1, -2), (2, -1), (2, 1), (1, 2), (-1, 2), (-2, 1)]
        allyColor = 'w' if self.whiteToMove else 'b'
        for m in knightMoves:
            endRow, endCol = r + m[0], c + m[1]
            if 0 <= endRow < len(self.board) and 0 <= endCol < len(self.board[0]):
                endPiece = self.board[endRow][endCol]
                if endPiece[0] != allyColor:
                    moves.append((r, c, endRow, endCol))

    def getBishopMoves(self, r, c, moves):
        directions = [(-1, -1), (-1, 1), (1, -1), (1, 1)]
        for d in directions:
            for i in range(1, len(self.board)):
                endRow, endCol = r + d[0] * i, c + d[1] * i
                if 0 <= endRow < len(self.board) and 0 <= endCol < len(self.board[0]):
                    endPiece = self.board[endRow][endCol]
                    if endPiece == '--':
                        moves.append((r, c, endRow, endCol))
                    elif endPiece[0] == ('w' if self.whiteToMove else 'b'):
                        break
                    else:
                        moves.append((r, c, endRow, endCol))
                        break
                else:
                    break

    def getQueenMoves(self, r, c, moves):
        # Queen's moves are a combination of rook and bishop moves
        self.getRookMoves(r, c, moves)
        self.getBishopMoves(r, c, moves)

    def getKingMoves(self, r, c, moves):
        kingMoves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]
        allyColor = 'w' if self.whiteToMove else 'b'
        for m in kingMoves:
            endRow, endCol = r + m[0], c + m[1]
            if 0 <= endRow < len(self.board) and 0 <= endCol < len(self.board[0]):
                endPiece = self.board[endRow][endCol]
                if endPiece[0] != allyColor:
                    moves.append((r, c, endRow, endCol))

    def getValidMoves(self):
        moves = []
        for r in range(len(self.board)):
            for c in range(len(self.board[r])):
                piece = self.board[r][c]
                if piece != '--':
                    color, type_ = piece[0], piece[2]
                    if (color == 'w' and self.whiteToMove) or (color == 'b' and not self.whiteToMove):
                        self.moveFunctions[type_](r, c, moves)
        return moves
