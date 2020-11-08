from random import choice
from copy import deepcopy


class peon:
    def __init__(self, color, ordinal):
        self.color = color
        self.ordinal = ordinal
        self.id = color + str(ordinal)
        self.dir = self.dir()

    def dir(self):
        """returns direction as positive or negative unit (int)"""
        if self.color in {'g', ' '}:
            return 1
        elif self.color == 'b':
            return -1

    # minor hack: giving the blank peon non-zero direction. since there's only one blank peon
    # we won't need to make special case for it and it won't find another blank peon it that direction.

    def place(self, bord):
        """retruns the the index (int) of the peon on the bord from grey side to black side
        bord is assumed to be either board object or a list (it's self.val)"""
        if type(bord) is board:
            bord = bord.val
        return bord.index(self)

    def is_step(self, bord):
        """returns boolean value of is it possible for the peon to move one space"""
        bord = bord.val
        place = bord.index(self)
        try:
            pl = place + self.dir  # a place one step to the left or to the right
        except IndexError:
            return False
        back = bord[pl].color == ' '
        return back

    def is_jump(self, bord):
        """returns boolean value of is it possible for the peon jump over one opposite peon"""
        bord = bord.val
        place = bord.index(self)
        try:
            pl1 = place + self.dir
            pl2 = pl1 + self.dir
        except IndexError:
            return False
        back = bord[pl1].dir == -self.dir and bord[pl2].color == ' '
        return back


class board:
    def __init__(self, call=None):
        if call is None:
            call = [peon('g', i) for i in range(4)]
            call.append(peon(' ', 4))
            call.extend([peon('b', i + 5) for i in range(4)])
        self.val = call

    def expose(self):
        """returns human readable list of unique peons"""
        return [p.id for p in self.val]

    def score(self):
        back = 0
        for p in self.val:
            point = p.place(self)
            if p.color == 'b':
                point = len(self.val) - point - 1
            elif p.color == ' ':
                point = 0
            back += point
        return back


def list_moves(bord: board):
    """returns list of possible moves. each move formated as
    a pair of a peon object, a string for kind of move,
    and an int for the score of the move"""
    movi = []
    for p in bord.val:
        if p.color == ' ':
            continue
        if p.is_step(bord):
            movi.append([p, 'step'])
        if p.is_jump(bord):
            movi.append([p, 'jump'])
    movi = movi_score(movi, bord)
    return movi

# skipping blank peon move listing fixes IndexError in this function in the endgame.
# it might make prior blank direction hack unnecesary.


def movi_score(movi, bord):
    """take a list of moves without a score and adds a score"""
    back = []
    for mv in movi:
        consequnce = move(bord, mv[0], mv[1])
        score = consequnce.score()
        mv = (mv[0], mv[1], score)
        back.append(mv)
    return back


def distance(kind):
    """returns int value for each kind of move"""
    if kind == 'jump':
        return 2
    elif kind == 'step':
        return 1
    else:
        raise ValueError


def move(bord, p, kind):
    """returns a new board object repesenting the state after the move is taken"""
    # deepcopy is used to let us to look ahead at future boards without changing the current one
    bord = deepcopy(bord.val)
    place = bord.index(p)
    bord[place + distance(kind) * p.dir] = p
    bord[place] = peon(' ', 4)
    return board(bord)


def Game():
    bord = board()
    cond = True
    print(bord.expose())
    while cond:
        movi = list_moves(bord)
        try:
            ch = random_choice(movi)
            bord = move(bord, ch[0], ch[1])
        except IndexError:
            cond = False
        print(bord.expose())
        print(bord.score())


def random_choice(movi):
    return choice(movi)


def single_max_choice(movi):
    scori = [move[2] for move in movi]
    best = max(scori)
    back = movi[scori.index(best)]
    return back




Game()

"""
print(expose_bord(bord))
joe = [i.is_step() for i in bord]
print(joe)
"""
