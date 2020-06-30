import asyncio

from typing import Tuple
from ServiceProvider import Command


_PLAYER1 = '🔴'
_PLAYER2 = '🟡'

_COLS = (':one:', ':two:', ':three:', ':four:', ':five:', ':six:', ':seven:', ':eight:', ':nine:', ':regional_indicator_a:', ':regional_indicator_b:', ':regional_indicator_c:', ':regional_indicator_d:', ':regional_indicator_e:', ':regional_indicator_f:', ':regional_indicator_g:', ':regional_indicator_h:', ':regional_indicator_i:', ':regional_indicator_j:', ':regional_indicator_k:')
_REACTIONS = ('1️⃣', '2️⃣', '3️⃣', '4️⃣', '5️⃣', '6️⃣', '7️⃣', '8️⃣', '9️⃣', '🇦', '🇧', '🇨', '🇩', '🇪', '🇫', '🇬', '🇭', '🇮', '🇯', '🇰')
_PLAYERS = ('⚫', _PLAYER1, _PLAYER2)

@Command.register("connect")
async def command(message):
    msg = await message.reply("Choose your color")
    await msg.add_reaction(_PLAYER1)
    await msg.add_reaction(_PLAYER2)

    # Player selection
    users = [1, None, None]
    client = message.client
    while not all(users):
        try:
            reaction, user = await client.wait_for('reaction_add', timeout=60.0)
            if reaction.message.id == msg.id and reaction.emoji in _PLAYERS[1:]:
                i = _PLAYERS.index(reaction.emoji)
                if not user.bot and users[i] is None:
                    users[i] = user

        except asyncio.TimeoutError:
            await msg.delete()
            return

    await msg.delete()

    # Create game TODODOTODODODOO CLEANUP SLKJLFJDS
    n_connect, rowcols = message.content.split(' ')
    rows, cols = rowcols.split('x')
    g = Game(rows=rows, cols=cols, n_connect=n_connect)


    # Build board
    msgs = [
        await message.reply(f"Building board..."),
        await message.reply(str(g)),
    ]

    for row in range(g.cols()):
        await msgs[0].add_reaction(_REACTIONS[row])

    while g.has_won() is None:
        curr_user = users[g.turn()]
        curr_color = _PLAYERS[g.turn()]
        await msgs[0].edit(content=f"It's {curr_user.name}'s turn ({curr_color})")

        while True:
            try:
                reaction, user = await client.wait_for('reaction_add', timeout=12*60*60)
                if msgs[0].id == reaction.message.id:
                    if user.id == curr_user.id and reaction.emoji in _REACTIONS:
                        try:
                            # can do move
                            row, col = g.do_move(_REACTIONS.index(reaction.emoji))

                            content = [list(m) for m in msgs[-1].content.split('\n')]
                            content[-row-1][col] = curr_color
                            await msgs[-1].edit(content='\n'.join(''.join(c) for c in content))
                        except (AssertionError, IndexError):
                            pass

                        await reaction.remove(user)
                        break



            except asyncio.TimeoutError:
                return

    if g.has_won() is not None:
        if g.has_won() == 0:
            await msgs[0].edit(content='Game has finished in a draw.')
        else:
            await msgs[0].edit(content=f'Game has finished and {users[g.has_won()].name} has won!!!!')



#   ____                      _
#  |  _ \                    | |
#  | |_) | ___   __ _ _ __ __| |
#  |  _ < / _ \ / _` | '__/ _` |
#  | |_) | (_) | (_| | | | (_| |
#  |____/ \___/ \__,_|_|  \__,_|
#
#  Board

DEFAULT_PLAYER_NAMES = ('_ ', 'O ', 'X ')
DEFAULT_COL_NAMES = tuple(f'{x} ' for x in range(1, 10))


