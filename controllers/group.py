import config

from models.data import Grup, Topic

async def get_groups():
    return await Grup.find_all().to_list()

async def get_group(chat_id: int):
    return await Grup.find_one({"_id": chat_id})

async def create_group(chat_id: int, title: str, from_id: int):
    group = Grup(
        _id=chat_id, 
        chat_id=chat_id,
        title=title,
        from_id=from_id
    )
    await group.create()
    return group

async def get_mygroups(from_id: int):
    groups = await Grup.find(Grup.from_id == from_id).to_list()
    return groups

async def add_topic(chat_id: int, topic_id: int, title: str):
    group = await get_group(chat_id)
    if group:
        if not any(existing_topic.id == topic_id for existing_topic in group.topics):
            group.topics.append(Topic(
                id=topic_id,
                title=title
            ))
            await group.save()
            return group
        return False
    return group

async def add_access(chat_id: int, from_id: int):
    group = await get_group(chat_id)
    if group:
        for topic in group.topics:
            if from_id in topic.allow:
                return False
        for topic in group.topics:
            topic.allow.append(from_id)
        await group.save() 
        return group
    return group

async def delete_topic(chat_id: int, topic_id: int):
    group = await get_group(chat_id)
    if group:
        initial_count = len(group.topics)
        group.topics = [topic for topic in group.topics if topic.id != topic_id]
        if len(group.topics) < initial_count:
            await group.save()
            return group  # Topik berhasil dihapus
        return False  # Topik tidak ditemukan
    return group  # Grup tidak ditemukan

async def update_topic(self, topic_id: int, new_title: str):
        """Memperbarui judul topik berdasarkan topic_id."""
        for topic in self.topics:
            if topic.id == topic_id:
                topic.title = new_title
                await self.save()
                return True
        return False  # Jika topic_id tidak ditemukan

# async def update_role(user_id: int, role: str):
#     user = await get_user(user_id)
#     if user:
#         user.role = role
#         await user.save()
#     return user

# async def update_saldo(user_id: int, saldo_masuk: int):
#     user = await get_user(user_id)
#     if user:
#         potongan = config.MARGIN / 100
#         saldo_saya = saldo_masuk - (saldo_masuk * potongan)
#         user.saldo = int(user.saldo + saldo_saya)
#         await user.save()
#     return user

# async def update_saldo_penarikan(user_id: int, penarikan: int):
#     user = await get_user(user_id)
#     if user:
#         user.saldo = user.saldo - penarikan
#         await user.save()
#     return user

# async def get_all_admins():
#     user = await User.find(User.role == 'admin').to_list()
#     return user

# async def delete_user(user_id: int):
#     user = await get_user(user_id)
#     if user:
#         await user.delete()
#     return user