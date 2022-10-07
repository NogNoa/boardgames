from copy import deepcopy
import random as rnd

from typing import Tuple, Dict, Callable


class Peon:
    def __init__(self, color: str, ordinal: int, bord):
        self.color = color
        self.id = color + str(ordinal)
        self.dir = self.dir(color)
        self._bord = bord

    def __str__(self):
        return self.id

    def __repr__(self):
        return self.id

    @staticmethod
    def dir(color):
        """Returns direction as positive or negative unit (int)"""
        return {'g': 1, ' ': 0, 'b': -1}[color]

@property
    def place(self) -> int:
        return self._bord.place(self.id)

    def dest(self, kind: str):
        dist = {"jump": 2, "step": 1}[kind]
        dest_ind = self.place + dist * self.dir
        # a place one or two steps to the left or to the right.
        if not 0 <= dest_ind < len(self._bord):
            return None
        else:
            return self._bord[dest_ind]

    def is_move(self, kind: str) -> bool:
        """Returns boolean value of is it possible for a peon to move one space for a step or two for a jump."""
        dest = self.dest(kind)
        return dest is not None and dest[0] == ' '


class EmptySpace(Peon):
    def __init__(self, ordinal: int, bord):
        super().__init__(' ', ordinal, bord)

    @staticmethod
    def is_move(*_) -> bool:
        return False


class Board:
    def __init__(self, nmr_side, nmr_emp):
        peoni = [Peon('g', i, self) for i in range(nmr_side)]
        peoni.extend([(EmptySpace(i + nmr_side, self)) for i in range(nmr_emp)])
        peoni.extend([Peon('b', i + nmr_side + nmr_emp, self) for i in range(nmr_side)])
        self.order = [p.id for p in peoni]
        self.cntnt = {p.id: p for p in peoni}

    def __getitem__(self, i: int) -> str:
        return self.order[i]

    def __len__(self):
        return len(self.order)

    def __str__(self):
        """Returns human readable list of unique peons"""
        return str(self.order)

    def place(self, p_id: str) -> int:
        """Retruns the index (int) of a peon on the bord from grey side to black side."""
        return self.order.index(p_id)

    def peon_find(self, pid):
        try:
            return self.cntnt[pid]
        except KeyError:
            return None

    def after_move(self, mov: Dict[str:Peon, str:str]) -> list[str]:
        """returns a new board order repesenting the state after the move is taken"""
        # deepcopy is used to let us look ahead at future boards without changing the current one
        p, kind = mov["peon"], mov["kind"]
        n_order = deepcopy(self.order)
        emp = self.peon_find(p.dest(kind))
        n_order[emp.place] = p.id
        n_order[p.place] = emp.id
        return n_order

    def list_moves(self) -> list[Dict[str:Peon, str:str]]:
        """Returns list of possible moves. each move formated as
        a pair of a peon objects, and a string for the kind of move."""
        movi = []
        for p in self:
            p = self.peon_find(p)
            if p.color == ' ':
                continue
            for k in {"step", "jump"}:
                if p.is_move(k):
                    movi.append({'peon': p, 'kind': k})
        return movi

    # skipping blank peon move listing fixes IndexError in this function in the endgame.
    # it might make prior blank direction hack unnecessary.


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


def movi_score(movi: list[dict[str:]], bord: Board, scrfunc: Callable) -> list[int]:
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


def winscore(lng, nmr_side):
    return (lng * 2 - nmr_side - 1) * nmr_side


class NoMoveError(Exception):
    pass


def game(choice_fun="interactive", nmr_side=4, nmr_emp=2):
    bord = Board(nmr_side, nmr_emp)
    print(bord)
    choice_fun = eval(f"{choice_fun}_choice")
    while True:
        movi = bord.list_moves()
        try:
            ch = choice_fun(movi, bord)
            bord.order = bord.after_move(ch)
            print(bord)
            if debug: print(score(bord.order))
        except (IndexError, NoMoveError):
            if score(bord.order) == winscore(len(bord), nmr_side):
                print("You've done did it Chemp!")
            break


def choice_find(*choice_argi: Tuple[str]):
    if len(choice_argi) == 1:
        if choice_argi[0] == "interactive":
            return interactive_choice
        elif choice_argi[0] == "random":
            return random_choice
        else:
            scr_fun = eval(f"{choice_argi[0]}_scr")
            return single_pref_choice
    else:
        return two_pref_choice


