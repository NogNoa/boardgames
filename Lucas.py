from random import choice


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
        elif self.color is 'b':
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
        back = bord[pl].color is ' '
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
        back = bord[pl1].dir is -self.dir and bord[pl2].color is ' '
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
    """returns list of possible moves. each move formated as a pair of a peon object and a string for kind of move"""
    movi = []
    for p in bord.val:
        if p.color == ' ':
            continue
        if p.is_step(bord):
            movi.append((p, 'step'))
        if p.is_jump(bord):
            movi.append((p, 'jump'))
    return movi

# skipping blank peon move listing fixes IndexError in this function in the endgame.
# it might make prior blank direction hack unnecesary.


def distance(kind):
    """returns int value for each kind of move"""
    if kind is 'jump':
        return 2
    elif kind is 'step':
        return 1
    else:
        raise ValueError


def move(bord, p, kind):
    """returns a new board object repesenting the state after the move is taken"""
    bord = bord.val
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
            ch = random_move(movi)
            bord = move(bord, ch[0], ch[1])
        except IndexError:
            cond = False
        print(bord.expose())
        print(bord.score())


def random_move(movi):
    return choice(movi)

def move_score(movi,bord):
    back = []
    for move in movi:
        consequnce = move(bord, move[0], move[1])
        score = consequnce.score()
        move = tuple(list(move).append(score))
        back.append(move)
    return back


Game()

"""
print(expose_bord(bord))
joe = [i.is_step() for i in bord]
print(joe)
"""
