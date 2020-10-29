from random import choice


class peon:
    def __init__(self, color, ordinal):
        self.color = color
        self.ordinal = ordinal
        self.id = color + str(ordinal)
        self.dir = self.dir()

    def dir(self):
        if self.color in {'g', ' '}:
            return 1
        elif self.color is 'b':
            return -1

    # minor hack: giving the empty peon non-zero direction, since there's only one of it
    # means we won't need to make special case for it and it won't find another empty peon it that direction.

    def is_step(self):
        place = bord.index(self)
        try:
            pl = place + self.dir  # a place one step to the left or to the right
        except IndexError:
            return False
        back = bord[pl].color is ' '
        return back

    def is_jump(self):
        place = bord.index(self)
        try:
            pl1 = place + self.dir
            pl2 = pl1 + self.dir
        except IndexError:
            return False
        back = bord[pl1].dir is -self.dir and bord[pl2].color is ' '
        return back



bord = [peon('g', i) for i in range(4)]
bord.append(peon(' ', 4))
bord.extend([peon('b', i + 5) for i in range(4)])


def expose_bord(bord):
    return [p.id for p in bord]


def list_moves():
    movi = []
    for p in bord:
        if p.is_step():
            movi.append((p, 'step'))
        if p.is_jump():
            movi.append((p, 'jump'))
    return movi


def distance(kind):
    if kind is 'jump':
        return 2
    elif kind is 'step':
        return 1
    else:
        raise ValueError


def move(p, kind):
    global bord
    place = bord.index(p)
    bord[place + distance(kind) * p.dir] = p
    bord[place] = peon(' ', 4)
    return bord


def game():
    cond = True
    print(expose_bord(bord))
    while cond:
        try:
            movi = list_moves()
            ch = choice(movi)
            move(ch[0], ch[1])
        except IndexError:
            cond = False
        print(expose_bord(bord))

game()

"""
print(expose_bord(bord))
joe = [i.is_step() for i in bord]
print(joe)
"""
