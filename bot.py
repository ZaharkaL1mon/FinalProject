import logging
from telegram import ReplyKeyboardMarkup, Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext
from config import BOT_TOKEN
from SQLiteintegration import get_careers, get_career, save_user, get_recommendations


logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)


MAIN_MENU = ReplyKeyboardMarkup([
    ['Найти профессию', 'Заполнить анкету'],
    ['Мои результаты', 'Помощь']
], resize_keyboard=True)

async def start(update: Update, context: CallbackContext):
    context.user_data.clear()
    await update.message.reply_text(
        "Привет! Я бот‑советчик по выбору карьеры. Чем могу помочь?",
        reply_markup=MAIN_MENU
    )

async def handle_message(update: Update, context: CallbackContext):
    original_text = update.message.text
    text = original_text.strip().lower()
    user_id = update.effective_user.id

    logger.info(f"Получено сообщение: '{original_text}', шаг: {context.user_data.get('step')}")

    if text == 'найти профессию':
        careers = get_careers()
        if careers:
            careers_list = "\n".join([f"• {c}" for c in careers])
            await update.message.reply_text(f"Доступные профессии:\n{careers_list}\n\nНапишите название профессии для подробной информации.", reply_markup=MAIN_MENU)
        else:
            await update.message.reply_text("В базе пока нет профессий.", reply_markup=MAIN_MENU)

    elif text == 'заполнить анкету':
        context.user_data.clear()
        context.user_data['step'] = 'age'
        await update.message.reply_text("Сколько вам лет? (например: 16, 25, 30)")

    elif text == 'мои результаты':
        logger.info(f"Запрос рекомендаций для пользователя {user_id}")
        recs = get_recommendations(user_id)
        if recs:
            logger.info(f"Рекомендации найдены: {recs}")
            await update.message.reply_text(f"Ваши рекомендации:\n{recs}", reply_markup=MAIN_MENU)
        else:
            logger.info("Рекомендации не найдены для пользователя")
            await update.message.reply_text("Вы ещё не заполнили анкету. Используйте 'Заполнить анкету'.", reply_markup=MAIN_MENU)

    elif text == 'помощь':
        await update.message.reply_text(
            "Я помогу подобрать профессию по вашим интересам.\n"
            "Используйте меню:\n"
            "- 'Найти профессию' — посмотреть все профессии\n"
            "- 'Заполнить анкету' — получить персональные рекомендации\n"
            "- 'Мои результаты' — посмотреть свои рекомендации",
            reply_markup=MAIN_MENU
        )

    else:
        career_info = get_career(original_text)
        if career_info:
            response = (
                f"💼 {career_info['название']}\n\n"
                f"📝 {career_info['описание']}\n\n"
                f"🛠️ Навыки: {career_info['навыки']}\n"
                f"📚 Образование: {career_info['образование']}\n"
                f"💰 Зарплата: {career_info['зарплата']}\n"
                f"🚀 Перспективы: {career_info['перспективы']}"
            )
            await update.message.reply_text(response, reply_markup=MAIN_MENU)
            return

        step = context.user_data.get('step')

        if step == 'age':
            if text.isdigit() and 10 <= int(text) <= 80:
                context.user_data['age'] = text
                context.user_data['step'] = 'experience'
                await update.message.reply_text("Есть ли опыт работы? (Да/Нет)")
            else:
                await update.message.reply_text("Пожалуйста, введите корректный возраст (число от 10 до 80):")

        elif step == 'experience':
            text_lower = text.lower()
            if text_lower in ['да', 'нет']:
                context.user_data['experience'] = text_lower
                context.user_data['step'] = 'interests'
                await update.message.reply_text("Что вам больше нравится: творчество, аналитика или общение?")
            else:
                await update.message.reply_text("Пожалуйста, ответьте 'Да' или 'Нет':")

        elif step == 'interests':
            logger.info(f"Обработка интересов: '{text}'")
            all_careers = get_careers()
            recommendations = []
            text_lower = text.lower()

            if 'аналитик' in text_lower or 'аналитика' in text_lower:
                categories = ['IT', 'Инженерия', 'Авиация']
                for career in all_careers:
                    career_info = get_career(career)
                    if career_info and career_info.get('категория') in categories:
                        recommendations.append(career)
            elif 'творч' in text_lower or 'творчество' in text_lower:
                categories = ['Дизайн', 'Архитектура']
                for career in all_careers:
                    career_info = get_career(career)
                    if career_info and career_info.get('категория') in categories:
                        recommendations.append(career)
            elif 'общ' in text_lower or 'общение' in text_lower:
                categories = ['Маркетинг', 'Образование', 'Медицина']
                for career in all_careers:
                    career_info = get_career(career)
                    if career_info and career_info.get('категория') in categories:
                        recommendations.append(career)
            else:
                await update.message.reply_text(
                    "Не совсем понял ваш ответ. "
            "Пожалуйста, выберите: творчество, аналитика или общение."
                )
                return

            if recommendations:
                recs = "Рекомендуем: " + ", ".join(recommendations)
            else:
                recs = "Пока не удалось подобрать точных рекомендаций. Посмотрите все доступные профессии в разделе 'Найти профессию'."


            age = context.user_data.get('age', 'не указано')
            exp = context.user_data.get('experience', 'не указано')
            save_user(user_id, age, exp, text, recs)
            context.user_data.clear()
            await update.message.reply_text(f"Спасибо! Ваши рекомендации:\n{recs}", reply_markup=MAIN_MENU)
        else:
            await update.message.reply_text("Используйте кнопки меню.", reply_markup=MAIN_MENU)


def main():
    try:
        application = Application.builder().token(BOT_TOKEN).build()
        application.add_handler(CommandHandler("start", start))
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
        logger.info("Бот запущен! Ожидаю сообщений...")
        application.run_polling()
    except Exception as e:
        logger.error(f"Ошибка запуска: {e}")
        print("Проверьте токен в config.py и интернет‑соединение.")

if __name__ == '__main__':
    main()
 #Запуск: python SQLiteintegration.py(1)  python bot.py(3) python careers.py(2)