class Board:

    _board = [[]]

    def rows(self):
        return len(self._board)

    def cols(self):
        return len(self._board[0])

    def n_connect(self):
        return self._n_connect

    def __init__(self, rows=None, cols=None, player_names=DEFAULT_PLAYER_NAMES, col_names=DEFAULT_COL_NAMES, n_connect=None):
        """
        >>> b = Board(); (b.rows(), b.cols())
        (6, 7)
        >>> b = Board(4, 6); (b.rows(), b.cols())
        (4, 6)
        >>> try: Board(0, 0)
        ... except AssertionError: pass
        >>> try: Board('ahaha', 'frick')
        ... except AssertionError: pass
        """

        if rows is None:
            rows = 6
        if cols is None:
            cols = 7
        if n_connect is None:
            n_connect = 4

        try:
            rows = max(1, min(10, int(rows)))
            cols = max(1, min(len(col_names)-1, int(cols)))
            n_connect = max(0, int(n_connect))
        except ValueError:
            raise AssertionError('Rows and cols should be numbers')

        self._board = [[0] * cols for _ in range(rows)]
        self._player_names = tuple(player_names)
        self._col_names = tuple(col_names)
        self._n_connect = n_connect

    def do_move(self, player_1: bool, col: int) -> Tuple[int, int]:
        """
        >>> b = Board(4, 4)
        >>> b.do_move(True, 0)
        (0, 0)
        >>> try: b.do_move(True, -1)
        ... except AssertionError: pass
        >>> try: b.do_move(True, 8)
        ... except AssertionError: pass
        >>> b.do_move(True, 0)
        (1, 0)
        >>> b.do_move(True, 0)
        (2, 0)
        >>> b.do_move(True, 0)
        (3, 0)
        >>> try: b.do_move(False, 0)
        ... except AssertionError: pass
        """
        assert 0 <= col <= self.cols(), 'Invalid column'

        row = 0
        while self._board[row][col] != 0:
            row += 1
            assert row < self.rows(), 'Invalid row'

        self._board[row][col] = 1 if player_1 else 2
        return row, col

    def check_vertical(self, r, c):
        """
        >>> b = Board(4, 4)
        >>> b.check_vertical(*b.do_move(True, 0))
        False
        >>> b.check_vertical(*b.do_move(True, 0))
        False
        >>> b.check_vertical(*b.do_move(True, 0))
        False
        >>> b.check_vertical(*b.do_move(True, 0))
        True
        """
        board = self._board
        rows = self.rows()
        a = b = 1

        while r - a >= 000 and board[r - a][c] == board[r][c]: a += 1
        while r + b < rows and board[r + b][c] == board[r][c]: b += 1

        return (a - 1) + (b - 1) >= self._n_connect-1

    def check_horizontal(self, r, c):
        """
        >>> b = Board(4, 4)
        >>> b.check_horizontal(*b.do_move(True, 0))
        False
        >>> b.check_horizontal(*b.do_move(True, 2))
        False
        >>> b.check_horizontal(*b.do_move(True, 3))
        False
        >>> b.check_horizontal(*b.do_move(True, 1))
        True
        """
        board = self._board
        cols = self.cols()
        a = b = 1

        while c - a >= 000 and board[r][c - a] == board[r][c]: a += 1
        while c + b < cols and board[r][c + b] == board[r][c]: b += 1

        return (a - 1) + (b - 1) >= self._n_connect-1

    def check_diag0(self, r, c):
        """
        >>> b = Board(4, 4)
        >>> _ = b.do_move(False, 3)
        >>> _ = b.do_move(False, 3)
        >>> _ = b.do_move(False, 3)
        >>> _ = b.do_move(False, 2)
        >>> _ = b.do_move(False, 2)
        >>> _ = b.do_move(False, 1)
        >>> b.check_diag0(*b.do_move(True, 0))
        False
        >>> b.check_diag0(*b.do_move(True, 2))
        False
        >>> b.check_diag0(*b.do_move(True, 3))
        False
        >>> b.check_diag0(*b.do_move(True, 1))
        True
        """
        board = self._board
        rows = self.rows()
        cols = self.cols()
        a = b = 1

        while r - a >= 000 and c - a >= 000 and board[r - a][c - a] == board[r][c]: a += 1
        while r + b < rows and c + b < cols and board[r + b][c + b] == board[r][c]: b += 1

        return (a - 1) + (b - 1) >= self._n_connect-1

    def check_diag1(self, r, c):
        """
        >>> b = Board(4, 4)
        >>> _ = b.do_move(False, 0)
        >>> _ = b.do_move(False, 0)
        >>> _ = b.do_move(False, 0)
        >>> _ = b.do_move(False, 1)
        >>> _ = b.do_move(False, 1)
        >>> _ = b.do_move(False, 2)
        >>> b.check_diag1(*b.do_move(True, 0))
        False
        >>> b.check_diag1(*b.do_move(True, 2))
        False
        >>> b.check_diag1(*b.do_move(True, 3))
        False
        >>> b.check_diag1(*b.do_move(True, 1))
        True
        """
        board = self._board
        rows = self.rows()
        cols = self.cols()
        a = b = 1

        while r - a >= 000 and c + a < cols and board[r - a][c + a] == board[r][c]: a += 1
        while r + b < rows and c - b >= 000 and board[r + b][c - b] == board[r][c]: b += 1

        return (a - 1) + (b - 1) >= self._n_connect-1

    def check_4_in_row(self, row, col):
        return self.check_vertical(row, col)\
                or self.check_horizontal(row, col)\
                or self.check_diag0(row, col)\
                or self.check_diag1(row, col)

    def __repr__(self):
        """
        >>> b = Board(4, 4)
        >>> b
        1 2 3 4
        _ _ _ _
        _ _ _ _
        _ _ _ _
        _ _ _ _
        >>> _ = b.do_move(True, 1)
        >>> _ = b.do_move(False, 1)
        >>> _ = b.do_move(True, 0)
        >>> _ = b.do_move(False, 2)
        >>> _ = b.do_move(True, 3)
        >>> _ = b.do_move(False, 0)
        >>> _ = b.do_move(True, 0)
        >>> b
        1 2 3 4
        _ _ _ _
        O _ _ _
        X X _ _
        O O X O
        """
        str0 = '\u200c'.join(self._col_names[i] for i in range(self.cols())).strip()
        str1 = '\n'.join(''.join(self._player_names[p] for p in row).strip()
                         for row in self._board[::-1])

        return f'{str0}\n{str1}'


