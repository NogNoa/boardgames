from copy import deepcopy
from random import choice


class Peon:
    def __init__(self, color, ordinal):
        self.color = color
        self.ordinal = ordinal
        self.id = color + str(ordinal)
        self.dir = self.dir()
        self.bord = None

    def set_bord(self, bord):
        self.bord = bord

    def __str__(self):
        return self.id

    def __repr__(self):
        return self.id

    def dir(self):
        """returns direction as positive or negative unit (int)"""
        dirdic = {'g': 1, ' ': 1, 'b': -1}
        try:
            return dirdic[self.color]
        except KeyError:
            return None

    # minor hack: giving the blank peon non-zero direction. since there's only one blank peon
    # we won't need to make special case for it and it won't find another blank peon in that direction.

    def place(self):
        return self.bord.place(self.id)

    def step_dest(self):
        return self.bord.step_dest(self)

    def jump_dest(self):
        return self.bord.jump_dest(self)

    def is_step(self) -> bool:
        """returns boolean value of is it possible for a peon to move one space"""
        step_dest = self.step_dest()
        return step_dest is not None and step_dest.color == ' '

    def is_jump(self) -> bool:
        """returns boolean value of is it possible for a peon jump over one peon"""
        jump_dest = self.jump_dest()
        return jump_dest is not None and jump_dest.color == ' '


class Board:
    def __init__(self, order: list, emp):
        self.cntnt = {}
        for p in order:
            self.cntnt[p.id] = p
        self.order = [p.id for p in order]
        self.emp = emp

    def __str__(self):
        """returns human readable list of unique peons"""
        return str(self.order)

    def place(self, p_id: str):
        """retruns the the index (int) of a peon on the bord from grey side to black side"""
        return self.order.index(p_id)

    def peon_order(self):
        return [self.cntnt[p] for p in self.order]

    def step_dest(self, p: Peon):
        try:
            dest_id = self.order[self.place(p.id) + p.dir]  # a place one step to the left or to the right
            return self.cntnt[dest_id]
        except IndexError:
            return None

    def jump_dest(self, p: Peon):
        try:
            dest_id = self.order[self.place(p.id) + p.dir * 2]  # a place two steps to the left or to the right
            return self.cntnt[dest_id]
        except IndexError:
            return None


def score(order):
    back = 0
    for p in order:
        point = p.place()
        if p.color == 'b':
            point = len(order) - point - 1
        elif p.color == ' ':
            point = 0
        back += point
    return back


def list_moves(bord: Board):
    """returns list of possible moves. each move formated as
    a pair of a peon object, a string for kind of move,
    and an int for the score of the move"""
    movi = []
    for p in bord.peon_order():
        if p.color == ' ':
            continue
        if p.is_step():
            movi.append({'peon': p, 'kind': 'step'})
        if p.is_jump():
            movi.append({'peon': p, 'kind': 'jump'})
    movi = movi_score(movi, bord)
    return movi


# skipping blank peon move listing fixes IndexError in this function in the endgame.
# it might make prior blank direction hack unnecessary.


def movi_score(movi, bord):
    """take a list of moves without a score and adds a score"""
    back = []
    for mv in movi:
        consequnce = move(bord, mv["peon"], mv["kind"])
        scr = score(consequnce)
        mv = (mv[0], mv[1], scr)
        back.append(mv)
    return back


def distance(kind):
    """returns int value for each kind of move"""
    distdic = {"jump": 2, "step": 1}
    try:
        return distdic[kind]
    except KeyError:
        raise ValueError


def move(bord, p, kind):
    """returns a new board object repesenting the state after the move is taken"""
    # deepcopy is used to let us to look ahead at future boards without changing the current one
    n_bord = deepcopy(bord.order)
    place = bord.order.index(p.id)
    n_bord[place + distance(kind) * p.dir] = p
    n_bord[place] = bord.emp
    return n_bord


def game():
    openning = [Peon('g', i) for i in range(4)]
    emp = (Peon(' ', 4))
    openning.append(emp)
    openning.extend([Peon('b', i + 5) for i in range(4)])
    bord = Board(openning, emp)
    for p in openning:
        p.set_bord(bord)
    print(bord)
    cont = True
    while cont:
        movi = list_moves(bord)
        try:
            ch = random_choice(movi)
            bord.order = move(bord, ch["peon"], ch["kind"])
        except IndexError:
            cont = False
        print(bord)
        print(score(bord.order))


def random_choice(movi):
    return choice(movi)


def single_max_choice(movi):
    scori = [mov[2] for mov in movi]
    best = max(scori)
    back = movi[scori.index(best)]
    return back


if __name__ == "__main__":
    game()

"""
print(expose_bord(bord))
joe = [i.is_step() for i in bord]
print(joe)
"""
# TODO: probably shouldn't create a new board in each move().
#  Or else, let it identify same peon on different future boards.
#  That's what the id is supposedly for.
#  something is wonky in the hierarchy
#  try opposite direction, get rid of Board object and make program more functional, with a list instead of Board.
#  and control decentralised in the hands of each Peon.
#  -
#  clear separation of work. Board is just a phone book to find other Peons,
#  the game function call the peons to actually make the moves, and update Board.
#  -
#  score does need to be a board method
