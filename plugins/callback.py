from pyrogram import filters, types, enums, errors
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from clients import Client
from controllers import user, group

@Client.on_callback_query(filters.regex(r'^gc_(.+)'))
async def showList(c: Client, cb: types.CallbackQuery):
    usr = cb.from_user
    users = await user.get_user(usr.id)
    if not users:
        users = await user.create_user(usr.id, usr.first_name, usr.last_name, usr.username)
    if [users.first_name, users.last_name, users.username] != [usr.first_name, usr.last_name, usr.username]:
        users = await user.update_user(usr.id, usr.first_name, usr.last_name, usr.username)
    
    chatid = int(cb.matches[0].group(1))
    
    groups = await group.get_group(chatid)
    if not groups:
        await cb.answer('Tidak ada groups.', True)
        return
    if len(groups.topics) == 0:
        await cb.answer("Tidak ada Topics", True)
        return
    columns = 3
    keyboard = []

    for idx, i in enumerate(range(0, len(groups.topics), columns), start=1):
        row = [
            InlineKeyboardButton(
                f"Topic {idx + j}",
                url=f"t.me/c/{str(groups.chat_id).replace('-100', '')}/{gp.id}"
            )
            for j, gp in enumerate(groups.topics[i:i + columns])
        ]
        keyboard.append(row)

    await cb.edit_message_reply_markup(reply_markup=InlineKeyboardMarkup(keyboard))