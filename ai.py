import random;
pieceValue={"K":0,"Q":10,"R":4,"B":4,"N":7,"P":1};

knightGoodPositionsOnBoard=[
                    [1, 1, 1, 1, 1],
                    [1, 2, 2, 2, 1],
                    [1, 2, 3, 2, 1],
                    [1, 2, 3, 2, 1],
                    [1, 2, 2, 2, 1],
                    [1, 1, 1, 1, 1]
                    ];

bishopGoodPositionsOnBoard=[
                    [3, 2, 1, 2, 3],
                    [3, 3, 2, 3, 3],
                    [2, 3, 3, 3, 2],
                    [2, 3, 3, 3, 2],
                    [3, 3, 2, 3, 3],
                    [3, 2, 1, 2, 3]
                    ];
queenGoodPositionsOnBoard=[
                    [1, 2, 1, 2, 1],
                    [1, 2, 2, 2, 1],
                    [1, 2, 3, 2, 1],
                    [1, 2, 3, 2, 1],
                    [1, 2, 2, 2, 1],
                    [1, 2, 1, 2, 1]
                    ];
rookGoodPositionsOnBoard=[
                    [3, 3, 3, 3, 3],
                    [3, 2, 2, 2, 3],
                    [1, 2, 1, 2, 1],
                    [1, 2, 1, 2, 1],
                    [3, 2, 2, 2, 3],
                    [3, 3, 3, 3, 3]
                    ];
whitePawnGoodPositionsOnBoard=[
                        [5, 5, 5, 5, 5],
                        [4, 4, 4, 4, 4],
                        [3, 3, 3, 3, 3],
                        [2, 2, 2, 2, 2],
                        [1, 1, 1, 1, 1],
                        [0, 0, 0, 0, 0]
                        ];
blackPawnGoodPositionsOnBoard=[
                        [0, 0, 0, 0, 0],
                        [1, 1, 1, 1, 1],
                        [1, 2, 2, 2, 1],
                        [2, 3, 3, 3, 2],
                        [3, 4, 4, 4, 3],
                        [5, 5, 5, 5, 5]
                        ];

piecePositionalScore={
    "N":knightGoodPositionsOnBoard,
    "B":bishopGoodPositionsOnBoard,
    "Q":queenGoodPositionsOnBoard,
    "R":rookGoodPositionsOnBoard,
    "w_P":whitePawnGoodPositionsOnBoard,
    "b_P":blackPawnGoodPositionsOnBoard
}

CHECKMATE=float('inf');
STALEMATE=0;
DEPTH=0;

def findRandomMove(validMoves):
    return validMoves[random.randint(0,len(validMoves)-1)];

def findBestMove(gamestate, validMoves):
    global nextMove, counter
    nextMove = None  #it will store the best move found by Minimax.
    
    # Shuffle the order of valid moves to add variety to the AI's choices.
    random.shuffle(validMoves)
    #count the total moves evaluated.
    counter = 0

    MinMaxWithPruning(gamestate, validMoves, DEPTH, -CHECKMATE, CHECKMATE, 1 if gamestate.whiteToMove else -1)
    
    # Print the total number of moves evaluated at the given depth 
    print(f"{counter} possible moves in depth {DEPTH}")
    
    # Return the best move found by the search
    return nextMove


def MinMaxWithPruning(gamestate, validMoves, depth, alpha, beta, turnMultiplier):
    global nextMove, counter
    counter += 1 

    # Base case: If we've reached the maximum search depth, return the board score.
    if depth == 0:
        # Score is adjusted by turnMultiplier to reflect the current player's perspective.
        return turnMultiplier * scoreBoard(gamestate)

    maxScore = -CHECKMATE

    for move in validMoves:
        gamestate.makeMove(move) 
        nextMoves = gamestate.getValidMoves()  # Generate the next set of valid moves for the opponent.

        score = -MinMaxWithPruning(gamestate, nextMoves, depth-1, -beta, -alpha, -turnMultiplier)

        if score > maxScore:
            maxScore = score  

            if depth == DEPTH:
                nextMove = move

        gamestate.undoMove()  # Undo the move to restore the game state for the next iteration.

        # Update alpha if we've found a new best score.
        if maxScore > alpha:
            alpha = maxScore

        # Alpha-beta pruning: If alpha exceeds beta, we can stop evaluating this branch.
        if alpha >= beta:
            break

    return maxScore



def scoreBoard(gamestate):
    # Check if the game state is in checkmate.
    if gamestate.checkMate:
        if gamestate.whiteToMove:
            return -CHECKMATE  # Negative infinity to indicate a loss for white.
        else:
            return CHECKMATE  # Positive infinity to indicate a win for white.

    elif gamestate.staleMate:
        return STALEMATE  # Return 0 for a drawn position.

    score = 0  # Initialize score to 0, representing a neutral game state.

    # Loop through each square on the board.
    for row in range(len(gamestate.board)):
        for col in range(len(gamestate.board[row])):
            square = gamestate.board[row][col]

            # Check if the square is occupied by a piece.
            if square != "--":
                # Initialize positional score for the piece. The king does not use a positional score.
                piecePositionalScore = 0
                if square[-1] != "K":  
                    # For pawns, use specific positional values for black and white.
                    if square[-1] == "P":  
                        piecePositionalScore = piecePositionalScores[square][row][col]
                    else:  # For other pieces, use the general positional score.
                        piecePositionalScore = piecePositionalScores[square[-1]][row][col]

                # Calculate and add/subtract the piece’s value and positional score.
                if square[0] == 'w':  # White piece
                    # Add the piece’s base value and weighted positional score.
                    score += pieceValue[square[-1]] + piecePositionalScore * 0.1
                elif square[0] == 'b':  # Black piece
                    # Subtract the piece’s base value and weighted positional score.
                    score -= pieceValue[square[-1]] + piecePositionalScore * 0.1

    return score  # Return the final evaluated score.

