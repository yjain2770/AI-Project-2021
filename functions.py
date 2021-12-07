from random import choice, random
import numpy as np
from grid import next_play, isvalid, c, rand_moves, getAvailableMoves

gen = lambda: 2 if random() < .9 else 4
scoregrid = np.asarray([     [4**15,4**14,4**13,4**12],
                             [4**8,4**9,4**10,4**11],
                             [4**7,4**6,4**5,4**4],
                             [4**0,4**1,4**2,4**3]])
ind = np.arange(16).reshape(4,4)
ind1 = np.arange(16)

def getMove(data, plays_c):#snake strategy. Not much efficient as hardcoded stuffs are here.
    sc, mv = float('-inf'), 5
    mx = data.max()
    for  move in getAvailableMoves(data):
        moved = c(data.copy(), move) 
        if mx == data[0][0] and moved.max() != moved[0][0]:continue #stuck the head; temp added
        if ( moved == data).all(): continue
        score = 0
        score += minimaxab(moved.copy(), -np.inf, np.inf, plays_c, False)
        if move == 0 or move == 2: score+= 10000 #motivation on up or left.
        t_sc = score
        if t_sc > sc:
            sc= t_sc
            mv = move
        elif t_sc == sc:
            if mv in [0,2]: continue
            mv = random.choice([mv, move])
    return mv

