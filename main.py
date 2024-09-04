import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackContext, filters
import random

# Включите логирование, чтобы видеть ошибки и информацию о работе бота
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

# Список неправильных глаголов и их переводов
irregular_verbs = {
    'arise': 'возникать',
    'awake': 'просыпаться',
    'be': 'быть',
    'bear': 'нести',
    'beat': 'бить',
    'become': 'становиться',
    'begin': 'начинать',
    'bend': 'гнуть',
    'bet': 'ставить',
    'bid': 'предлагать',
    'bind': 'связывать',
    'bite': 'кусать',
    'bleed': 'кровоточить',
    'blow': 'дуть',
    'break': 'ломать',
    'bring': 'приносить',
    'broadcast': 'вещать',
    'build': 'строить',
    'burn': 'сжигать',
    'buy': 'покупать',
    'catch': 'ловить',
    'choose': 'выбирать',
    'cling': 'цепляться',
    'come': 'приходить',
    'cost': 'стоить',
    'creep': 'красться',
    'cut': 'резать',
    'deal': 'иметь дело',
    'dig': 'копать',
    'do': 'делать',
    'draw': 'рисовать',
    'dream': 'мечтать',
    'drink': 'пить',
    'drive': 'водить',
    'eat': 'есть',
    'fall': 'падать',
    'feed': 'кормить',
    'feel': 'чувствовать',
    'fight': 'бороться',
    'find': 'находить',
    'flee': 'бежать',
    'fling': 'бросать',
    'fly': 'летать',
    'forbid': 'запрещать',
    'forget': 'забывать',
    'forgive': 'прощать',
    'freeze': 'замерзать',
    'get': 'получать',
    'give': 'давать',
    'go': 'идти',
    'grow': 'расти',
    'hang': 'вешать',
    'have': 'иметь',
    'hear': 'слышать',
    'hide': 'прятать',
    'hit': 'ударять',
    'hold': 'держать',
    'hurt': 'ранить',
    'keep': 'сохранять',
    'know': 'знать',
    'lay': 'класть',
    'lead': 'вести',
    'lean': 'опираться',
    'leap': 'прыгать',
    'leave': 'уходить',
    'lend': 'одалживать',
    'let': 'позволять',
    'lie': 'лежать',
    'light': 'светить',
    'lose': 'терять',
    'make': 'делать',
    'mean': 'означать',
    'meet': 'встречать',
    'mow': 'косить',
    'overcome': 'преодолевать',
    'pay': 'платить',
    'put': 'класть',
    'quit': 'бросать',
    'read': 'читать',
    'ride': 'ехать',
    'ring': 'звонить',
    'rise': 'восходить',
    'run': 'бежать',
    'say': 'сказать',
    'see': 'видеть',
    'sell': 'продавать',
    'send': 'отправлять',
    'set': 'устанавливать',
    'sew': 'шить',
    'shake': 'трясти',
    'shine': 'светить',
    'shoot': 'стрелять',
    'show': 'показывать',
    'shrink': 'сжиматься',
    'shut': 'закрывать',
    'sing': 'петь',
    'sink': 'тонуть',
    'sit': 'сидеть',
    'sleep': 'спать',
    'slide': 'скользить',
    'speak': 'говорить',
    'spend': 'тратить',
    'spill': 'проливать',
    'spin': 'крутить',
    'split': 'разделять',
    'spread': 'распространять',
    'stand': 'стоять',
    'steal': 'воровать',
    'stick': 'приклеивать',
    'sting': 'жалить',
    'stink': 'вонять',
    'strike': 'ударять',
    'swear': 'клясться',
    'sweep': 'подметать',
    'swim': 'плавать',
    'take': 'брать',
    'teach': 'учить',
    'tear': 'рвать',
    'tell': 'рассказывать',
    'think': 'думать',
    'throw': 'бросать',
    'understand': 'понимать',
    'wake': 'будить',
    'wear': 'носить',
    'win': 'выигрывать',
    'write': 'писать',
}

# Выбирает случайный глагол
def get_random_verb():
    verb = random.choice(list(irregular_verbs.keys()))
    return verb, irregular_verbs[verb]

