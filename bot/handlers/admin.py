from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command
from config import load_config
from database.models import SessionLocal, Administrator

# подгружаем SUPERADMIN_ID из .env

config = load_config()
SUPERADMIN_ID = config.superadmin_id

router = Router()

@router.message(Command("add_admin"))
async def add_admin(message: Message):
    """Добавляет нового администратора по его telegram ID.
    Пример использования: /add_admin <telegram_id>
    Только супер-админ может использовать эту команду.
    """
    if str(message.from_user.id) != SUPERADMIN_ID:
        await message.answer("❌ Только супер-админ может выполнять эту команду.")
        return
    
    parts = message.text.split(maxsplit=1)
    if len(parts) < 2:
        await message.answer("❌ Неверный формат. Используйте:\n/add_admin <telegram_id>")
        return
    
    new_id = parts[1].strip()
    db = SessionLocal()
    exists = db.query(Administrator).filter_by(user_id=new_id).first()
    if exists:
        await message.answer(f"❌ Администратор с ID {new_id} уже существует.")
    else:
        db.add(Administrator(user_id=new_id))
        db.commit()
        await message.answer(f"✅ Администратор с ID {new_id} добавлен.")
    db.close()

@router.message(Command("remove_admin"))
async def remove_admin(message: Message):
    """Удаляет администратора по его TG ID.
    Пример использования: /remove_admin <telegram_id>
    Только супер-админ может использовать эту команду.
    """
    if str(message.from_user.id) != SUPERADMIN_ID:
        await message.answer("❌ Только супер-админ может выполнять эту команду.")
        return
    
    parts = message.text.split(maxsplit=1)
    if len(parts) < 2:
        await message.answer("❌Неверный формат. Используйте:\n/remove_admin <telegram_id>")
        return
    
    rem_id = parts[1].strip()
    db = SessionLocal()
    admin = db.query(Administrator).filter_by(user_id=rem_id).first()
    if not admin:
        await message.answer(f"❌ Администратор с ID {rem_id} не найден.")
    else:
        db.delete(admin)
        db.commit()
        await message.answer(f"✅ Администратор с ID {rem_id} удален.")
    db.close()

@router.message(Command("list_admins"))
async def list_admins(message: Message):
    """Выводит список всех администраторов.
    Только супер-админ может использовать эту команду.
    """
    if str(message.from_user.id) != SUPERADMIN_ID:
        await message.answer("❌ Только супер-админ может выполнять эту команду.")
        return
    
    db = SessionLocal()
    admins = db.query(Administrator).all()
    db.close()
    
    if not admins:
        await message.answer("Список администраторов пуст.")
        return
    
    admin_list = "\n".join([f"- ID: {admin.user_id}" for admin in admins])
    await message.answer(f"Список администраторов:\n{admin_list}")