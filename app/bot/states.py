"""FSM state for the "tap a button, then just send text" input flow."""

from __future__ import annotations

from aiogram.fsm.state import State, StatesGroup


class AwaitingInput(StatesGroup):
    waiting = State()