async def start(update: Update, context: CallbackContext) -> None:
    if 'lesson_active' in context.user_data and context.user_data['lesson_active']:
        await update.message.reply_text("Урок уже активен.")
        return

    context.user_data['lesson_active'] = True
    context.user_data['verbs'] = list(irregular_verbs.keys())
    random.shuffle(context.user_data['verbs'])
    context.user_data['incorrect_answers'] = []

    # Отправляем первое задание
    await send_next_verb(update, context)

async def stop(update: Update, context: CallbackContext) -> None:
    if 'lesson_active' not in context.user_data or not context.user_data['lesson_active']:
        await update.message.reply_text("Урок не активен.")
        return

    context.user_data['lesson_active'] = False

    # Отправляем сообщение по окончании урока
    await update.message.reply_text("Урок окончен. Ты молодец!")

    # Отправляем неправильные ответы
    for verb, user_input in context.user_data.get('incorrect_answers', []):
        correct_forms = get_correct_forms(verb)
        await update.message.reply_text(f"Вы неправильно ответили на глагол: {verb}. Правильные формы: {correct_forms}")

async def send_next_verb(update: Update, context: CallbackContext) -> None:
    if not context.user_data.get('lesson_active', False):
        return

    if not context.user_data['verbs']:
        # Если глаголы закончились, завершаем урок
        await stop(update, context)
        return

    verb = context.user_data['verbs'].pop(0)
    translation = irregular_verbs[verb]
    context.user_data['current_verb'] = verb
    context.user_data['current_translation'] = translation

    await update.message.reply_text(
        f"Неправильный глагол: {verb}\nПеревод: {translation}\nВведите три формы этого глагола (например, do did done)."
    )

async def check_verbs(update: Update, context: CallbackContext) -> None:
    if 'lesson_active' not in context.user_data or not context.user_data['lesson_active']:
        await update.message.reply_text("Урок не активен. Используйте команду /start для начала урока.")
        return

    if 'current_verb' not in context.user_data:
        await update.message.reply_text("Ожидается новое задание. Используйте команду /start для начала.")
        return

    correct_verb = context.user_data['current_verb']
    correct_forms = get_correct_forms(correct_verb)
    user_input = update.message.text.strip().lower()

    # Сравниваем пользовательский ввод с правильными формами, приведенными к нижнему регистру
    if user_input == correct_forms.lower():
        await update.message.reply_text("Правильно!")
    else:
        await update.message.reply_text(f"Неправильно. Правильные формы: {correct_forms}")
        context.user_data.setdefault('incorrect_answers', []).append((correct_verb, user_input))

    # Отправляем следующее задание
    await send_next_verb(update, context)

