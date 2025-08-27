from aiogram import Router
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from database.models import Student, SessionLocal
from database.models import Administrator
import config
from bot.keyboards.students_keyboard import main_menu_kb, students_list_kb

router = Router()

# простая in-memory очередь ожидания действий: {user_id: {action: str, payload: dict}}
pending_actions: dict[int, dict] = {}
menu_messages: dict[int, dict] = {}


def is_admin(user_id: int) -> bool:
    db = SessionLocal()
    admin = db.query(Administrator).filter_by(user_id=str(user_id)).first()
    db.close()
    return admin is not None


@router.message(Command("students"))
async def students_menu(message: Message):
    """Главное меню управления учениками с inline-клавиатурой"""
    if not is_admin(message.from_user.id):
        await message.answer("❌ Только администраторы могут управлять учениками.")
        return
    sent = await message.answer("Выберите действие с учениками:", reply_markup=main_menu_kb())
    # сохраняем id сообщения меню и id команды пользователя, чтобы можно было удалить потом
    menu_messages[message.from_user.id] = {
        "bot_msg_id": sent.message_id,
        "chat_id": sent.chat.id,
        "user_cmd_id": message.message_id,
    }


@router.callback_query(lambda c: c.data and c.data.startswith("students:"))
async def students_callback_handler(callback: CallbackQuery):
    data = callback.data
    user_id = callback.from_user.id
    # обработать основные команды
    if data == "students:menu":
        await callback.message.edit_text("Выберите действие с учениками:", reply_markup=main_menu_kb())
        await callback.answer()
        return

    if data == "students:view":
        db = SessionLocal()
        students = db.query(Student).order_by(Student.id).all()
        db.close()
        if not students:
            await callback.answer("Список пуст.")
            return
        await callback.message.edit_text("Список учеников:", reply_markup=students_list_kb(students, mode="view"))
        await callback.answer()
        return

    if data == "students:add":
        pending_actions[user_id] = {"action": "add", "payload": {}}
        await callback.message.edit_text("Отправьте имя нового ученика как обычное сообщение.")
        await callback.answer()
        return

    if data == "students:edit":
        db = SessionLocal()
        students = db.query(Student).order_by(Student.id).all()
        db.close()
        if not students:
            await callback.answer("Список пуст.")
            return
        await callback.message.edit_text("Выберите ученика для редактирования:", reply_markup=students_list_kb(students, mode="edit"))
        await callback.answer()
        return

    if data == "students:delete":
        db = SessionLocal()
        students = db.query(Student).order_by(Student.id).all()
        db.close()
        if not students:
            await callback.answer("Список пуст.")
            return
        await callback.message.edit_text("Выберите ученика для удаления:", reply_markup=students_list_kb(students, mode="delete"))
        await callback.answer()
        return

    # обработка выбора конкретного студента: формат students:action:id
    parts = data.split(":")
    if len(parts) >= 3:
        _, action, sid = parts[0], parts[1], parts[2]
        if not sid.isdigit():
            await callback.answer("Неверный ID.")
            return
        student_id = int(sid)
        if action == "view":
            db = SessionLocal()
            student = db.get(Student, student_id)
            db.close()
            if not student:
                await callback.answer("Ученик не найден.")
                return
            # показываем краткую информацию в всплывающем уведомлении, не меняя сообщение
            await callback.answer(f"#{student.id} — {student.name}", show_alert=False)
            return

        if action == "edit":
            # помечаем pending action
            pending_actions[user_id] = {"action": "edit", "payload": {"student_id": student_id}}
            await callback.message.edit_text(f"Отправьте новое имя для ученика #{student_id} как обычное сообщение.")
            await callback.answer()
            return

        if action == "delete":
            db = SessionLocal()
            student = db.get(Student, student_id)
            if not student:
                db.close()
                await callback.answer("Ученик не найден.")
                return
            db.delete(student)
            db.commit()
            db.close()
            await callback.message.edit_text(f"✅ Ученик #{student_id} удалён.", reply_markup=main_menu_kb())
            await callback.answer()
            return

    # выход — удаляем сообщение с клавиатурой
    if data == "students:exit":
        # пытаемся удалить сообщение меню (бота)
        try:
            await callback.message.delete()
        except Exception:
            try:
                await callback.message.edit_reply_markup(None)
            except Exception:
                pass

        # если есть сохранённое сообщение команды пользователя — удалим
        info = menu_messages.pop(callback.from_user.id, None)
        if info:
            try:
                await callback.bot.delete_message(info["chat_id"], info.get("user_cmd_id"))
            except Exception:
                pass

        # отправим краткое подтверждение в чат (не alert)
        try:
            await callback.bot.send_message(callback.message.chat.id if callback.message and callback.message.chat else info.get("chat_id"), "Меню закрыто.")
        except Exception:
            # fallback: показать уведомление
            await callback.answer("Меню закрыто.")

        await callback.answer()
        return


@router.message()
async def catch_messages(message: Message):
    """Перехватывает обычные сообщения для обработки ожидающих действий (add/edit)."""
    user_id = message.from_user.id
    if user_id not in pending_actions:
        return
    action = pending_actions[user_id]
    if action["action"] == "add":
        name = message.text.strip()
        if not name:
            await message.answer("❌ Имя пустое. Отправьте корректное имя.")
            return
        db = SessionLocal()
        new_student = Student(name=name)
        db.add(new_student)
        db.commit()
        db.refresh(new_student)
        db.close()
        del pending_actions[user_id]
        await message.answer(f"✅ Ученик {name} добавлен с ID {new_student.id}.", reply_markup=main_menu_kb())

    elif action["action"] == "edit":
        student_id = action["payload"].get("student_id")
        if not student_id:
            del pending_actions[user_id]
            await message.answer("❌ Внутренняя ошибка: отсутствует ID ученика.")
            return
        new_name = message.text.strip()
        if not new_name:
            await message.answer("❌ Имя пустое. Отправьте корректное имя.")
            return
        db = SessionLocal()
        student = db.get(Student, student_id)
        if not student:
            db.close()
            del pending_actions[user_id]
            await message.answer("❌ Ученик не найден.")
            return
        student.name = new_name
        db.commit()
        db.close()
        del pending_actions[user_id]
        await message.answer(f"✅ Имя ученика #{student_id} изменено на {new_name}.", reply_markup=main_menu_kb())

