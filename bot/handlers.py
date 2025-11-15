from aiogram import Router, types, F
from aiogram.filters import CommandStart, StateFilter
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from utils.localization import localization

router = Router()

CHOICE_TO_KEY = {
    "choice1": "technical_faq",
    "choice2": "feature_faq",
    "choice3": "payment_faq",
}

class HelpFlow(StatesGroup):
    browsing = State()
    support = State()
    waitingForTicketMessage = State()

# //////////////////////////
# Клавиатуры
# //////////////////////////

def main_keyboard(lang: str) -> InlineKeyboardMarkup:
    buttons = []
    i = 1
    while True:
        choice = localization.get(f"choice{i}", lang)
        if choice is None:
            break
        buttons.append([InlineKeyboardButton(text=choice, callback_data=f"choice{i}")])
        i += 1
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def categories_keyboard(lang: str) -> InlineKeyboardMarkup:
    cats = localization.categories(lang)
    buttons = []
    for cid, meta in cats.items():
        title = meta.get("display_name", cid)
        buttons.append([InlineKeyboardButton(text=title, callback_data=f"cat:{cid}")])
    buttons.append([InlineKeyboardButton(text=localization.get("back_to_menu", lang), callback_data="back_to_menu")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def options_keyboard(lang: str, category_id: str, q_index: int, options: list[str]) -> InlineKeyboardMarkup:
    rows = []
    for i, opt in enumerate(options):
        rows.append([InlineKeyboardButton(text=opt, callback_data=f"sup:{category_id}:q:{q_index}:ans:{i}")])
    rows.append([InlineKeyboardButton(text=localization.get("back_to_menu", lang), callback_data="back_to_menu")])
    return InlineKeyboardMarkup(inline_keyboard=rows)

def finish_keyboard(lang: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=localization.get("back_to_menu", lang), callback_data="back_to_menu")],
        ]
    )

# //////////////////////////
# Старт/меню/FAQ
# //////////////////////////

@router.message(CommandStart())
async def start_command(msg: types.Message, state: FSMContext):
    tg_lang = (msg.from_user.language_code or "").lower() if msg.from_user else ""
    user_lang = "ru" if tg_lang.startswith("ru") else "en"

    await state.set_state(HelpFlow.browsing)
    await state.update_data(lang=user_lang, pending=None)

    await msg.answer(
        localization.get("start_message", user_lang),
        reply_markup=main_keyboard(user_lang)
    )

@router.callback_query(F.data.in_(set(CHOICE_TO_KEY)), StateFilter(HelpFlow.browsing))
async def handle_faq_choices(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    lang = data.get("lang", "en")
    key = CHOICE_TO_KEY[callback.data]

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text=localization.get("back_to_menu", lang), callback_data="back_to_menu")]]
    )
    await callback.message.edit_text(localization.get(key, lang), reply_markup=keyboard)
    await callback.answer()