def get_correct_forms(verb):
    forms = {
        'arise': 'arise arose arisen',
        'awake': 'awake awoke awoken',
        'be': 'be was/were been',
        'bear': 'bear bore born',
        'beat': 'beat beat beaten',
        'become': 'become became become',
        'begin': 'begin began begun',
        'bend': 'bend bent bent',
        'bet': 'bet bet bet',
        'bid': 'bid bid bid',
        'bind': 'bind bound bound',
        'bite': 'bite bit bitten',
        'bleed': 'bleed bled bled',
        'blow': 'blow blew blown',
        'break': 'break broke broken',
        'bring': 'bring brought brought',
        'broadcast': 'broadcast broadcast broadcast',
        'build': 'build built built',
        'burn': 'burn burned/burnt burned/burnt',
        'buy': 'buy bought bought',
        'catch': 'catch caught caught',
        'choose': 'choose chose chosen',
        'cling': 'cling clung clung',
        'come': 'come came come',
        'cost': 'cost cost cost',
        'creep': 'creep crept crept',
        'cut': 'cut cut cut',
        'deal': 'deal dealt dealt',
        'dig': 'dig dug dug',
        'do': 'do did done',
        'draw': 'draw drew drawn',
        'dream': 'dream dreamed/dreamt dreamed/dreamt',
        'drink': 'drink drank drunk',
        'drive': 'drive drove driven',
        'eat': 'eat ate eaten',
        'fall': 'fall fell fallen',
        'feed': 'feed fed fed',
        'feel': 'feel felt felt',
        'fight': 'fight fought fought',
        'find': 'find found found',
        'flee': 'flee fled fled',
        'fling': 'fling flung flung',
        'fly': 'fly flew flown',
        'forbid': 'forbid forbade forbidden',
        'forget': 'forget forgot forgotten',
        'forgive': 'forgive forgave forgiven',
        'freeze': 'freeze froze frozen',
        'get': 'get got gotten/got',
        'give': 'give gave given',
        'go': 'go went gone',
        'grow': 'grow grew grown',
        'hang': 'hang hung hung',
        'have': 'have had had',
        'hear': 'hear heard heard',
        'hide': 'hide hid hidden',
        'hit': 'hit hit hit',
        'hold': 'hold held held',
        'hurt': 'hurt hurt hurt',
        'keep': 'keep kept kept',
        'know': 'know knew known',
        'lay': 'lay laid laid',
        'lead': 'lead led led',
        'lean': 'lean leaned/leant leaned/leant',
        'leap': 'leap leapt leapt',
        'leave': 'leave left left',
        'lend': 'lend lent lent',
        'let': 'let let let',
        'lie': 'lie lay lain',
        'light': 'light lit/lighted lit/lighted',
        'lose': 'lose lost lost',
        'make': 'make made made',
        'mean': 'mean meant meant',
        'meet': 'meet met met',
        'mow': 'mow mowed mowed/mown',
        'overcome': 'overcome overcame overcome',
        'pay': 'pay paid paid',
        'put': 'put put put',
        'quit': 'quit quit quit',
        'read': 'read read read',
        'ride': 'ride rode ridden',
        'ring': 'ring rang rung',
        'rise': 'rise rose risen',
        'run': 'run ran run',
        'say': 'say said said',
        'see': 'see saw seen',
        'sell': 'sell sold sold',
        'send': 'send sent sent',
        'set': 'set set set',
        'sew': 'sew sewed sewn/sewed',
        'shake': 'shake shook shaken',
        'shine': 'shine shone shone',
        'shoot': 'shoot shot shot',
        'show': 'show showed shown',
        'shrink': 'shrink shrank shrunk',
        'shut': 'shut shut shut',
        'sing': 'sing sang sung',
        'sink': 'sink sank sunk',
        'sit': 'sit sat sat',
        'sleep': 'sleep slept slept',
        'slide': 'slide slid slid',
        'speak': 'speak spoke spoken',
        'spend': 'spend spent spent',
        'spill': 'spill spilled/spilt spilled/spilt',
        'spin': 'spin spun spun',
        'split': 'split split split',
        'spread': 'spread spread spread',
        'stand': 'stand stood stood',
        'steal': 'steal stole stolen',
        'stick': 'stick stuck stuck',
        'sting': 'sting stung stung',
        'stink': 'stink stank stunk',
        'strike': 'strike struck struck',
        'swear': 'swear swore sworn',
        'sweep': 'sweep swept swept',
        'swim': 'swim swam swum',
        'take': 'take took taken',
        'teach': 'teach taught taught',
        'tear': 'tear tore torn',
        'tell': 'tell told told',
        'think': 'think thought thought',
        'throw': 'throw threw thrown',
        'understand': 'understand understood understood',
        'wake': 'wake woke woken',
        'wear': 'wear wore worn',
        'win': 'win won won',
        'write': 'write wrote written',
    }
    return forms.get(verb, '')

async def check_verbs(update: Update, context: CallbackContext) -> None:
    if 'lesson_active' not in context.user_data or not context.user_data['lesson_active']:
        await update.message.reply_text("Урок не активен. Используйте команду /start для начала урока.")
        return

    if 'current_verb' not in context.user_data:
        await update.message.reply_text("Ожидается новое задание. Используйте команду /start для начала.")
        return

    correct_verb = context.user_data['current_verb']
    correct_forms = get_correct_forms(correct_verb)
    user_input = update.message.text.strip().lower()

    # Сравниваем пользовательский ввод с правильными формами, приведенными к нижнему регистру
    if user_input == correct_forms.lower():
        await update.message.reply_text("Правильно!")
    else:
        await update.message.reply_text(f"Неправильно. Правильные формы: {correct_forms}")
        context.user_data.setdefault('incorrect_answers', []).append((correct_verb, user_input))

    # Отправляем следующее задание
    await send_next_verb(update, context)

def main() -> None:
    # Вставьте сюда ваш токен
    TOKEN = '????'

    application = Application.builder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("stop", stop))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, check_verbs))

    application.run_polling()

if __name__ == '__main__':
    main()
