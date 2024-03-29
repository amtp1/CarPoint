from typing import Any

from aiogram.types import Message
from aiogram.dispatcher.storage import FSMContext

from objects.globals import dp
from objects import globals
from keyboard.keyboard import contact_me_markup

@dp.message_handler(lambda message: message.text == 'Для инвесторов', state='*')
async def for_investors(message: Message, state: FSMContext) -> Message:
    await state.finish()
    page: Any = globals.root.find("for_investors")
    return await message.answer(page.text, reply_markup=contact_me_markup)
