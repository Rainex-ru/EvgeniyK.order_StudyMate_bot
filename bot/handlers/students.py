from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command
from database.models import Student, SessionLocal

router = Router()

@router.message(Command("add_student"))
async def add_student(message: Message):

    """Добавляет нового ученика в базу данных."""
    """Пример использования: /add_student <имя>"""

    parts = message.text.split(maxsplit=1)
    if len(parts) < 2:
        await message.answer("Неверный формат. Используйте:\n/add_student <имя>")
        return

    name = parts[1].strip()
    db = SessionLocal()
    new_student = Student(name=name)
    db.add(new_student)
    db.commit()
    db.refresh(new_student)
    db.close()

    await message.answer(f"Ученик {name} добавлен с ID {new_student.id}.")

@router.message(Command("delete_student"))
async def delete_student(message: Message):

    """Удаляет ученика из базы данных по ID."""
    """Пример использования: /delete_student <id>"""

    parts = message.text.split(maxsplit=1)
    if len(parts) < 2 or not parts[1].isdigit():
        await message.nswer("Неверный формат. Используйте:\n/delete_student <id>")
        return
    
    student_id = int(parts[1])
    db = SessionLocal()
    student = db.get(Student, student_id)
    if not student:
        await message.answer(f"Ученик с ID {student_id} не найден.")
        return
    
    db.delete(student)
    db.commit()
    db.close()
    await message.answer(f"Ученик с ID {student_id} удален.")

@router.message(Command("list_students"))
async def list_students(message: Message):

    """Выводит список всех учеников в базе данных"""

    db = SessionLocal()
    students = db.query(Student).order_by(Student.id).all()
    db.close()

    if not students:
        await message.answer("Список учеников пуст.")
        return

    lines = [f"#{s.id} -- {s.name}" for s in students]
    text = "Список учеников:\n" + "\n".join(lines)
    await message.answer(text)
    