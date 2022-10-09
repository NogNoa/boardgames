from copy import deepcopy
import random as rnd

from typing import Tuple, Dict, List, Callable


class Peon:
    def __init__(self, color: str, ordinal: int):
        self.color = color
        self.id = color + str(ordinal)
        self.dir = self.dir(color)

    def __str__(self):
        return self.id

    def __repr__(self):
        return self.id

    @staticmethod
    def dir(color):
        """Returns direction as positive or negative unit (int)"""
        return {'g': 1, ' ': 0, 'b': -1}[color]

    def place(self, order: List) -> int:
        """Retruns the index (int) of a peon on the bord from grey side to black side."""
        return order.index(self.id)

    def dest(self, order: List, kind: str):
        """Returns an empty place in which the peon can land"""
        dist = {"jump": 2, "step": 1}[kind]
        dest_ind = self.place(order) + dist * self.dir
        # a place one or two steps to the left or to the right.
        if not 0 <= dest_ind < len(order):
            return None
        else:
            return order[dest_ind]

    def is_move(self, order: List, kind: str) -> bool:
        """Returns whether it's possible for a peon to move one space for a step or two for a jump."""
        dest = self.dest(order, kind)
        return dest is not None and dest[0] == ' '


class EmptySpace(Peon):
    def __init__(self, ordinal: int):
        super().__init__(' ', ordinal)

    @staticmethod
    def is_move(*_) -> bool:
        return False

    @staticmethod
    def dest(*_):
        return None


class Board:
    def __init__(self, nmr_side, nmr_emp):
        peoni = [Peon('g', i) for i in range(nmr_side)]
        peoni.extend([(EmptySpace(i + nmr_side)) for i in range(nmr_emp)])
        peoni.extend([Peon('b', i + nmr_side + nmr_emp) for i in range(nmr_side)])
        self.order = [p.id for p in peoni]
        self.cntnt = {p.id: p for p in peoni}

    def __getitem__(self, i: int) -> str:
        return self.order[i]

    def __len__(self):
        return len(self.order)

    def __str__(self):
        """Returns human readable list of unique peons"""
        return str(self.order)

    def peon_find(self, pid):
        try:
            return self.cntnt[pid]
        except KeyError:
            return None

    def after_move(self, mov: Dict[str, any]) -> list[str]:
        """Returns a new board order repesenting the state after the move is taken."""
        # deepcopy is used to let us look ahead at future boards without changing the current one.
        p, kind = mov["peon"], mov["kind"]
        n_order = deepcopy(self.order)
        emp = self.peon_find(p.dest(self.order, kind))
        n_order[emp.place(self.order)] = p.id
        n_order[p.place(self.order)] = emp.id
        return n_order

    def list_moves(self) -> list[Dict[str, any]]:
        """Returns list of possible moves. Each move formated as
        a pair of peon objects, and a string for the kind of move."""
        movi = []
        for p in self:
            p = self.peon_find(p)
            if p.color == ' ':
                continue
            for k in {"step", "jump"}:
                if p.is_move(self.order, k):
                    movi.append({'peon': p, 'kind': k})
        return movi

    # skipping blank peon move listing fixes IndexError in this function in the endgame.
    # it might make prior blank direction hack unnecessary.


def adv_scr(order: list[str]) -> int:
    back = 0
    for i, p in enumerate(order):
        point = i
        if p[0] == 'b':
            point = len(order) - point - 1
        elif p[0] == ' ':
            point = 0
        back += point
    return back


def movi_score(movi: list[Dict[str, any]], bord: Board, scrfunc: Callable) -> list[int]:
    """Take a list of moves without a score and adds a score."""
    scori = []
    for mov in movi:
        consequnce = bord.after_move(mov)
        scr = scrfunc(consequnce)
        scori.append(scr)
    return scori


def empty_center_scr(consq: list[str]) -> int:
    scr = 0
    cntr = len(consq) / 2
    for i, p in enumerate(consq):
        if p[0] == ' ':
            scr += cntr - abs(cntr - i)
    return scr


