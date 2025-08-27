from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def main_menu_kb() -> InlineKeyboardMarkup:
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📋 Просмотреть", callback_data="students:view")],
        [InlineKeyboardButton(text="➕ Добавить", callback_data="students:add")],
        [InlineKeyboardButton(text="✏️ Редактировать", callback_data="students:edit")],
    [InlineKeyboardButton(text="🗑️ Удалить", callback_data="students:delete")],
    [InlineKeyboardButton(text="❌ Выйти", callback_data="students:exit")],
    ])
    return kb


def students_list_kb(students, mode: str = "view") -> InlineKeyboardMarkup:
    """Возвращает клавиатуру со списком учеников.
    mode: 'view'|'edit'|'delete' — формирует callback_data соответственно.
    """
    buttons = []
    for s in students:
        if mode == "edit":
            cb = f"students:edit:{s.id}"
        elif mode == "delete":
            cb = f"students:delete:{s.id}"
        else:
            cb = f"students:view:{s.id}"
        buttons.append([InlineKeyboardButton(text=f"#{s.id} {s.name}", callback_data=cb)])

    # кнопка назад
    buttons.append([InlineKeyboardButton(text="⬅️ Назад", callback_data="students:menu")])

    return InlineKeyboardMarkup(inline_keyboard=buttons)