#    _____
#   / ____|
#  | |  __  __ _ _ __ ___   ___
#  | | |_ |/ _` | '_ ` _ \ / _ \
#  | |__| | (_| | | | | | |  __/
#   \_____|\__,_|_| |_| |_|\___|
#
#  Game



class Game:

    def __init__(self, rows=6, cols=7, n_connect=4):
        self._board = Board(rows, cols, _PLAYERS, _COLS, n_connect)

        self._turn = 0
        self._has_won = 3 if self._board.n_connect() > 0 else 1

    def has_won(self):
        return None if self._has_won == 3 else self._has_won

    def turn(self):
        return (self._turn % 2) + 1

    def cols(self):
        return self._board.cols()

    def do_move(self, col: int):
        """
        >>> g = Game()
        >>> _ = g.do_move(3)
        >>> _ = g.do_move(2)
        >>> _ = g.do_move(3)
        >>> _ = g.do_move(2)
        >>> _ = g.do_move(3)
        >>> g.has_won()
        >>> _ = g.do_move(2)
        >>> _ = g.do_move(3)
        >>> g.has_won()
        1
        """
        assert self._has_won == 3, 'Game already finished'

        row, col = self._board.do_move(self.turn() == 1, col)
        self.update_win(row, col)
        return row, col

    def __repr__(self):
        return repr(self._board)

    def __str__(self):
        return repr(self._board)

    def update_win(self, row, col):
        if self._board.check_4_in_row(row, col):
            self._has_won = self.turn()
        self._turn += 1
        if self._turn >= self._board.rows() * self._board.cols():
            if self._has_won == 3:
                self._has_won = 0


if __name__ == '__main__':
    import doctest

    doctest.testmod()