"""def first_scr(consq: list[str], first: bool) -> int:
    return 16 * first"""


def random_scr(consq: list[str]) -> int:
    return int(rnd.random() * len(consq))


def winscore(lng, nmr_side):
    return (lng * 2 - nmr_side - 1) * nmr_side


class NoMoveError(Exception):
    pass


def game(choice_args=("interactive",), nmr_side=4, nmr_emp=2):
    bord = Board(nmr_side, nmr_emp)
    print(bord)
    choice_fun = choice_find(choice_args)
    while True:
        movi = bord.list_moves()
        try:
            ch = choice_fun(movi, bord)
            bord.order = bord.after_move(ch)
            print(bord)
            if debug: print(adv_scr(bord.order))
        except (IndexError, NoMoveError):
            if adv_scr(bord.order) == winscore(len(bord), nmr_side):
                print("You've done did it Chemp!")
            break


def choice_find(choice_argi: Tuple[str]):
    if len(choice_argi) == 1:
        if choice_argi[0] == "interactive":
            return interactive_choice
        elif choice_argi[0] == "random":
            return random_choice
        else:
            scr_fun = eval(f"{choice_argi[0]}_scr")
            return single_pref_choice(scr_fun)
    else:
        scr_fun1 = eval(f"{choice_argi[0]}_scr")
        scr_fun2 = eval(f"{choice_argi[1]}_scr")
        return two_pref_choice(scr_fun1, scr_fun2)


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


def first_max_choice(movi: list[Dict[str, any]], bord: Board, scr_fun=adv_scr) -> Dict[str, any]:
    if not movi:
        raise NoMoveError
    scori = movi_score(movi, bord, scr_fun)
    best = max(scori)
    back = movi[scori.index(best)]
    return back


@choice
def single_pref_choice(scr_fun):
    def general_1pref_choice(movi: list[Dict[str, any]], bord: Board) -> list[int]:
        scori = movi_score(movi, bord, scr_fun)
        best = max(scori)
        return [pl for pl, scr in enumerate(scori) if scr == best]

    return general_1pref_choice


@choice
def two_pref_choice(scr_fun_1, scr_fun_2):
    def general_2pref_choice(movi: list[Dict[str, any]], bord: Board, ) -> list[int]:
        scori_1 = movi_score(movi, bord, scr_fun_1)
        scori_2 = movi_score(movi, bord, scr_fun_2)
        max_1 = max(scori_1)
        besti = [scr if scori_1[pl] == max_1 else 0 for pl, scr in enumerate(scori_2)]
        best_of_both = max(besti)
        return [pl for pl, scr in enumerate(besti) if scr == best_of_both]

    return general_2pref_choice


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

debug = False
if __name__ == "__main__":
    def main():
        import argparse
        global debug

        choices = {"random", "first", "emp_center", "interactive", "adv"}
        parser = argparse.ArgumentParser(
            description=f"A game of lucas. you can choose an algorithm or play interactively: {choices}")
        parser.add_argument('choice', metavar="C", nargs="*", help="Algorithm to decide the moves")
        parser.add_argument("-p", help="Number of peons on each side", default=4)
        parser.add_argument("-e", help="Number of empty spaces in the middle", default=2)
        parser.add_argument("-d", help="Turn on debug mode", action="store_true", )
        args = parser.parse_args()
        debug = args.d

        if not set(args.choice).issubset(choices):
            print("Please enter a valid decision algorithm:\n\t", str(choices)[1:-1])
            exit(0)
        args.choice = tuple(args.choice) if args.choice else ("interactive",)
        game(args.choice, 4, 2)


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
#  rebust AI

# Done:
#  Either incorporate content into board or make it just be a plain list.
#  The interactive function is conditioned wrong. Rethink.

# don't:
# make generic choice function, that accept score functions, and random.
# obviously doesn't include interactive choice.

# N/A
# make empty peon less object and regular more?
