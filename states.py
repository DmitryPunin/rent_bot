from aiogram.fsm.state import State, StatesGroup
class Form(StatesGroup):
    type = State()
    city = State()
    price = State()
    street = State()
    contact = State()
class select(StatesGroup):
    type = State()
    city = State()
    street = State()
    price_range = State()