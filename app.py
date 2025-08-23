import logging
import os
import json
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Загрузка вопросов
def load_questions():
    try:
        with open('questions.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
<<<<<<< HEAD
        # Создаем минимальный пример если файла нет
=======
>>>>>>> ba62384f2d716de3da40c8a3d9f1896e006a9dfc
        default_questions = {
            "1": {
                "question": "Пример вопроса?",
                "options": ["Вариант A", "Вариант B", "Вариант C", "Вариант D"],
                "correct_answer": [0],
                "multiple": False
            }
        }
        with open('questions.json', 'w', encoding='utf-8') as f:
            json.dump(default_questions, f, ensure_ascii=False, indent=2)
        return default_questions

questions = load_questions()
user_progress = {}
user_answers = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_progress[user_id] = {"current_question": 1, "score": 0}
    user_answers[user_id] = {}
    
    keyboard = [
        [InlineKeyboardButton("Начать тест", callback_data="start_test")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "Добро пожаловать в экзаменационный бот! 🎓\n\n"
        "Тест содержит вопросы с одним и несколькими правильными ответами.\n"
        "Вопросы с несколькими правильными ответами помечены специально.\n\n"
        "Нажмите 'Начать тест' чтобы начать.",
        reply_markup=reply_markup
    )

async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    data = query.data
    
    if user_id not in user_progress:
        user_progress[user_id] = {"current_question": 1, "score": 0}
        user_answers[user_id] = {}
    
    if data == "start_test":
        await show_question(update, context, user_id, "1")
    elif data.startswith("answer_"):
        parts = data.split("_")
        question_id = parts[1]
        answer_index = int(parts[2])
        
        question = questions[question_id]
        
<<<<<<< HEAD
        # Для вопросов с множественным выбором
        if question["multiple"]:
            if user_id not in user_answers:
                user_answers[user_id] = {}
            if question_id not in user_answers[user_id]:
                user_answers[user_id][question_id] = []
            
            # Добавляем/удаляем ответ
            if answer_index in user_answers[user_id][question_id]:
                user_answers[user_id][question_id].remove(answer_index)
            else:
                user_answers[user_id][question_id].append(answer_index)
                
            # Показываем текущий выбор
            await show_multiple_choice(update, context, user_id, question_id)
        else:
            # Для одиночного выбора
            correct_answer = question["correct_answer"]
            is_correct = answer_index in correct_answer
            
            if is_correct:
                user_progress[user_id]["score"] += 1
                await show_answer_feedback(update, context, question_id, answer_index, True)
            else:
                await show_answer_feedback(update, context, question_id, answer_index, False)
            
            # Задержка перед следующим вопросом
            await asyncio.sleep(2)
            await show_next_question(context, user_id, question_id)
            
    elif data.startswith("submit_"):
        # Отправка ответов для множественного выбора
        question_id = data.split("_")[1]
        await check_multiple_answers(update, context, user_id, question_id)
        
    elif data == "restart":
        user_progress[user_id] = {"current_question": 1, "score": 0}
        user_answers[user_id] = {}
        await show_question(update, context, user_id, "1")

async def show_multiple_choice(update: Update, context: ContextTypes.DEFAULT_TYPE, 
                              user_id: int, question_id: str):
    query = update.callback_query
    question = questions[question_id]
    selected = user_answers[user_id].get(question_id, [])
    
    keyboard = []
    for i, option in enumerate(question["options"]):
        if i in selected:
            button_text = f"✅ {option}"
        else:
            button_text = f"◻️ {option}"
        keyboard.append([InlineKeyboardButton(button_text, callback_data=f"answer_{question_id}_{i}")])
    
    # Кнопка отправки
    keyboard.append([InlineKeyboardButton("✅ Отправить ответ", callback_data=f"submit_{question_id}")])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        text=f"{question['question']}\n\nВыберите все правильные ответы:",
        reply_markup=reply_markup
    )

async def check_multiple_answers(update: Update, context: ContextTypes.DEFAULT_TYPE,
                                user_id: int, question_id: str):
    query = update.callback_query
    question = questions[question_id]
    selected = user_answers[user_id].get(question_id, [])
    correct_answer = question["correct_answer"]
    
    # Сортируем для сравнения
    selected_sorted = sorted(selected)
    correct_sorted = sorted(correct_answer)
    
    is_correct = selected_sorted == correct_sorted
    
    # Подсветка правильных/неправильных ответов
    keyboard = []
    for i, option in enumerate(question["options"]):
        if i in correct_answer:
            button_text = f"✅ {option}"
        elif i in selected:
            button_text = f"❌ {option}"
        else:
            button_text = f"◻️ {option}"
        keyboard.append([InlineKeyboardButton(button_text, callback_data=f"dummy_{question_id}_{i}")])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    if is_correct:
        user_progress[user_id]["score"] += 1
        message = "✅ Все ответы правильные! Молодец!"
    else:
        message = f"❌ Неправильно! Правильные ответы: {', '.join([chr(97 + i) for i in correct_answer])}"
    
    await query.edit_message_text(
        text=f"{question['question']}\n\n{message}",
        reply_markup=reply_markup
    )
    
    # Задержка перед следующим вопросом
    await asyncio.sleep(3)
    await show_next_question(context, user_id, question_id)
=======
        if answer_index == correct_answer:
            user_progress[user_id]["score"] += 1
            await show_answer_feedback(update, context, question_id, answer_index, True)
        else:
            await show_answer_feedback(update, context, question_id, answer_index, False)
        
        # Задержка перед следующим вопросом
        await asyncio.sleep(2)
        await show_next_question(context, user_id, question_id)
        
    elif data == "restart":
        user_progress[user_id] = {"current_question": 1, "score": 0}
        await show_question(update, context, user_id, "1")
>>>>>>> ba62384f2d716de3da40c8a3d9f1896e006a9dfc

async def show_answer_feedback(update: Update, context: ContextTypes.DEFAULT_TYPE, 
                             question_id: str, answer_index: int, is_correct: bool):
    query = update.callback_query
    question = questions[question_id]
    correct_answer = question["correct_answer"]
    
    keyboard = []
    for i, option in enumerate(question["options"]):
        if i == answer_index:
            if is_correct:
                button_text = f"✅ {option}"
            else:
                button_text = f"❌ {option}"
        elif i in correct_answer:
            button_text = f"✅ {option}"
        else:
            button_text = f"◻️ {option}"
            
        keyboard.append([InlineKeyboardButton(button_text, callback_data=f"dummy_{question_id}_{i}")])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    if is_correct:
        message = "✅ Правильно! Молодец!"
    else:
        message = f"❌ Неправильно! Правильный ответ: {', '.join([chr(97 + i) for i in correct_answer])}"
    
    await query.edit_message_text(
        text=f"{question['question']}\n\n{message}",
        reply_markup=reply_markup
    )

async def show_next_question(context, user_id, current_question_id):
    next_question_id = str(int(current_question_id) + 1)
    
    if next_question_id in questions:
        user_progress[user_id]["current_question"] = int(next_question_id)
        await show_question(None, context, user_id, next_question_id)
    else:
        score = user_progress[user_id]["score"]
        total = len(questions)
        
        keyboard = [
            [InlineKeyboardButton("Начать заново", callback_data="restart")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await context.bot.send_message(
            chat_id=user_id,
            text=f"🎉 Тест завершен!\nВаш результат: {score}/{total}\n\n"
                 f"Процент правильных ответов: {round(score/total*100)}%",
            reply_markup=reply_markup
        )

async def show_question(update: Update, context: ContextTypes.DEFAULT_TYPE, 
                       user_id: int, question_id: str):
    question = questions[str(question_id)]
    
    keyboard = []
    for i, option in enumerate(question["options"]):
        keyboard.append([
            InlineKeyboardButton(
                f"{['A', 'B', 'C', 'D'][i]}. {option}", 
                callback_data=f"answer_{question_id}_{i}"
            )
        ])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    text = f"Вопрос {question_id}/{len(questions)}\n\n{question['question']}"
    if question["multiple"]:
        text += "\n\n⚠️ Выберите ВСЕ правильные ответы!"
    
    if update and update.callback_query:
        await update.callback_query.edit_message_text(text, reply_markup=reply_markup)
    else:
        await context.bot.send_message(user_id, text, reply_markup=reply_markup)

def main():
    TOKEN = os.getenv('TELEGRAM_TOKEN')
    if not TOKEN:
        logger.error("Токен не найден! Установите переменную окружения TELEGRAM_TOKEN")
        return
    
    application = Application.builder().token(TOKEN).build()
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(handle_callback))
    
    logger.info("Бот запущен!")
    application.run_polling()

if __name__ == "__main__":
    main()
