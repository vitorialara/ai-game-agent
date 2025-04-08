# Student agent: Add your own agent here
from cmath import sqrt
from agents.agent import Agent
from store import register_agent
import numpy as np
import threading as th
import sys

def debug(*objects, sep=' ', end='\n', file=sys.stdout, flush=False):
        DB = 0
        if(DB):
            print(*objects)

@register_agent("old_agent")
class old_agent(Agent):
    """
    A dummy class for your implementation. Feel free to use this class to
    add any helper functionalities needed for your agent.
    """
    moveName = ["Up", "Right", "Down", "Left"]

    def __init__(self):
        super(old_agent, self).__init__()
        self.name = "old_agent"
        self.autoplay = True # Change to enable autplay (default runs 1000)
        
        self.dir_map = {
            "u": 0,
            "r": 1,
            "d": 2,
            "l": 3,
        }

    
    def dist(self, my_pos, adv_pos):
        mR, mC = my_pos
        aR, aC = adv_pos

        return ((mR-aR)**2+(aR-aC)**2)**(1/2)
        

    # TODO: Make a function to see if we are one square adjacent to adv
    def checkIfAdj(self, my_pos, adv_pos):
        mX, mY = my_pos
        aX, aY = adv_pos

        if((mX == aX and mY == aY-1) or
            (mX == aX and mY == aY+1) or \
            (mY == aY and mX == aX-1) or \
            (mY == aY and mX == aX+1)):

            return True # We are adjacent to them, stop moving

        return False

    def pickDirection(self, my_pos, adv_pos, possible):
        allDirs = [(-1,0), (0,1), (1,0), (0,-1)]
        # Think of X as row, and Y as column
        # I know it's confusing
        myX, myY = my_pos
        advX, advY = adv_pos

        # Up, Right, Down, Left = 
        # [(-1,0), (0,1), (1,0), (0,-1)]
        # debug(possible)
        if(((myX - advX)**2 > (myY - advY)**2)):
            
            # difference in R bigger, focus on up or down
            r = (-1*np.sign(myX-advX), 0)
            dir = allDirs.index(r)
            if(r in possible):
                return r, dir
            else:
                # newR = (0, r[0])
                newR = (-1*r[0], 0)
                dir = allDirs.index(newR)
                if(newR in possible):
                    return newR, dir
        elif(((0,-1) not in possible) and ((0,1) not in possible)): # When right and left not possible
            debug("We made it :)")
            debug("Possible: ",possible)

            r = (-1*np.sign(myX-advX), 0)

            if(r==(0,0)):
                 r = (np.random.choice([-1,1]), 0)

            dir = allDirs.index(r)

            if(r in possible):
                return r, dir
            else:
                newR = (-1*r[0], 0)
                dir = allDirs.index(newR)
                if(newR in possible):
                    return newR, dir
            
        # Either difference is bigger in Cs or difference is equal 
        r = (0, -1*np.sign(myY-advY)) # Error if difference is 0 
        if(r == (0,0)):
            r = possible[0] # TODO: ????
        dir = allDirs.index(r)  
        if(r in possible): # difference in Y bigger, focus on up or down
            return r, dir
        else:
            # newR = (r[1], 0)
            newR = (0, -1*r[1])
            dir = allDirs.index(newR)
            if(newR in possible):
                return newR, dir  

        debug("This should never be displayed !!")
        return (0,0), 0 # Should never happen

    def boxChecker(self, board, my_pos):
        mR, mC = my_pos
        around = board[mR, mC]
        
        nOfWalls = np.sum(around) # Sum counts number of Trues == walls
        if(nOfWalls == 3):
            for index, wall in enumerate(around):
                if(not wall):
                    debug("Stuck at", self.moveName[index])
                    return True, index # True, we will be boxed in, and index is dir to head
        return False, -1
        
    

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
        # TODO: Add a checker if we're about to 'box ourselves in'
            # TODO: There's something wrong with the checker :/
        # TODO: Add a flag for special 'T'-case
        # TODO: Figure out a way to know when to stop early
        
        # Up, Right, Down, Left 
        
        '''
        result = self.flowChartStrategy(my_pos, adv_pos, chess_board, max_step)
        pos_out = (result[0], result[1])
        dir_out = result[2]
        debug("Result: ",result)

        return pos_out, dir_out

        '''
        allDirs = [(-1,0), (0,1), (1,0), (0,-1)]
        posVisited = set() # Keeps track of positions visited 

        

        for m in range(max_step):
            debug("Current Pos: ",my_pos)
            posVisited.add(my_pos)

            mx, my = my_pos

            # Check if we are about to be boxed in
            areWeStuck, pathOut = self.boxChecker(chess_board, my_pos)

            possibleWalls = [(-1,0), (0,1), (1,0), (0,-1)]
            possibleMoves = [(-1,0), (0,1), (1,0), (0,-1)]

            if(areWeStuck):    
                nR, nC = allDirs[pathOut]
                next = (mx + nR, my + nC)
                debug("We got stuck :(",nR, nC,pathOut, next)
                dir = self.pickDirection(next, adv_pos, possibleMoves)[1]
                possibleWalls.remove(allDirs[(pathOut)])
                # If the next move is potentially further, break, else calculate the next move
                if(self.dist(my_pos, adv_pos) < self.dist(next, adv_pos)):
                    my_pos = next
                    continue
                else:
                    my_pos = next
                    break
                

            if(self.checkIfAdj(my_pos, adv_pos) and not areWeStuck):
                
                dir = self.pickDirection(my_pos, adv_pos, possibleMoves)[1]
                debug(my_pos, "is Adjacent ! to",adv_pos," placing wall with dir",self.moveName[dir])

                # If there is a wall ALREADY placed in the adjacent direction, pick a different move
                if(not chess_board[my_pos[0], my_pos[1], dir]): 
                    debug("Adjacent and there is NO wall !!")
                    break

                #break

            # Moves (Up, Right, Down, Left)
            r, c = my_pos
            
            if(not areWeStuck):
                

                newPos, dir = self.pickDirection(my_pos, adv_pos, possibleMoves)
                mx, my = newPos

                next = (r + mx, c + my)

            k=0

            # The problem is we are categorizing moves and their walls together
            while((chess_board[r, c, dir] or next == adv_pos or self.boxChecker(chess_board, next)[0]) and not areWeStuck):
                debug("Current big loop iter: ",k,next,self.moveName[dir],"Can't go bc of wall!")
                debug("removing (",mx,my,")")
                # recalculate move because there's a wall
                possibleMoves.remove((mx, my))
                newPos, dir = self.pickDirection(my_pos, adv_pos, possibleMoves)
                debug("Current Dir:",self.moveName[dir],newPos)
                mx, my = newPos

                next = (r + mx, c + my)

                k += 1
                if k > 20:
                    break
            
            if(next in posVisited): # if the place they want us to go has already been visited
                debug("Been there, done that")
                dir = (dir+2)%4
                break

            my_pos = next

        barrierDir = dir

        r,c = my_pos
        
        i=0
        debug("Pos before wall loop:",my_pos,self.moveName[barrierDir])

        while chess_board[r, c, barrierDir]:
            debug("Wall determ. iteration: ",i,"barrierDir: ",self.moveName[barrierDir])
            debug(possibleWalls)
            barrierDir = self.pickDirection(my_pos, adv_pos, possibleWalls)[1]

            possibleWalls.remove(allDirs[barrierDir])
            i+=1
            debug("POST Wall determ. iteration: ",i,"barrierDir: ",self.moveName[barrierDir])
            

        return my_pos, barrierDir

