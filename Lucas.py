from copy import deepcopy
import random as rnd


class Peon:
    def __init__(self, color: str, ordinal: int):
        self.color = color
        self.id = color + str(ordinal)
        self.bord = self.peon_find = None

    def set_contacts(self, bord, pfind):
        self.bord = bord
        self.peon_find = pfind

    def __str__(self):
        return self.id

    def __repr__(self):
        return self.id

    @property
    def dir(self):
        """returns direction as positive or negative unit (int)"""
        dirdic = {'g': 1, ' ': 0, 'b': -1}
        try:
            return dirdic[self.color]
        except KeyError:
            return None

    @property
    def place(self) -> int:
        return self.bord.place(self.id)

    def dest(self, kind: str):
        dist = {"jump": 2, "step": 1}[kind]
        try:
            dest_id = self.bord[self.place + dist * self.dir]
            # a place one or two steps to the left or to the right
            return self.peon_find(dest_id)
        except IndexError:
            return None

    def is_move(self, kind: str) -> bool:
        """returns boolean value of is it possible for a peon to move one space for step or two for jump"""
        dest = self.dest(kind)
        return dest is not None and dest.color == ' '


class EmptySpace(Peon):
    def __init__(self, ordinal: int):
        super().__init__(' ', ordinal)

    def is_move(self, _) -> bool:
        return False


class Content:
    def __init__(self, peoni: set):
        self.val = {p.id: p for p in peoni}

    def __call__(self, pid: str):
        try:
            return self.val[pid]
        except KeyError:
            return None


class Board:
    def __init__(self, order: list[str]):
        self.order = order

    def __getitem__(self, i: int) -> str:
        return self.order[i]

    def __str__(self):
        """returns human readable list of unique peons"""
        return str(self.order)

    def place(self, p_id: str) -> int:
        """retruns the index (int) of a peon on the bord from grey side to black side"""
        return self.order.index(p_id)

    def __len__(self):
        return len(self.order)


def score(order: list[str]) -> int:
    back = 0
    for i, p in enumerate(order):
        point = i
        if p[0] == 'b':
            point = len(order) - point - 1
        elif p[0] == ' ':
            point = 0
        back += point
    return back


def list_moves(bord: Board, peon_find: Content) -> list[dict]:
    """returns list of possible moves. each move formated as
    a pair of a peon object, a string for kind of move,
    and an int for the score of the move"""
    movi = []
    for p in bord:
        p = peon_find(p)
        if p.color == ' ':
            continue
        for k in {"step", "jump"}:
            if p.is_move(k):
                movi.append({'peon': p, 'kind': k})
    return movi


# skipping blank peon move listing fixes IndexError in this function in the endgame.
# it might make prior blank direction hack unnecessary.


def movi_score(movi: list, bord: Board, scrfunc) -> list[int]:
    """take a list of moves without a score and adds a score"""
    scori = []
    for mv in movi:
        consequnce = move(bord, mv)
        scr = scrfunc(consequnce)
        scori.append(scr)
    return scori


def emp_center_scr(consq: list[str]) -> int:
    scr = 0
    cntr = len(consq) / 2
    for i, p in enumerate(consq):
        if p[0] == ' ':
            scr += cntr - abs(cntr - i)
    return scr


"""def movi_count(consq: list[str], pf: Content) -> int:
    movi = list_moves(Board(consq), pf)
    return len(movi)
"""


def move(bord: Board, mv: dict) -> list[str]:
    """returns a new board object repesenting the state after the move is taken"""
    # deepcopy is used to let us look ahead at future boards without changing the current one
    p, kind = mv["peon"], mv["kind"]
    n_bord = deepcopy(bord.order)
    place = bord.order.index(p.id)
    emp = p.dest(kind)
    n_bord[emp.place] = p.id
    n_bord[place] = emp.id
    return n_bord


def winscore(lng, nmr_side):
    return (lng * 2 - nmr_side - 1) * nmr_side


def game(choice_fun="random", nmr_side=4, nmr_emp=2, dbg=False):
    openning = [Peon('g', i) for i in range(nmr_side)]
    openning.extend([(EmptySpace(i + nmr_side)) for i in range(nmr_emp)])
    openning.extend([Peon('b', i + nmr_side + nmr_emp) for i in range(nmr_side)])
    cntnt = Content(set(openning))
    openids = [p.id for p in openning]
    bord = Board(openids)
    for p in openning:
        p.set_contacts(bord, cntnt)
    print(bord)
    cont = True
    while cont:
        movi = list_moves(bord, cntnt)
        try:
            ch = eval(f"{choice_fun}_choice(movi, bord, cntnt)")
            bord.order = move(bord, ch)
            print(bord)
            if dbg: print(score(bord.order))
        except IndexError:
            if score(bord.order) == winscore(len(bord), nmr_side):
                print("You've done did it Chemp!")
            cont = False


