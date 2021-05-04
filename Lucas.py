from random import choice
from copy import deepcopy


class Peon:
    def __init__(self, bord, color, ordinal):
        self.color = color
        self.ordinal = ordinal
        self.id = color + str(ordinal)
        self.dir = self.dir()
        self.bord = bord

    def dir(self):
        """returns direction as positive or negative unit (int)"""
        if self.color in {'g', ' '}:
            return 1
        elif self.color == 'b':
            return -1

    # minor hack: giving the blank peon non-zero direction. since there's only one blank peon
    # we won't need to make special case for it and it won't find another blank peon it that direction.

    def place(self):
        """retruns the the index (int) of the peon on the bord from grey side to black side"""
        return self.bord.place(self)


class Board:
    def __init__(self, call=None):
        if call is None:
            call = [Peon(self, 'g', i) for i in range(4)]
            call.append(Peon(self, ' ', 4))
            call.extend([Peon(self, 'b', i + 5) for i in range(4)])
        self.val = call

    def place(self, p: Peon):
        return self.val.index(p)

    def expose(self):
        """returns human readable list of unique peons"""
        return [p.id for p in self.val]

    def score(self):
        back = 0
        for p in self.val:
            point = self.place(p)
            if p.color == 'b':
                point = len(self.val) - point - 1
            elif p.color == ' ':
                point = 0
            back += point
        return back

    def is_step(self, p: Peon):
        try:
            pl = self.place(p) + p.dir  # a place one step to the left or to the right
        except IndexError:
            return False
        return self.val[pl].color == ' '

    def is_jump(self, p: Peon):
        pl0 = self.place(p)
        try:
            pl1 = pl0 + p.dir
            pl2 = pl1 + p.dir
        except IndexError:
            return False
        back = self.val[pl1].dir == p.dir and self.val[pl2].color == ' '


def list_moves(bord: Board):
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
# it might make prior blank direction hack unnecessary.


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
    bord[place] = Peon(' ', 4)
    return Board(bord)


def game():
    bord = Board()
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


game()

"""
print(expose_bord(bord))
joe = [i.is_step() for i in bord]
print(joe)
"""
