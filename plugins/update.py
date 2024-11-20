import asyncio

from pyrogram import filters, types, enums, errors
from clients import Client

from controllers import group

@Client.on_message(filters.group)
async def update_message(c: Client, m: types.Message):
    if not m.is_topic_message:
        await c.leave_chat(m.chat.id)
        return

    if m.service == enums.MessageServiceType.NEW_CHAT_MEMBERS:
        for user in m.new_chat_members:
            if user.id == c.me.id:
                await m.reply("Wah, terima kasih banyak sudah mengizinkan saya bergabung di grup luar biasa ini! Rasanya seperti masuk ke istana persahabatan yang megah!")
                return
            
    print(f"[ {m.from_user.id} ] [ {m.message_thread_id} ] : {m.text}")
    if m.is_topic_message:
        try:
            member = await c.get_chat_member(m.chat.id, m.from_user.id)
            if member.status in [enums.ChatMemberStatus.OWNER, enums.ChatMemberStatus.ADMINISTRATOR]:
                return
            else:
                groups = await group.get_group(m.chat.id)
                if not groups:
                    return
                for topic in groups.topics:
                    if topic.id == m.message_thread_id:
                        if m.from_user.id not in topic.allow:
                            await m.delete()
                            
        except errors.UserNotParticipant:
            return
        except errors.FloodWait as e:
            await asyncio.sleep(e.value + 2)
            await m.delete()
            return
        except:
            return