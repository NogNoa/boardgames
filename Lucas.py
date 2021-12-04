from copy import deepcopy
from random import choice


class Peon:
    def __init__(self, color, ordinal):
        self.color = color
        self.id = color + str(ordinal)
        self.dir = self.dir()
        self.bord = self.peon_find = None

    def set_contacts(self, bord: object, pfind):
        self.bord = bord
        self.peon_find = pfind

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
    # we won't need to make special case for it, and it won't find another blank peon in that direction.

    def place(self):
        return self.bord.place(self.id)

    def step_dest(self):
        return self.peon_find(self.bord.step_dest(self))

    def jump_dest(self):
        return self.peon_find(self.bord.jump_dest(self))

    def is_step(self) -> bool:
        """returns boolean value of is it possible for a peon to move one space"""
        step_dest = self.step_dest()
        return step_dest is not None and step_dest.color == ' '

    def is_jump(self) -> bool:
        """returns boolean value of is it possible for a peon jump over one peon"""
        jump_dest = self.jump_dest()
        return jump_dest is not None and jump_dest.color == ' '


class Content:
    def __init__(self, peoni: set):
        self.val = {p.id: p for p in peoni}

    def peon_find(self, pid: str):
        try:
            return self.val[pid]
        except KeyError:
            return None


class Board:
    def __init__(self, order: list):
        self.order = order

    def __getitem__(self, i):
        return self.order[i]

    def __str__(self):
        """returns human readable list of unique peons"""
        return str(self.order)

    def place(self, p_id: str):
        """retruns the index (int) of a peon on the bord from grey side to black side"""
        return self.order.index(p_id)

    def step_dest(self, p: Peon):
        try:
            dest_id = self.order[self.place(p.id) + p.dir]  # a place one step to the left or to the right
            return dest_id
        except IndexError:
            return None

    def jump_dest(self, p: Peon):
        try:
            dest_id = self.order[self.place(p.id) + p.dir * 2]  # a place two steps to the left or to the right
            return dest_id
        except IndexError:
            return None


def score(order):
    back = 0
    for i, p in enumerate(order):
        point = i
        if p[0] == 'b':
            point = len(order) - point - 1
        elif p[0] == ' ':
            point = 0
        back += point
    return back


def list_moves(bord: Board, cntnt: Content):
    """returns list of possible moves. each move formated as
    a pair of a peon object, a string for kind of move,
    and an int for the score of the move"""
    movi = []
    for p in bord:
        p = cntnt.peon_find(p)
        if p.color == ' ':
            continue
        if p.is_step():
            movi.append({'peon': p, 'kind': 'step'})
        if p.is_jump():
            movi.append({'peon': p, 'kind': 'jump'})
    return movi


# skipping blank peon move listing fixes IndexError in this function in the endgame.
# it might make prior blank direction hack unnecessary.


def movi_score(movi: list, bord: Board, scrfunc):
    """take a list of moves without a score and adds a score"""
    scori = []
    for mv in movi:
        consequnce = move(bord, mv["peon"], mv["kind"])
        scr = scrfunc(consequnce)
        scori.append(scr)
    return scori


def emp_center_scr(consq, empid=" 4"):
    emp_pl = consq.index(empid)
    scr = 4 - abs(4 - emp_pl)
    return scr


def distance(kind: str):
    """returns int value for each kind of move"""
    distdic = {"jump": 2, "step": 1}
    try:
        return distdic[kind]
    except KeyError:
        raise ValueError


def move(bord: Board, p: Peon, kind: str, empid=' 4'):
    """returns a new board object repesenting the state after the move is taken"""
    # deepcopy is used to let us look ahead at future boards without changing the current one
    n_bord = deepcopy(bord.order)
    place = bord.order.index(p.id)
    n_bord[place + distance(kind) * p.dir] = p.id
    n_bord[place] = empid
    return n_bord