def getChildren(data,playerT):
    #copyproof
    if playerT:
        l = []
        for move in range(4):
            #if (c(data, move) == data).all(): continue
            l.append(c(data, move))
    else:
        if 0 not in data: return [(data, 1)]
        indices = (ind[data == 0]).flatten()
        l = []
        for idx in indices:
            data1 = data.copy()
            p = idx - 4*(idx//4)
            data1[idx//4][p] = 2
            l.append((data1,0.9))
            data1[idx//4][p] = 4
            l.append((data1,0.1))
    return l

def score_G(data):
    #heuristics
    """
    Upgrades needed:
    1. Smootheness measure.
    2. It is hard coded for top-left. Needs to be automatically decide for any corner.
    """
    grid = scoregrid
    score = (grid * data).sum()
    """
    Not going in score's dimension is recommended.
    
    With below heuristic and 4th level AI: 2048: 50%+
    
    div = 100
    #a1 = -score/div if (data == 0).sum() < 3 else score/10 #free tiles
    a1 = score/(div*(16-(data == 0).sum()))
    a2 = score/div if data[0][0]>=data[1][0]>=data[2][0] else 0  #monoton1
    a3 = score/div if data[0][0]>=data[0][1]>=data[0][2]>=data[0][3] else -score/50 #monoton2
    a4 = score/div if data[0][3] >= data[1][3] else -score/20
    a5 = score/div if data.max() == data[0][0] else -score
    a6 = score/div if data[0][1] >= data[1][1] and data[0][2] >= data[1][2] else -score/2
    a7 = score/div if data[1][3] >= data[1][2] else -score/20
    -----------------------------------------------------------------------
    
    """
    div = 300
    #a1 = -score/div if (data == 0).sum() < 3 else score/10 #free tiles
    a1 = score/(div*(16-(data == 0).sum()))
    a2 = score/div if data[0][0]>=data[1][0]>=data[2][0] else 0  #left vert.1 monotone
    a3 = score/div if data[0][0]>=data[0][1]>=data[0][2]>=data[0][3] else -score/50 #top horz. monotone.
    a4 = score/div if data[0][3] >= data[1][3] and data[1][3] >= data[1][2] else -score/50 #1to2 rightop corner monotone
    a5 = score/div if data.max() == data[0][0] else -2*score #max at top left.
    a6 = score/div if data[0][1] >= data[1][1] >= data[2][1] else -score/3 #vert 2 mono
    a7 = score/div if data[0][2] >= data[1][2] >= data[2][2] else -score/20  #vert 3 mono
    a8 = score/div if data[2][2] <= data[1][2] else -score/20
    
    return score + a1+ a2+ a3 + a4 + a5 + a6 + a7 + a8

def expectimax(data,depth, maximizing):
    if depth <= 0 or not isvalid(data): return score_G(data)
    if maximizing:
        sc = float('-inf')
        for child in getChildren(data, True): #will run 4 times at max
            sc = max(sc, expectimax(child,depth-1,False))
        return sc
    if not maximizing: #chance node 
        sc = 0
        t = getChildren(data, False)
        for child,w in t:
            sc += w*expectimax(child,depth-1,True)
        return sc/len(t)

def minimaxab(data, alpha, beta,depth, maximizing):
    #funcs used: isvalid, score_G, getChildren
    if depth <= 0 or not isvalid(data): return score_G(data)
    if maximizing:
        sc = float('-inf')
        for child in getChildren(data, True): #will run 4 times at max
            sc = max(sc, minimaxab(child,alpha,beta, depth-1,False))
            if sc >= beta: return sc  #actually it is same as if alpha >= beta, 
                                        #maximizing player need not to care now #mamavsbhanja
            alpha = max(alpha, sc)
        return sc
    if not maximizing:
        sc = float('inf')
        for child,w in getChildren(data, False):
            sc = min(sc, minimaxab(child,alpha,beta, depth-1,True))
            if sc < alpha: return sc # minimizer need not to care
            beta = min(beta, sc)
        return sc

"""
def getMove(data, plays_c):
    sc, mv = float('-inf'), 5
    for  move in range(4):
        moved = c(data.copy(), move)
        if ( moved == data).all(): continue
        score = 0
        score += minimaxab(moved.copy(), -np.inf, np.inf, plays_c, False)
        if move == 0 or move == 2: score+= 10000 #motivation on up or left.
        t_sc = score
        if t_sc > sc:
            sc= t_sc
            mv = move
        elif t_sc == sc:
            if mv in [0,2]: continue
            mv = random.choice([mv, move])
    return mv
"""
"""
#Other versions of getMove, slight modifications:

def getMove(data, plays_c):
    #snake strategy with minimaxab
    sc, mv = float('-inf'), 5
    mx = data.max()
    for move in [0,2,3]:#for move in range(4)  temp change
        moved = c(data, move)
        if mx == data[0][0] and moved.max() != moved[0][0]:continue #stuck the head; temp added
        if ( moved == data).all(): continue
        score = 0
        score += minimaxab(moved, -np.inf, np.inf,plays_c, False)
        #score += expectimax(moved, plays_c, False)     #if running expectimax; not much effect due to weak heuristics.
        if move == 0 or move == 2: score += 10000 #motivation on up or left.
        t_sc = score
        if t_sc > sc:
            sc= t_sc
            mv = move
        elif t_sc == sc:
            if mv in [0,2]: continue
            mv = choice([mv, move])
    return mv

def getMove(data, plays_c):              #monte carlo version
    sc, mv = float('-inf'), 5
    mx = data.max()
    for move in [0,1,2,3]:
        score = 0
        #score += minimaxab(next_play(data.copy(), move),-np.inf, np.inf,plays_c, False)
        score += monte_carlo(data.copy(),move,plays_c = plays_c)
        t_sc = score
        if t_sc > sc:
            sc= t_sc
            mv = move
        elif t_sc == sc:
            mv = choice([mv, move])
    return mv

Other modified heuristics for snake strategy:
    div = 300
    #a1 = -score/div if (data == 0).sum() < 3 else score/10 #free tiles
    a1 = score/(div*(16-(data == 0).sum()))
    a2 = score/div if data[0][0]>=data[1][0]>=data[2][0] else 0  #left vert.1 monotone
    a3 = score/div if data[0][0]>=data[0][1]>=data[0][2]>=data[0][3] else -score/50 #top horz. monotone.
    a4 = score/div if data[0][3] >= data[1][3] and data[1][3] >= data[1][2] else -score/30 #1to2 rightop corner monotone
    a5 = 2*score/div if data.max() == data[0][0] else -3*score #max at top left.
    a6 = score/div if data[0][1] >= data[1][1] >= data[2][1] else -score/3 #vert 2 mono
    a7 = score/div if data[0][2] >= data[1][2] >= data[2][2] else -score/20  #vert 3 mono
    a8 = score/div if data[2][2] <= data[1][2] else -score/20
    
"""

    

