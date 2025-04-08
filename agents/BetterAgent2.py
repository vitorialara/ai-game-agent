# Better agent: Add your own agent here
from cmath import sqrt
from operator import indexOf
from agents.agent import Agent
from store import register_agent
import time
import numpy as np
import sys

def debug(*objects, sep=' ', end='\n', file=sys.stdout, flush=False):
        DB = 0
        if(DB):
            print(*objects)

@register_agent("better_agent2")
class BetterAgent2(Agent):

    def __init__(self):
        super(BetterAgent2, self).__init__()
        self.name = "BetterAgent2"
        self.autoplay = True # Change to enable autplay (default runs 1000)
        
        self.dir_map = {
            "u": 0,
            "r": 1,
            "d": 2,
            "l": 3,
        }

    def check_endgame(self, board, my_pos, adv_pos):

        """
        Check if the game ends and compute the current score of the agents.

        Returns
        -------
        is_endgame : bool
            Whether the game ends.
        player_1_score : int
            The score of player 1.
        player_2_score : int
            The score of player 2.
        """
        moves = ((-1, 0), (0, 1), (1, 0), (0, -1))

        p0_pos = my_pos
        p1_pos = adv_pos

        board_size = len(board)
        # Union-Find
        father = dict()
        for r in range(board_size):
            for c in range(board_size):
                father[(r, c)] = (r, c)

        def find(pos):
            if father[pos] != pos:
                father[pos] = find(father[pos])
            return father[pos]

        def union(pos1, pos2):
            father[pos1] = pos2

        for r in range(board_size):
            for c in range(board_size):
                for dir, move in enumerate(
                    moves[1:3] 
                ):  # Only check down and right
                    if board[r, c, dir + 1]:
                        continue
                    pos_a = find((r, c))
                    pos_b = find((r + move[0], c + move[1]))
                    if pos_a != pos_b:
                        union(pos_a, pos_b)

        for r in range(board_size):
            for c in range(board_size):
                find((r, c))
        p0_r = find(tuple(p0_pos))
        p1_r = find(tuple(p1_pos))
        p0_score = list(father.values()).count(p0_r)
        p1_score = list(father.values()).count(p1_r)
        if p0_r == p1_r:
            return False, p0_score, p1_score
        player_win = None
        win_blocks = -1
        if p0_score > p1_score:
            player_win = 0
            win_blocks = p0_score
        elif p0_score < p1_score:
            player_win = 1
            win_blocks = p1_score
        else:
            player_win = -1  # Tie
            '''
        if player_win >= 0:
            logging.info(
                f"Game ends! Player {self.player_names[player_win]} wins having control over {win_blocks} blocks!"
            )
        else:
            logging.info("Game ends! It is a Tie!")
            '''
        return True, p0_score, p1_score

    def check_valid_step(self, start_pos, end_pos, adv_pos, barrier_dir, chess_board, max_step):
        """
        Check if the step the agent takes is valid (reachable and within max steps).

        Parameters
        ----------
        start_pos : tuple
            The start position of the agent.
        end_pos : np.ndarray
            The end position of the agent.
        barrier_dir : int
            The direction of the barrier.
        """
        moves = ((-1, 0), (0, 1), (1, 0), (0, -1))

        # Endpoint already has barrier or is border
        r, c = end_pos
        if chess_board[r, c, barrier_dir]:
            return False
        if np.array_equal(start_pos, end_pos): # We're alreay there :)
            return True

        # Get position of the adversary
        adv_pos = adv_pos

        # BFS
        state_queue = [(start_pos, 0)]
        visited = {tuple(start_pos)}
        is_reached = False
        while state_queue and not is_reached:
            cur_pos, cur_step = state_queue.pop(0)
            
            r, c = cur_pos
            if cur_step == max_step:
                break

            for dir, move in enumerate(moves):
                if chess_board[r, c, dir]: # There's a wall, can't go there
                    continue

                next_pos = (cur_pos[0]+move[0], cur_pos[1]+move[1])
                if np.array_equal(next_pos, adv_pos) or tuple(next_pos) in visited: # Either already visited or we are where adv_pos is
                    continue
                if np.array_equal(next_pos, end_pos):
                    is_reached = True # We got there !!
                    break

                visited.add(tuple(next_pos))
                state_queue.append((next_pos, cur_step + 1))

        return is_reached

    def set_barrier(self, r, c, dir, board):
        opposites = {0: 2, 1: 3, 2: 0, 3: 1}
        # Set the barrier to True
        board[r, c, dir] = True
        # Set the opposite barrier to True
        moves = ((-1, 0), (0, 1), (1, 0), (0, -1))
        move = moves[dir]
        board[r + move[0], c + move[1], opposites[dir]] = True

    def checkPossEnd(self, newMove, board):
        r, c, dir = newMove
        # If this function returns true, the move COULD be a win, loss, or tie

        rows = cols = len(board)
        if(dir == 0 or dir == 2): # if dir wall is placed is up or down
            # Need to check if there are walls on it's left and right
            wallHL = (c == 0) or (board[r,c-1, dir]) # Wall horizontal left
            wallHR = (c == cols-1) or (board[r, c+1, dir]) # Wall horizontal right

            if(dir == 0): # Wall placed up
                wallVL = board[r,c,3] or board[r-1, c, 3]
                wallVR = board[r,c,1] or board[r-1, c, 1]
                
            elif(dir == 2): # Wall placed down
                wallVL = board[r,c,3] or board[r+1,c,3]
                wallVR = board[r,c,1] or board[r+1,c,1]

        
            return (wallVL or wallHL) and (wallVR or wallHR)

        elif(dir == 1 or dir == 3): # If dir wall is placed is right or left
            wallVUp = (r == 0) or (board[r-1, c, dir])
            wallVDown = (r == rows-1) or (board[r+1, c, dir])

            if(dir == 1): # wall placed Right 
                wallHUp = board[r, c, 0] or board[r, c+1, 0]
                wallHDown = board[r, c, 2] or board[r, c+1, 2]

            elif(dir == 3): # wall placed left
                wallHUp = board[r, c, 0] or board[r, c-1, 0]
                wallHDown = board[r, c, 2] or board[r, c-1, 2]

            return(wallHUp or wallVUp) and (wallHDown or wallVDown)

        return False

    def checkIfWallAdj(self, my_pos, adv_pos):
        mX, mY, dir = my_pos
        aX, aY = adv_pos

        if((mX == aX and mY == aY-1)): # We're on the left 
            if(dir == 1):
                return True
        if((mX == aX and mY == aY+1)): # We're on the right
            if(dir == 3):
                return True
        if((mY == aY and mX == aX-1)): # We're on top
            if(dir == 2):
                return True
        if((mY == aY and mX == aX+1)): # We're on the bottom
            if(dir == 0):
                return True
            
        return False

    def findQuadrant(self, pos, board_size):
        r, c = pos

        # Up Right Down Left
        corners = [(0, board_size-1), (0,0), (board_size-1, 0), (board_size-1,board_size-1)]
        distances = [] # Top Left, Top Right, 
        for c in corners:
            distances.append(self.dist(pos, c))

        quadrant = distances.index(min(distances))+1
        return quadrant
        '''
        if(r <= board_size//2):
            # We're in top half, Q1 or Q2
            if(c <= board_size//2):
                return 2
            else:
                return 1

        else:
            # We're in bottom half, Q3, or Q4
            if(c <= board_size//2):
                return 3
            else:
                return 4
        '''
    def checkWallProx(self, move_pos, adv_pos, board_size):
        # This method will return whether executing a move would 
        # put leave the opponent between you and a wall (good -> True) or 
        # not (bad -> False)

        # First need to figure out what quadrant we're in
        quadrant = 0 # Using same convention as graphs
        # 1 = top right
        # 2 = top left
        # 3 = bot left
        # 4 = bot right

        mR, mC = move_pos
        aR, aC = adv_pos
        """
        # Option 1, do it by quadrant 
        myQuad = self.findQuadrant(move_pos, board_size)
        advQuad = self.findQuadrant(adv_pos, board_size)

        if(myQuad == advQuad):
            # We're in the same quadrant
            if(myQuad == 1):
                return (mC < aC or mR > aR)
            elif(myQuad == 2):
                return (mC > aC or mR > aR)
            elif(myQuad == 3):
                return (mC > aC or mR < aR)
            elif(myQuad == 4):
                return (mC < aC or mR < aR)
            
        return True # If not same quadrant, we don't really care
        """

        ''' Option 2, by proximity to nearest border
        # Four possibilities as far as proximity goes
        # Up Right Down Left 
        mDistances = [mR, board_size - mC, mR, board_size - mR]
        aDistances = [aR, board_size - aC, aR, board_size - aR]

        return min(mDistances) > min(aDistances)
       '''

        # Option 3, by proximity to center
        center = (board_size//2, board_size//2)
        return self.dist(move_pos, center)
        # return self.dist(adv_pos, center) > self.dist(move_pos, center)



    def flowChartStrategy(self, my_pos, adv_pos, board, max_step):
        startTime = time.time()

        # First, find worstCase move
        for i, wall in enumerate(board[my_pos[0], my_pos[1]]):
            if(not wall):
                break

        worstCaseMove = my_pos
        worstCaseDir = i

        possibleMoves = []
        safeMovesByDistance = {}

        for r, row in enumerate(board):
            for c, col in enumerate(row):
                for bDir, w in enumerate(board[r,c]):
                    if(self.check_valid_step(my_pos, (r,c), adv_pos, bDir, board, max_step)):
                        # check_valid_step(self, start_pos, end_pos, adv_pos, barrier_dir, chess_board, max_step):
                        # if no wall and valid move from my_pos to r,c
                        # (self, start_pos, end_pos, adv_pos, barrier_dir, chess_board, max_step):

                        possibleMoves.append((r,c, bDir)) # Valid !
                        
        if(time.time() - startTime > 1.95):
            return (worstCaseMove[0], worstCaseMove[1], worstCaseDir)
        
        better = []
        notGood = []
        ties = []
        adjBest = []
        good = []

        for move in possibleMoves:

            if(time.time() - startTime > 1.95):
                return (worstCaseMove[0], worstCaseMove[1], worstCaseDir)

            if(self.checkPossEnd(move, board)):
                # Possibly a win, tie, or loss
                # TODO: These are sometimes out of range for some reason 
                testBoard = board
                new_test_pos_r = move[0] 
                new_test_pos_c = move[1]
                test_dir = move[2]

                self.set_barrier(new_test_pos_r, new_test_pos_c, test_dir, testBoard)
                isEnd, myScore, advScore = self.check_endgame(board, my_pos, adv_pos)

                if(isEnd and myScore > advScore): # Win !!
                    return (move[0], move[1], move[2])
                elif(isEnd and myScore == advScore): # Tie :/
                    worstCaseMove = (move[0], move[1])
                    worstCaseDir = move[2]
                    ties.append(move)
                    continue
                elif(isEnd and myScore < advScore):
                    continue # Ignore this case, it's a loss
                # If none of these three occur, then the move for sure does not end the game 

            # Now, categorize non-game-ending moves into good, better, best, and not good
            # not good if we end up with 3 walls around us (boxed in)

            n=0
          
            
            for i, wall in enumerate(board[move[0], move[1]]):
                if(i == move[2]):  # There's a wall there bc we would place one
                    n += 1
                elif(wall):  # There's a wall there from the get go
                    n += 1
        
            # Counts number of walls, and add one for the one we place
            # n = board[move[0], move[1]].count(1) + 1
            
            if(n >= 3):  # If there are 3 or more walls around us
                notGood.append(move)

            else:

                if(self.checkIfWallAdj(move, adv_pos)):
                    adjBest.append(move)
                else:
                    
                    # Option 2 : Rank moves by how close they are to the center
                    distance = self.checkWallProx((move[0], move[1]), adv_pos, len(board))
                    safeMovesByDistance[distance] = move
                    
                    #if(self.checkWallProx((move[0], move[1]), adv_pos, len(board))):
                    #    better.append(move) 
                        # Means the move will ensure we are further from the barrier than the opponent
                        # (if in same quadrant)
                    #else:
                        #good.append(move)
                    
                '''
                    # Option 1: rank safe moves by distance from opponent     
                    distance = self.dist((move[0], move[1]), adv_pos)
                    safeMovesByDistance[distance] = move
                '''
                
        
        if(time.time() - startTime > 1.95):
            return (worstCaseMove[0], worstCaseMove[1], worstCaseDir)

        safeMoves = sorted(safeMovesByDistance.items())
        # masterList = [foo[1] for foo in safeMoves]+ties+unsafe
        # masterList = safe+ties+unsafe[::-1]
        masterList = adjBest+better+[foo[1] for foo in safeMoves]+ties+notGood
        # debug(safeMoves)

        if(not len(masterList)):  # If list is empty --> return worstCase move
            return (worstCaseMove[0], worstCaseMove[1], worstCaseDir)

        # Return first element, hopefully a safe move or a tie
        return masterList[0]

    def dist(self, my_pos, adv_pos):
        mR, mC = my_pos
        aR, aC = adv_pos

        return ((mR-aR)**2+(mC-aC)**2)**(1/2)
    

    def step(self, chess_board, my_pos, adv_pos, max_step):
        """
        Implement the step function of your agent here.
        You can use the following variables to access the chess board:
        - chess_board: a numpy array of shape (x_max, y_max, 4)
        - my_pos: a tuple of (x, y)
        - adv_pos: a tuple of (x, y)
        - max_step: an integer

        You should return a tuple of ((x, y), dir),
        where (x, y) is the next position of your agent and dir is the direction of the wall
        you want to put on.

        Please check the sample implementation in agents/random_agent.py or agents/human_agent.py for more details.
        """
        
        # Up, Right, Down, Left 
        
        result = self.flowChartStrategy(my_pos, adv_pos, chess_board, max_step)
        pos_out = (result[0], result[1])
        dir_out = result[2]
        debug("Result: ",result)

        return pos_out, dir_out
