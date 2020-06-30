import asyncio
import re

from typing import Tuple
from ServiceProvider import Command
import numpy as np
from math import prod

import argparse

_COLS = (':one:', ':two:', ':three:', ':four:', ':five:', ':six:', ':seven:', ':eight:', ':nine:', ':regional_indicator_a:', ':regional_indicator_b:', ':regional_indicator_c:', ':regional_indicator_d:', ':regional_indicator_e:', ':regional_indicator_f:', ':regional_indicator_g:', ':regional_indicator_h:', ':regional_indicator_i:', ':regional_indicator_j:', ':regional_indicator_k:')
_REACTIONS = ('1️⃣', '2️⃣', '3️⃣', '4️⃣', '5️⃣', '6️⃣', '7️⃣', '8️⃣', '9️⃣', '🇦', '🇧', '🇨', '🇩', '🇪', '🇫', '🇬', '🇭', '🇮', '🇯', '🇰')
_PLAYERS = ('⚫', '🔴', '🟡', '🔵', '⚪', '🟢', '🟠', '🟣', '🟤')

class ArgumentParser(argparse.ArgumentParser):
    def error(self, message):
        raise Exception(self.format_help())

def size(q):
    m = re.match("([0-9]+)x([0-9]+)",q)
    if m:
        return (int(m.group(1)),int(m.group(2)))
    raise Exception("invalid format")

def bound(a,x,b):
    return max(a,min(x,b))

@Command.register("connect")
async def command(message):
    parser = ArgumentParser(description='Connect n in a row', prog="!connect",add_help=False,formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('-connect' , metavar='N', type=int,help='how many pieces in a row the player needs to win',nargs="?",default=4)
    parser.add_argument('-size', metavar='AxB', type=size,help="how big the board is",nargs="?",default="6x7")
    parser.add_argument('-players', metavar="M", type=int,nargs="?",default=2, help="how many player can play")
    try:
        k = parser.parse_args(message.content.split(" ") if message.content else [])
    except Exception as e:
        await message.reply(f"```{parser.format_help()}```")
        return

    k=vars(k)
    rows, cols = k["size"]
    cols = bound(1,cols,len(_COLS)-1)
    rows = bound(1,rows,(2000//cols-1)//16)
    n_players = bound(1,k["players"],len(_PLAYERS)-1)
    n_connect = max(0,k["connect"])

    msg = await message.reply(f"Playing connect {n_connect} on a {rows}x{cols} board with {n_players} players.\nChoose your color.")

    # Player selection
    for i in range(n_players):
        await msg.add_reaction(_PLAYERS[i+1])

    # Player selection
    users = [None] * n_players
    client = message.client
    while not all(users):
        try:
            reaction, user = await client.wait_for('reaction_add', timeout=60.0)
            #replace with check
            if reaction.message.id == msg.id and reaction.emoji in _PLAYERS[1:n_players+2]:
                i = _PLAYERS.index(reaction.emoji) - 1
                if not user.bot and users[i] is None:
                    users[i] = user

        except asyncio.TimeoutError:
            await msg.clear_reactions()
            await msg.edit(content="Not enough players unfortunatly")
            return

    await msg.clear_reactions()
    await msg.edit(content=f"Playing connect {n_connect} on a {rows}x{cols} board with {n_players} players.\nCurrently playing: {', '.join(f'{u.name} {_PLAYERS[i+1]}' for i, u in enumerate(users))}.")

    board = Board(rows,cols,n_connect)

    status = await message.reply(f"Building board...")
    header = await message.reply('\u200c'.join(_COLS[:cols]).strip())
    body   = await message.reply("\n".join(['\u200c'.join([_PLAYERS[int(i)] for i in r]) for r in board.board()]))
    footer = await message.reply('\u200c'.join(_COLS[:cols]).strip())

    if n_connect == 0:
        await status.edit(content=f'Game has finished and {users[0].name} has won!!!!')
        return

    for row in range(cols):
        await status.add_reaction(_REACTIONS[row])

    turn = 0
    while not board.done():
        curr_user = users[turn]
        curr_color = _PLAYERS[turn+1]
        await status.edit(content=f"It's {curr_user.name}'s turn ({curr_color})")

        while True:
            try:
                reaction, user = await client.wait_for('reaction_add', timeout=12*60*60)
                if status.id == reaction.message.id:
                    if user.id == curr_user.id and reaction.emoji in _REACTIONS:
                        try:
                            # can do move
                            board.do_move(turn+1,_REACTIONS.index(reaction.emoji))
                            await body.edit(content="\n".join(['\u200c'.join([_PLAYERS[int(i)] for i in r]) for r in board.board()]))
                            turn = (turn + 1) % len(users)
                        except Exception as e:
                            pass
                        await reaction.remove(user)
                        break
            except asyncio.TimeoutError:
                return

    if board.winners:
        await status.edit(content=f'Game has finished and {" ,".join([users[int(i)].name for i in board.winners])} has won!!!!')
    else:
        await status.edit(content='Game has finished in a draw.')

def check_up_diag(board,n_connect):
    winners = set()
    r,c = board.shape
    p = board[0,:]
    d = np.r_[0, p[:-1]]
    w1,w2 = np.zeros(c),np.zeros(c)
    for i in range(1,r):
        q = board[i,:]
        w1,w2 = (w1+1)*(p == q), (w2+1)*(d == q)
        winners.update(q[w1 >= n_connect-1])
        winners.update(q[w2 >= n_connect-1])
        w2 = np.r_[0, w2[:-1]]
        p = q
        d = np.r_[0, p[:-1]]
    return winners

class Board:
    def __init__(self, rows, cols, n_connect):
        self._board = np.zeros((rows,cols))
        self.n_connect = n_connect
        self.index = np.arange(rows)
        self.filled = 0
        self.winners = set()

    def do_move(self, player, col):
        try:
            row = self.index[self._board[:,col]==0][-1]
            self._board[row,col] = player
            self.filled += 1
            return row, col
        except Exception as e:
            raise Exception("invalid move")

    def done(self):
        self.winners = self._winners()
        return self.winners or (self.filled >= prod(self._board.shape))

    def _winners(self):
        p = check_up_diag(self._board,self.n_connect)
        q = check_up_diag(np.flip(self._board.T,0),self.n_connect)
        return (p | q) - {0}

    def board(self):
        return self._board