def random_choice(movi: list[dict], _, __) -> dict:
    return rnd.choice(movi)


def first_max_choice(movi: list[dict], bord: Board, _) -> dict:
    if not movi:
        raise IndexError
    scori = movi_score(movi, bord, score)
    best = max(scori)
    back = movi[scori.index(best)]
    return back


def rand_max_choice(movi: list[dict], bord: Board, _) -> dict:
    if not movi:
        raise IndexError
    scori = movi_score(movi, bord, score)
    best = max(scori)
    besti = [pl for pl, scr in enumerate(scori) if scr == best]
    back = movi[rnd.choice(besti)]
    return back


def emp_center_choice(movi: list[dict], bord: Board, _) -> dict:
    if not movi:
        raise IndexError
    scori = movi_score(movi, bord, emp_center_scr)
    best = max(scori)
    besti = [pl for pl, scr in enumerate(scori) if scr == best]
    back = movi[rnd.choice(besti)]
    return back


def center_max_choice(movi: list[dict], bord: Board, _) -> dict:
    if not movi:
        raise IndexError
    maxi = movi_score(movi, bord, score)
    centri = movi_score(movi, bord, emp_center_scr)
    best_score = max(maxi)
    besti = [scr if maxi[pl] == best_score else 0 for pl, scr in enumerate(centri)]
    best_center = max(besti)
    besti = [pl for pl, scr in enumerate(besti) if scr == best_center]
    back = movi[rnd.choice(besti)]
    return back


def max_center_choice(movi: list[dict], bord: Board, _) -> dict:
    if not movi:
        raise IndexError
    maxi = movi_score(movi, bord, score)
    centri = movi_score(movi, bord, emp_center_scr)
    best_center = max(centri)
    besti = [scr if centri[pl] == best_center else 0 for pl, scr in enumerate(maxi)]
    best_score = max(besti)
    besti = [pl for pl, scr in enumerate(besti) if scr == best_score]
    back = movi[rnd.choice(besti)]
    return back


"""def keep_options_choice(movi: list[dict], bord: Board, pf: Content) -> dict:
    scori = movi_score(movi, bord, movi_count)
"""


def interactive_choice(movi: list[dict], bord: Board, peon_find: Content) -> dict:
    if not movi:
        raise IndexError
    hlp = """A valid move is the name of a paon, followed by 's' or "step" for a move of 1 space 
or followed by 'j' or "jump" for a move of 2 spaces. Type 'q', "quit" or "exit" to exit the program.
    """
    call = input("Move?\n > ").lower()
    call = call.split()
    if len(call) >= 1:
        if call[0] in {"h", "help"}:
            print(hlp)
            return interactive_choice(movi, bord, peon_find)
        elif call[0] == "movi":
            print(movi)  # for debuging
            return interactive_choice(movi, bord, peon_find)
        elif call[0] in {'q', "quit", "exit"}:
            print("Be seeing you.")
            raise IndexError
        else:
            move = {"peon": peon_find(call[0])}
    else:
        move = None
    if len(call) >= 2:
        move["kind"] = call[1]
        if move["kind"] in {'j', 's'}:
            move["kind"] = {'j': "jump", "s": "step"}[move["kind"]]
        else:
            move["kind"] = call[1]
    if move in movi:
        return move
    else:
        print('please enter a vlid move.  If you need help just enter \'h\' or "help".')
        return interactive_choice(movi, bord, peon_find)


# priority in function names from right to left

if __name__ == "__main__":
    def main():
        import argparse

        choices = {"max_center", "random", "first_max", "rand_max", "emp_center", "center_max", "interactive"}
        parser = argparse.ArgumentParser(
            description=f"a game of lucas. you can choose an algorithm or play interactively: {choices}")
        parser.add_argument('choice', metavar="C", help="Algorithm to decide the moves", default="random")
        parser.add_argument("-d", help="turn on debug mode", action="store_true", )
        args = parser.parse_args()

        if args.choice not in choices:
            print("please enter a valid decision algorithm:\n\t", str(choices)[1:-1])
            exit(0)
        game(args.choice, 4, 2, args.d)


    main()

"""
the winning strategy is basicaly to identify dead blocks and avoid making them.
a dead block is a block of peons, none of which could move, no matter of free spaces
there is around the block.

we don't need to take the ends of the board into account, in fact we have to desregard them.
a block in the opposite end is fine this is the desired endstate of those peons, 
and if the board didn't end those peons could have moved.

good euristics are to seek to order the peons alternatingly re: their color; and to have and use "ladders".
a ladder is when say a black peon has in front of him a patern "grey, emp, grey, emp" and using the ladder is jumping 
over the two grey peons.
But we don't necessarily need to add them to the AI
"""


# todo: either incorporate content into board or make it just be a plain list.

