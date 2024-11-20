import config

from models.user import User

async def get_users():
    return await User.find_all().to_list()

async def get_user(user_id: int):
    return await User.find_one({"_id": user_id})

async def create_user(user_id: int, first_name: str, last_name: str = None, username: str = None):
    role = 'owner' if config.OWNER_ID == user_id else 'member'
    user = User(
        _id=user_id, 
        first_name=first_name, 
        last_name=last_name, 
        username=username,
        role=role
    )
    await user.create()
    return user

async def update_user(user_id: int, first_name: str = None, last_name: str = None, username: str = None):
    user = await get_user(user_id)
    if user:
        if first_name is not None:
            user.first_name = first_name
        user.last_name = last_name
        user.username = username
        await user.save()
    return user

async def update_role(user_id: int, role: str):
    user = await get_user(user_id)
    if user:
        user.role = role
        await user.save()
    return user

async def update_saldo(user_id: int, saldo_masuk: int):
    user = await get_user(user_id)
    if user:
        potongan = config.MARGIN / 100
        saldo_saya = saldo_masuk - (saldo_masuk * potongan)
        user.saldo = int(user.saldo + saldo_saya)
        await user.save()
    return user

async def update_saldo_penarikan(user_id: int, penarikan: int):
    user = await get_user(user_id)
    if user:
        user.saldo = user.saldo - penarikan
        await user.save()
    return user

async def get_all_admins():
    user = await User.find(User.role == 'admin').to_list()
    return user

async def delete_user(user_id: int):
    user = await get_user(user_id)
    if user:
        await user.delete()
    return user