"""FSM state for the "tap a button, then just send text" input flow."""

from __future__ import annotations

from aiogram.fsm.state import State, StatesGroup


class AwaitingInput(StatesGroup):
    waiting = State()


class PersonalWordlistForm(StatesGroup):
    """Step-by-step questions for the personal wordlist generator."""

    name = State()
    nickname = State()
    birth_year = State()
    extra = State()
