import asyncio
import re

from pyrogram import filters, types, enums, errors
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from clients import Client
from controllers import user, group


from datetime import datetime as dt

async def create_keyboard(groups, columns=2):
    keyboard = []
    for i in range(0, len(groups), columns):
        row = [InlineKeyboardButton(f"{gp.title}", callback_data=f"gc_{gp.id}") for gp in groups[i:i + columns]]
        keyboard.append(row)
    return InlineKeyboardMarkup(keyboard)

@Client.on_message(filters.command('start'))
async def start_handler(c, m: types.Message):
    usr = m.from_user
    users = await user.get_user(usr.id)
    if not users:
        users = await user.create_user(usr.id, usr.first_name, usr.last_name, usr.username)
    if [users.first_name, users.last_name, users.username] != [usr.first_name, usr.last_name, usr.username]:
        users = await user.update_user(usr.id, usr.first_name, usr.last_name, usr.username)
    
    if len(m.command) > 1:
        if m.command[1] == 'add':
            await add_handler(c, m)
            return
    
    await m.reply(f'<b>Hi {users.first_name}\nTOPIC</b> adalah Bot Telegram yang Dibuat untuk Mengatur TOPIC Group.')
    
@Client.on_message(filters.command('add') & filters.private)
async def add_handler(c: Client, m: types.Message):
    if len(m.command) == 1:
        await m.reply('gunakan /add chat_id')
        return
    else:
        try:
            if m.text == '/start add':
                await m.reply('gunakan /add chat_id')
                return
            chat = await c.get_chat(m.command[1])
            if chat.is_forum:
                groups = await group.get_group(chat.id)
                if not groups:
                    groups = await group.create_group(chat.id, chat.title, m.from_user.id)
                    pesan = 'Berhasil ditambahkan'
                else:
                    pesan = f'{groups.title}\nSudah ditambahkan, Oleh <a href="tg://user?id={groups.from_id}">Owner</a>'
                await m.reply(pesan)
            else:
                await m.reply(f'{m.command[1]} Bukan group')
        except errors.UsernameInvalid:
            await m.reply(f'Username {m.command[1]} tidak valid.')
        except errors.PeerIdInvalid:
            await m.reply(f'ID {m.command[1]} tidak valid.')
        except errors.ChannelPrivate:
            await m.reply('Saya tidak berada dalam group')
        except Exception as e:
            await m.reply(f'Terjadi kesalahan: {str(e)}')
            
@Client.on_message(filters.command(['mygroup', 'mygroups']) & filters.private)
async def mygroup_handler(c: Client, m: types.Message):
    usr = m.from_user
    users = await user.get_user(usr.id)
    if not users:
        users = await user.create_user(usr.id, usr.first_name, usr.last_name, usr.username)
    if [users.first_name, users.last_name, users.username] != [usr.first_name, usr.last_name, usr.username]:
        users = await user.update_user(usr.id, usr.first_name, usr.last_name, usr.username)
        
    groups = await group.get_groups()
    if len(groups) == 0:
        await m.reply('Tidak ada groups')
        return
    data = []
    for i in groups:
        try:
            member = await c.get_chat_member(i.chat_id, m.from_user.id)
            if member.status in [enums.ChatMemberStatus.OWNER, enums.ChatMemberStatus.ADMINISTRATOR]:
                data.append(i)
        except errors.UserNotParticipant:
            pass
        except:
            pass
    
    markup = await create_keyboard(data, 3)
    await m.reply('Your current group by topic: ', reply_markup=markup)
    
@Client.on_message(filters.command('addtopic') & filters.private)
async def addtopic_handler(c: Client, m: types.Message):
    message = await m.reply('Kirimkan saya link topic anda.\nKetik /cancel untuk membatalkan.')
    data = await c.listen(chat_id=m.chat.id, user_id=m.from_user.id)
    if not data.text or data.text == f"/{m.command[0]}":
        await message.delete()
        await data.delete()
        await addtopic_handler(c, m)
        return
    
    if data.text == '/cancel':
        p = await m.reply('Berhasil dibatalkan')
        await c.send_reaction(m.chat.id, p.id, emoji='👍')
        return
    
    matched = re.search(r"https?:\/\/t\.me\/(?:c\/(\d+)\/|([a-zA-Z0-9_]+)\/)(\d+)", data.text)
    if not matched:
        await message.delete()
        await data.delete()
        await addtopic_handler(c, m)
        return
    
    grupid = matched.group(2) if matched.group(2) else int(f"-100{matched.group(1)}")
    topicid = int(matched.group(3))
    
    try:
        data_chat = await c.get_chat(grupid)
        gc = await c.send_message(grupid, "Testing...")
        await gc.delete()
        if gc.chat.type == enums.ChatType.PRIVATE:
            await m.reply('<i>❌ Pengguna tidak dapat Ditambahkan.</i>')
            return
        if not gc.is_topic_message:
            await m.reply('<i>❌ Bukan Topic Grup.</i>')
            return
        
        try:
            member = await c.get_chat_member(grupid, m.from_user.id)
            if member.status == enums.ChatMemberStatus.MEMBER:
                await m.reply('<i>❌ Pastikan kamu adalah admin grup.</i>')
                return
        except errors.UserNotParticipant:
            await m.reply('<i>❌ Kamu bukan bagian anggota grup</i>')
            return
        
        groups = await group.get_group(data_chat.id)
        if not groups:
            await m.reply('Silahkan list dulu grup diprivate', reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton('Klik disini', url=f't.me/{c.me.username}?start=add')]
            ]))
            return
        data_topic = await group.add_topic(data_chat.id, topicid, '')
        if data_topic:
            pesan = (
                f"<b><i><u>Berhasil Menambahkan Topic Chat ✅</b></i></u>\n\n"
                f"{data_chat.title}\n"
                f"Member: {data_chat.members_count:,}".replace(',', '.')
            )
            
        else:
            pesan = (
                f"<b><i><u>Gagal Menambahkan Topic Chat ❌</b></i></u>\n\n"
                f"{data_chat.title}\n"
                f"Member: {data_chat.members_count:,}".replace(',', '.')
            )
        await m.reply(pesan, reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton('Link', url=data.text)]
        ]))
    except Exception as e:
        await m.reply(f"Terjadi kesalahan lek: str{e}")
        