def random_choice(movi: list[Dict[str, any]]) -> Dict[str, any]:
    return rnd.choice(movi)


def choice(ch_fun):
    def general_choice(movi, *args, **kwargs) -> Dict[str, any]:
        if not movi:
            raise NoMoveError
        besti = ch_fun(movi, *args, **kwargs)
        back = movi[rnd.choice(besti)]
        return back

    return general_choice


def first_max_choice(movi: list[Dict[str, any]], bord: Board, scr_fun=score) -> Dict[str, any]:
    if not movi:
        raise NoMoveError
    scori = movi_score(movi, bord, scr_fun)
    best = max(scori)
    back = movi[scori.index(best)]
    return back


@choice
def single_pref_choice(movi: list[Dict[str, any]], bord: Board, scr_fun) -> list[int]:
    scori = movi_score(movi, bord, scr_fun)
    best = max(scori)
    return [pl for pl, scr in enumerate(scori) if scr == best]


@choice
def two_pref_choice(movi: list[Dict[str, any]], bord: Board, scr_fun_1, scr_fun_2) -> list[int]:
    scori_1 = movi_score(movi, bord, scr_fun_1)
    scori_2 = movi_score(movi, bord, scr_fun_2)
    max_1 = max(scori_1)
    besti = [scr if scori_1[pl] == max_1 else 0 for pl, scr in enumerate(scori_2)]
    best_of_both = max(besti)
    return [pl for pl, scr in enumerate(besti) if scr == best_of_both]


"""def keep_options_choice(movi: list[Dict], bord: Board, pf: Content) -> Dict:
    scori = movi_score(movi, bord, movi_count)
"""


def interactive_choice(movi: list[Dict[str, any]], bord: Board) -> Dict[str, any]:
    if not movi:
        raise NoMoveError
    hlp = \
        """A valid move is the name of a paon, followed by 's' or "step" for a move of 1 space or followed by 'j' or 
"jump" for a move of 2 spaces. Type 'q', "quit" or "exit" to exit the program.
        """
    while True:
        call = input("Move?\n > ").lower()
        call = call.split()
        if call:
            if call[0] in {"h", "help"}:
                print(hlp)
            elif call[0] in dir():  # bord hlp movi call
                print(eval(call[0]))  # for debugging
            elif call[0] in {'q', "quit", "exit"}:
                print("Be seeing you.")
                raise NoMoveError
            else:
                break
    mov = {"peon": call[0] if call else '', "kind": call[1] if len(call) >= 2 else ''}
    mov["peon"] = bord.peon_find(mov["peon"])
    if mov["kind"] in {'j', 's'}:
        mov["kind"] = {'j': "jump", "s": "step"}[mov["kind"]]
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
            description=f"A game of lucas. you can choose an algorithm or play interactively: {choices}")
        parser.add_argument('choice', metavar="C", nargs="?", default="interactive",
                            help="Algorithm to decide the moves")
        parser.add_argument("-p", help="Number of peons on each side", default=4)
        parser.add_argument("-e", help="Number of empty spaces in the middle", default=2)
        parser.add_argument("-d", help="Turn on debug mode", action="store_true", )
        args = parser.parse_args()
        debug = args.d

        if args.choice not in choices:
            print("Please enter a valid decision algorithm:\n\t", str(choices)[1:-1])
            exit(0)
        game(args.choice, 4, 2)


    debug = None
    main()

"""
The winning strategy is basicaly to identify dead blocks and avoid making them.
a dead block is a block of peons, none of which could move, no matter of free spaces
there is around the block.

we don't need to take the ends of the board into account, in fact we have to desregard them.
a block in the opposite end is fine this is the desired endstate of those peons, 
and if the board didn't end those peons could have moved.

good euristics are to seek to order the peons alternatingly re: their color; and to have and use "ladders".
a ladder is when say a black peon has in front of him a patern "grey, emp, grey, emp" and using the ladder is jumping 
over the two grey peons.
But we don't necessarily need to add them to the AI.
"""

# todo:
#  generic choice functions (glue code)

# Done:
#  Either incorporate content into board or make it just be a plain list.
#  The interactive function is conditioned wrong. Rethink.

# don't:
# make generic choice function, that accept score functions, and random.
# obviously doesn't include interactive choice.

# N/A
# make empty peon less object and regular more?