def game(choice_fun="random", dbg=False):
    openning = [Peon('g', i) for i in range(4)]
    emp = (Peon(' ', 4))
    openning.append(emp)
    openning.extend([Peon('b', i + 5) for i in range(4)])
    cntnt = Content(set(openning))
    openids = [p.id for p in openning]
    bord = Board(openids)
    for p in openning:
        p.set_contacts(bord, cntnt.peon_find)
    print(bord)
    cont = True
    while cont:
        movi = list_moves(bord, cntnt)
        try:
            ch = eval(f"{choice_fun}_choice(movi, bord)")
            bord.order = move(bord, ch["peon"], ch["kind"])
            print(bord)
            if dbg: print(score(bord.order))
        except IndexError:
            cont = False


def random_choice(movi, _):
    return choice(movi)


def first_max_choice(movi, bord):
    if not movi:
        raise IndexError
    scori = movi_score(movi, bord, score)
    best = max(scori)
    back = movi[scori.index(best)]
    return back


def rand_max_choice(movi, bord):
    if not movi:
        raise IndexError
    scori = movi_score(movi, bord, score)
    best = max(scori)
    besti = [pl for pl, scr in enumerate(scori) if scr == best]
    back = movi[choice(besti)]
    return back


def emp_center_choice(movi, bord):
    if not movi:
        raise IndexError
    scori = movi_score(movi, bord, emp_center_scr)
    best = max(scori)
    besti = [pl for pl, scr in enumerate(scori) if scr == best]
    back = movi[choice(besti)]
    return back


def center_max_choice(movi, bord):
    if not movi:
        raise IndexError
    maxi = movi_score(movi, bord, score)
    centri = movi_score(movi, bord, emp_center_scr)
    best_score = max(maxi)
    besti = [scr if maxi[pl] == best_score else 0 for pl, scr in enumerate(centri)]
    best_center = max(besti)
    besti = [pl for pl, scr in enumerate(besti) if scr == best_center]
    back = movi[choice(besti)]
    return back


def max_center_choice(movi, bord):
    if not movi:
        raise IndexError
    maxi = movi_score(movi, bord, score)
    centri = movi_score(movi, bord, emp_center_scr)
    best_center = max(centri)
    besti = [scr if centri[pl] == best_center else 0 for pl, scr in enumerate(maxi)]
    best_score = max(besti)
    besti = [pl for pl, scr in enumerate(besti) if scr == best_score]
    back = movi[choice(besti)]
    return back


def interactive_choice(movi, bord):
    if not movi:
        raise IndexError
    hlp = """A valid move is the name of a paon, followed by "step" for a move of 1 or "jump" for a move of 2"""
    move = input("Move?\n > ").lower()
    move = move.split()
    if len(move) >= 2:
        move = {"peon": move[0], "kind": move[1]}
        if move["kind"] in {'j', 's'}:
            move["kind"] = {'j': "jump", "s": "step"}[move["kind"]]
    if move in movi:
        return move
    elif move[0] in {"h", "help"}:
        print(hlp)
        return interactive_choice(movi, bord)
    else:
        print('please enter a vlid move.  If you need help just enter "help".')
        return interactive_choice(movi, bord)


# priority in function names from right to left

if __name__ == "__main__":
    def main():
        import argparse

        parser = argparse.ArgumentParser()
        parser.add_argument('choice', metavar="C", help="Algorithm to decide the moves", default="random")
        parser.add_argument("-d", help="turn on debug mode", action="store_true", )
        args = parser.parse_args()
        choices = {"max_center", "random", "first_max", "rand_max", "emp_cent", "center_max", "interactive"}

        if args.choice not in choices:
            print("please enter a valid decision algorithm:\n\t", str(choices)[1:-1])
            exit(0)
        game(args.choice, args.d)


    main()

"""
print(expose_bord(bord))
joe = [i.is_step() for i in bord]
print(joe)
"""