@router.callback_query(F.data == "choice5", StateFilter(HelpFlow.browsing))  # Переключение языка
async def toggle_language(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    current_lang = data.get("lang", "en")
    new_lang = "ru" if current_lang == "en" else "en"

    await state.update_data(lang=new_lang)
    await callback.message.edit_text(
        localization.get("start_message", new_lang),
        reply_markup=main_keyboard(new_lang)
    )
    await callback.answer()

@router.callback_query(F.data == "back_to_menu")
async def back_to_menu(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    lang = data.get("lang", "en")
    await state.set_state(HelpFlow.browsing)
    await state.update_data(pending=None, ticket_data=None)
    await callback.message.edit_text(
        localization.get("start_message", lang),
        reply_markup=main_keyboard(lang)
    )
    await callback.answer()

# //////////////////////////
# Саппорт: пошаговый выбор
# //////////////////////////

@router.callback_query(F.data == "choice4", StateFilter(HelpFlow.browsing))  # Contact support
async def start_ticket_flow(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    lang = data.get("lang", "en")

    await state.set_state(HelpFlow.support)
    await state.update_data(pending=None, ticket_data=None)
    await callback.message.edit_text(
        localization.get("ticket_question", lang),
        reply_markup=categories_keyboard(lang)
    )
    await callback.answer()

@router.callback_query(F.data.startswith("cat:"), StateFilter(HelpFlow.support))
async def pick_category(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    lang = data.get("lang", "en")
    category_id = callback.data.split(":", 1)[1]
    
    # Инициализируем структуру для хранения данных тикета
    category_name = localization.category_display_name(category_id, lang)
    await state.update_data(
        pending=None,
        ticket_data={
            "category_id": category_id,
            "category_name": category_name,
            "answers": []  # Список словарей {"question": "...", "answer": "..."}
        }
    )
    
    await ask_question(callback, state, lang, category_id, q_index=0)
    await callback.answer()

@router.callback_query(F.data.startswith("sup:"), StateFilter(HelpFlow.support))
async def handle_support_callbacks(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    lang = data.get("lang", "en")

    # sup:<category_id>:q:<index>:ans:<optIndex>
    parts = callback.data.split(":")
    if len(parts) < 4 or parts[0] != "sup" or parts[2] != "q":
        await callback.answer()
        return

    category_id = parts[1]
    try:
        q_index = int(parts[3])
    except ValueError:
        await callback.answer()
        return

    # Сохраняем ответ пользователя
    action = parts[4] if len(parts) >= 5 else None
    if action == "ans":
        opt_index = int(parts[5]) if len(parts) >= 6 else 0
        questions = localization.category_questions(category_id, lang)
        if questions and q_index < len(questions):
            q = questions[q_index]
            q_text = q.get("text", "Question")
            opts = q.get("options") or []
            if opt_index < len(opts):
                selected_option = opts[opt_index]
                
                # Добавляем ответ в структуру данных
                ticket_data = data.get("ticket_data", {})
                if not ticket_data.get("answers"):
                    ticket_data["answers"] = []
                
                ticket_data["answers"].append({
                    "question": q_text,
                    "answer": selected_option,
                    "question_index": q_index
                })
                
                await state.update_data(ticket_data=ticket_data)

    # Переходим к следующему вопросу
    if action == "ans":
        await ask_question(callback, state, lang, category_id, q_index=q_index + 1)
    else:
        await ask_question(callback, state, lang, category_id, q_index=q_index)

    await callback.answer()

@router.message(StateFilter(HelpFlow.waitingForTicketMessage))
async def handle_ticket_message(msg: types.Message, state: FSMContext):
    data = await state.get_data()
    lang = data.get("lang", "en")
    
    # Получаем все собранные данные
    ticket_data = data.get("ticket_data", {})
    ticket_text = msg.text
    
    # Добавляем финальное описание в структуру
    ticket_data["user_description"] = ticket_text
    ticket_data["user_id"] = msg.from_user.id
    ticket_data["username"] = msg.from_user.username
    
    # ===== ВОТ ЗДЕСЬ У ТЕБЯ БУДЕТ ВСЯ ИНФА ДЛЯ ОТПРАВКИ НА САЙТ =====
    # ticket_data = {
    #     "category_id": "...",
    #     "category_name": "...",
    #     "answers": [
    #         {"question": "...", "answer": "...", "question_index": 0},
    #         {"question": "...", "answer": "...", "question_index": 1},
    #     ],
    #     "user_description": "текст от пользователя",
    #     "user_id": 123456,
    #     "username": "username"
    # }
    
    # TODO: Здесь отправка на сайт
    # await send_ticket_to_website(ticket_data)
    
    await msg.answer(localization.get("FinalMess", lang), reply_markup=main_keyboard(lang))
    await state.set_state(HelpFlow.browsing)
    await state.update_data(pending=None, ticket_data=None)


# //////////////////////////
# Хелперы
# //////////////////////////

async def ask_question(source: types.Union[CallbackQuery, types.Message], state: FSMContext, lang: str, category_id: str, q_index: int):
    data = await state.get_data()
    questions = localization.category_questions(category_id, lang)
    
    # Если вопросы закончились, просим описать проблему
    if not questions or q_index >= len(questions):
        summary = localization.get("describe", lang)
        
        await state.set_state(HelpFlow.waitingForTicketMessage)
        
        kb = finish_keyboard(lang)
        if isinstance(source, CallbackQuery):
            await source.message.edit_text(summary, reply_markup=kb)
        else:
            await source.answer(summary, reply_markup=kb)
        return

    q = questions[q_index]
    q_text = q.get("text", "")
    opts = q.get("options") or []

    # Все вопросы только с опциями (keyboard)
    kb = options_keyboard(lang, category_id, q_index, opts)
    if isinstance(source, CallbackQuery):
        await source.message.edit_text(q_text, reply_markup=kb)
    else:
        await source.answer(q_text, reply_markup=kb)