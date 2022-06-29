from copy import deepcopy
import random as rnd


class Board:
    class Peon:
        def __init__(self, color: str, ordinal: int, bord):
            self.color = color
            self.id = color + str(ordinal)
            self.bord = bord
            self.dir = {'g': 1, ' ': 0, 'b': -1}[color]

        def __str__(self):
            return self.id

        def __repr__(self):
            return self.id

        @property
        def place(self) -> int:
            return self.bord.place(self.id)

        def dest(self, kind: str):
            dist = {"jump": 2, "step": 1}[kind]
            try:
                dest_id = self.bord[self.place + dist * self.dir]
                # a place one or two steps to the left or to the right
                return dest_id
            except IndexError:
                return None

        def is_move(self, kind: str) -> bool:
            """Returns boolean value of is it possible for a peon to move one space for step or two for jump"""
            dest = self.dest(kind)
            return dest is not None and dest[0] == ' '

    class EmptySpace(Peon):
        def __init__(self, ordinal: int):
            super().__init__(' ', ordinal)

        def is_move(self, _) -> bool:
            return False

    def __init__(self, nmr_side, nmr_emp):
        peoni = [Board.Peon('g', i, self) for i in range(nmr_side)]
        peoni.extend([(Board.EmptySpace(i + nmr_side)) for i in range(nmr_emp)])
        peoni.extend([Board.Peon('b', i + nmr_side + nmr_emp, self) for i in range(nmr_side)])
        self.order = [p.id for p in peoni]
        self.cntnt = {p.id: p for p in peoni}

    def __getitem__(self, i: int) -> str:
        return self.order[i]

    def __len__(self):
        return len(self.order)

    def __str__(self):
        """returns human readable list of unique peons"""
        return str(self.order)

    def place(self, p_id: str) -> int:
        """Retruns the index (int) of a peon on the bord from grey side to black side"""
        return self.order.index(p_id)

    def peon_find(self, pid):
        try:
            return self.cntnt[pid]
        except KeyError:
            return None

    def list_moves(self) -> list[dict[str, any]]:
        """Returns list of possible moves. Each move formated as
        a pair of a peon object, a string for kind of move,
        and an int for the score of the move."""
        movi = []
        for p in self:
            p = self.peon_find(p)
            if p.color == ' ':
                continue
            for k in {"step", "jump"}:
                if p.is_move(k):
                    movi.append({'peon': p, 'kind': k})
        return movi

    # Skipping blank peon move listing fixes IndexError in this function in the endgame.
    # It might make prior blank direction hack unnecessary.

    def after_move(self, mov: dict[str, any]) -> list[str]:
        """Returns a new board object repesenting the state after the move is taken"""
        # deepcopy is used to let us look ahead at future boards without changing the current one
        p, kind = mov["peon"], mov["kind"]
        n_bord = deepcopy(self.order)
        place = self.order.index(p.id)
        emp = self.peon_find(p.dest(kind))
        n_bord[emp.place] = p.id
        n_bord[place] = emp.id
        return n_bord


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


def movi_score(movi: list[dict[str:]], bord: Board, scrfunc) -> list[int]:
    """Take a list of moves without a score and adds a score"""
    scori = []
    for mov in movi:
        consequnce = bord.after_move(mov)
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


def winscore(lng, nmr_side):
    return (lng * 2 - nmr_side - 1) * nmr_side


def game(choice_fun, nmr_side=4, nmr_emp=2):
    bord = Board(nmr_side, nmr_emp)
    print(bord)
    cont = True
    while cont:
        movi = bord.list_moves()
        try:
            ch = eval(f"{choice_fun}_choice(movi, bord)")
            bord.order = bord.after_move(ch)
            print(bord)
            if debug: print(score(bord.order))
        except IndexError:
            if score(bord.order) == winscore(len(bord), nmr_side):
                print("You've done did it Chemp!")
            cont = False


def random_choice(movi: list[dict[str:]], _, __) -> dict[str, any]:
    return rnd.choice(movi)


def first_max_choice(movi: list[dict[str:]], bord: Board, _) -> dict[str, any]:
    if not movi:
        raise IndexError
    scori = movi_score(movi, bord, score)
    best = max(scori)
    back = movi[scori.index(best)]
    return back


def rand_max_choice(movi: list[dict[str:]], bord: Board, _) -> dict[str, any]:
    if not movi:
        raise IndexError
    scori = movi_score(movi, bord, score)
    best = max(scori)
    besti = [pl for pl, scr in enumerate(scori) if scr == best]
    back = movi[rnd.choice(besti)]
    return back


def emp_center_choice(movi: list[dict[str:]], bord: Board, _) -> dict[str, any]:
    if not movi:
        raise IndexError
    scori = movi_score(movi, bord, emp_center_scr)
    best = max(scori)
    besti = [pl for pl, scr in enumerate(scori) if scr == best]
    back = movi[rnd.choice(besti)]
    return back


def center_max_choice(movi: list[dict[str:]], bord: Board, _) -> dict[str, any]:
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


def max_center_choice(movi: list[dict[str:]], bord: Board, _) -> dict[str, any]:
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


def interactive_choice(movi: list[dict[str:]], bord: Board) -> dict[str, any]:
    if not movi:
        raise IndexError
    hlp = \
        """A valid move is the name of a paon, followed by 's' or "step" for a move of 1 space or followed by 'j' or 
"jump" for a move of 2 spaces. Type 'q', "quit" or "exit" to exit the program.
        """
    call = input("Move?\n > ").lower()
    call = call.split()
    if len(call) >= 1:
        if call[0] in {"h", "help"}:
            print(hlp)
            return interactive_choice(movi, bord)
        elif call[0] == "movi":
            print(movi)  # for debugging
            return interactive_choice(movi, bord)
        elif call[0] in {'q', "quit", "exit"}:
            print("Be seeing you.")
            raise IndexError
        else:
            mov = {"peon": bord.peon_find(call[0])}
    else:
        mov = None
    if len(call) >= 2:
        mov["kind"] = call[1]
        if mov["kind"] in {'j', 's'}:
            mov["kind"] = {'j': "jump", "s": "step"}[mov["kind"]]
        else:
            mov["kind"] = call[1]
    if mov in movi:
        return mov
    else:
        print('please enter a vlid move.  If you need help just enter \'h\' or "help".')
        return interactive_choice(movi, bord)


# priority in function names from right to left

if __name__ == "__main__":
    def main():
        import argparse
        global debug

        choices = {"max_center", "random", "first_max", "rand_max", "emp_center", "center_max", "interactive"}
        parser = argparse.ArgumentParser(
            description=f"a game of lucas. you can choose an algorithm or play interactively: {choices}")
        parser.add_argument('choice', metavar="C", nargs="?", default="interactive",
                            help="Algorithm to decide the moves")
        parser.add_argument("-d", help="turn on debug mode", action="store_true", )
        args = parser.parse_args()
        debug = args.d

        if args.choice not in choices:
            print("please enter a valid decision algorithm:\n\t", str(choices)[1:-1])
            exit(0)
        game(args.choice, 4, 2)


    debug = None
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
#  the interactive function is conditioned wrong. rethink.
#  make generic choice function, that accept score functions, and random.
#   obviously doesn't include interactive choice
#  make empty peon less object and regular more?