@Client.on_message(filters.command('deltopic') & filters.private)
async def untopic_handler(c: Client, m: types.Message):
    message = await m.reply('Kirimkan saya link topic anda.\nKetik /cancel untuk membatalkan.')
    data = await c.listen(chat_id=m.chat.id, user_id=m.from_user.id)
    if not data.text or data.text == f"/{m.command[0]}":
        await message.delete()
        await data.delete()
        await untopic_handler(c, m)
        return
    
    if data.text == '/cancel':
        p = await m.reply('Berhasil dibatalkan')
        await c.send_reaction(m.chat.id, p.id, emoji='👍')
        return
    
    matched = re.search(r"https?:\/\/t\.me\/(?:c\/(\d+)\/|([a-zA-Z0-9_]+)\/)(\d+)", data.text)
    if not matched:
        await message.delete()
        await data.delete()
        await untopic_handler(c, m)
        return
    
    grupid = matched.group(2) if matched.group(2) else int(f"-100{matched.group(1)}")
    topicid = int(matched.group(3))
    
    try:
        data_chat = await c.get_chat(grupid)
        gc = await c.send_message(grupid, "Testing...")
        await gc.delete()
        if gc.chat.type == enums.ChatType.PRIVATE:
            await m.reply('<i>❌ Pengguna tidak dapat Ditambahkan.</i>')
            return
        if not gc.is_topic_message:
            await m.reply('<i>❌ Bukan Topic Grup.</i>')
            return
        
        try:
            member = await c.get_chat_member(grupid, m.from_user.id)
            if member.status == enums.ChatMemberStatus.MEMBER:
                await m.reply('<i>❌ Pastikan kamu adalah admin grup.</i>')
                return
        except errors.UserNotParticipant:
            await m.reply('<i>❌ Kamu bukan bagian anggota grup</i>')
            return
        
        groups = await group.get_group(data_chat.id)
        if not groups:
            await m.reply('Silahkan list dulu grup diprivate', reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton('Klik disini', url=f't.me/{c.me.username}?start=add')]
            ]))
            return
        data_topic = await group.delete_topic(data_chat.id, topicid)
        if data_topic:
            pesan = (
                f"<b><i><u>Berhasil Menghapus Topic Chat ✅</b></i></u>\n\n"
                f"{data_chat.title}\n"
                f"Member: {data_chat.members_count:,}".replace(',', '.')
            )
        else:
            pesan = (
                f"<b><i><u>Gagal Menghapus Topic Chat ❌</b></i></u>\n\n"
                f"{data_chat.title}\n"
                f"Member: {data_chat.members_count:,}".replace(',', '.')
            )
        await m.reply(pesan, reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton('Link', url=data.text)]
        ]))
    except Exception as e:
        await m.reply(f"Terjadi kesalahan lek: str{e}")
        
@Client.on_message(filters.command('addtour') & filters.group)
async def addtour_handler(c: Client, m: types.Message):
    try:
        member = await c.get_chat_member(m.chat.id, m.from_user.id)
        if member.status == enums.ChatMemberStatus.MEMBER:
            if m.is_topic_message:
                groups = await group.get_group(m.chat.id)
                if not groups:
                    return
                if any(existing_topic.id == m.message_thread_id for existing_topic in groups.topics):
                    data = await group.add_tour(m.chat.id, m.from_user.id)
                    if data:
                        p =  await m.reply(f"{m.from_user.first_name} diizinkan")
                        await m.delete()
                        await asyncio.sleep(5)
                        await p.delete()
                        return
                    
        await m.delete()
    except errors.UserNotParticipant:
        return
    except errors.FloodWait as e:
        await asyncio.sleep(e.value + 2)
        await m.delete()
        return
    except BaseException as e:
        print("Terjadi error saat menggunakan /addtour")
        print(e)
    
@Client.on_message(filters.command('addtour') & filters.private)
async def wkkw(_, m):
    await m.reply('Lakukan di grup lek')