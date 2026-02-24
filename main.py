from logic import DB_Manager
from config import *
from telebot import TeleBot
from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from telebot import types

bot = TeleBot(TOKEN)
hideBoard = types.ReplyKeyboardRemove() 

cancel_button = "Отмена 🚫"

def cansel(message):
    """Отменяет текущее действие и показывает сообщение."""
    bot.send_message(message.chat.id, "Чтобы посмотреть команды, используй - /info", reply_markup=hideBoard)

def no_projects(message):
    """Сообщает пользователю, что у него нет сыров."""
    bot.send_message(message.chat.id, 'У тебя пока нет сыров!\nМожешь добавить их с помощью команды /new_cheese')

def gen_inline_markup(rows):
    """Создает инлайн-клавиатуру."""
    markup = InlineKeyboardMarkup()
    markup.row_width = 1
    for row in rows:
        markup.add(InlineKeyboardButton(row, callback_data=row))
    return markup

def gen_markup(rows):
    """Создает клавиатуру с одноразовым использованием."""
    markup = ReplyKeyboardMarkup(one_time_keyboard=True)
    markup.row_width = 1
    for row in rows:
        markup.add(KeyboardButton(row))
    markup.add(KeyboardButton(cancel_button))
    return markup

attributes_of_projects = {
    'Название сыра': ["Введите новое имя сыра", "project_name"],
    'Описание': ["Введите новое описание сыра", "description"],
    'Рекомендация': ["Введите, с чем вы бы порекомендовали сыр", "recommendations"],
    'Ссылка': ["Введите новую ссылку на ваш вкусный сыр", "url"],
    'Статус': ["Выберите новый статус сыра", "status_id"]
}

def info_project(message, user_id, project_name):
    """Отправляет информацию о проекте пользователю."""
    info = manager.get_project_info(user_id, project_name)[0]
    skills = manager.get_project_skills(project_name)
    if not skills:
        skills = 'Навыки пока не добавлены'
    bot.send_message(message.chat.id, f"""Cheese name: {info[0]}
Description: {info[1]}
Recommendations: {info[2]}
Link: {info[3]}
Status: {info[4]}
Skills: {skills}
""")

@bot.message_handler(commands=['start'])
def start_command(message):
    """Запускает бота и приветствует пользователя."""
    bot.send_message(message.chat.id, """👋 Привет! Я бот-менеджер вашего сыра
Помогу тебе сохранить твои сыры и информацию о них! 📁
Используй /info, если хочешь знать команды 📜
""")
    info(message)

@bot.message_handler(commands=['info'])
def info(message):
    """Отправляет информацию о командах сырах."""
    bot.send_message(message.chat.id,
"""
Вот команды которые могут тебе помочь:

/new_cheese - используй для добавления нового сыра
/skills - выбери навык для сыра
/cheeses - посмотри все свои вкусные сыры
/delete - удали сыр (пощади беднягу)
/update_cheeses - обнови информацию о проекте
Также ты можешь ввести имя проекта и узнать информацию о нем!
""")

@bot.message_handler(commands=['new_cheese'])
def addtask_command(message):
    """Запускает процесс добавления нового сыра."""
    bot.send_message(message.chat.id, "Введите название сыра:")
    bot.register_next_step_handler(message, name_project)

def name_project(message):
    """Сохраняет название сыра и запрашивает ссылку."""
    name = message.text
    user_id = message.from_user.id
    data = [user_id, name]
    bot.send_message(message.chat.id, "Введите ссылку на ваш вкусный сыр")
    bot.register_next_step_handler(message, link_project, data=data)

def recommend_cheeses(message):
    """Сохраняет рекомендации сыра."""
    recommendation = message.text 
    user_id = message.from_user.id
    data = [user_id, recommendation]
    bot.send_message(message.chat.id, "Введите рекоммендации к вашему сыру")
    bot.register_next_step_handler(message, link_project, data=data)

def link_project(message, data):
    """Сохраняет ссылку на сыр."""
    data.append(message.text)
    statuses = [x[0] for x in manager.get_statuses()] 
    bot.send_message(message.chat.id, "Введите текущий статус сыра", reply_markup=gen_markup(statuses))
    bot.register_next_step_handler(message, callback_project, data=data, statuses=statuses)

def callback_project(message, data, statuses):
    """Сохраняет статус сыра и добавляет проект в базу данных."""
    status = message.text
    if message.text == cancel_button:
        cansel(message)
        return
    if status not in statuses:
        bot.send_message(message.chat.id, "Ты выбрал статус не из списка, попробуй еще раз!)", reply_markup=gen_markup(statuses))
        bot.register_next_step_handler(message, callback_project, data=data, statuses=statuses)
        return
    status_id = manager.get_status_id(status)
    data.append(status_id)
    manager.insert_project([tuple(data)])
    bot.send_message(message.chat.id, "сыр сохранен")

@bot.message_handler(commands=['skills'])
def skill_handler(message):
    """Запрашивает навыки для сыра."""
    user_id = message.from_user.id
    projects = manager.get_projects(user_id)
    if projects:
        projects = [x[2] for x in projects]
        bot.send_message(message.chat.id, 'Выбери сыр для которого нужно выбрать навык', reply_markup=gen_markup(projects))
        bot.register_next_step_handler(message, skill_project, projects=projects)
    else:
        no_projects(message)

def skill_project(message, projects):
    """Выбирает сыр для добавления навыка."""
    project_name = message.text
    if message.text == cancel_button:
        cansel(message)
        return
        
    if project_name not in projects:
        bot.send_message(message.chat.id, 'У тебя нет такого сыра, попробуй еще раз!) Выбери сыр для которого нужно выбрать навык', reply_markup=gen_markup(projects))
        bot.register_next_step_handler(message, skill_project, projects=projects)
    else:
        skills = [x[1] for x in manager.get_skills()]
        bot.send_message(message.chat.id, 'Выбери навык', reply_markup=gen_markup(skills))
        bot.register_next_step_handler(message, set_skill, project_name=project_name, skills=skills)

def set_skill(message, project_name, skills):
    """Добавляет навык к сыру."""
    skill = message.text
    user_id = message.from_user.id
    if message.text == cancel_button:
        cansel(message)
        return
        
    if skill not in skills:
        bot.send_message(message.chat.id, 'Видимо, ты выбрал навык не из списка, попробуй еще раз!) Выбери навык', reply_markup=gen_markup(skills))
        bot.register_next_step_handler(message, set_skill, project_name=project_name, skills=skills)
        return
    manager.insert_skill(user_id, project_name, skill)
    bot.send_message(message.chat.id, f'Навык {skill} добавлен сыру {project_name}')

@bot.message_handler(commands=['cheeses'])
def get_projects(message):
    """Отправляет список сыров пользователя."""
    user_id = message.from_user.id
    projects = manager.get_projects(user_id)
    if projects:
        text = "\n".join([f"Project name: {x[2]} \nLink: {x[4]}\n" for x in projects])
        bot.send_message(message.chat.id, text, reply_markup=gen_inline_markup([x[2] for x in projects]))
    else:
        no_projects(message)

@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    """Обрабатывает нажатия на инлайн-кнопки."""
    project_name = call.data
    info_project(call.message, call.from_user.id, project_name)

@bot.message_handler(commands=['delete'])
def delete_handler(message):
    """Запускает процесс удаления сыра."""
    user_id = message.from_user.id
    projects = manager.get_projects(user_id)
    if projects:
        text = "\n".join([f"Project name: {x[2]} \nLink: {x[4]}\n" for x in projects])
        projects = [x[2] for x in projects]
        bot.send_message(message.chat.id, text, reply_markup=gen_markup(projects))
        bot.register_next_step_handler(message, delete_project, projects=projects)
    else:
        no_projects(message)

def delete_project(message, projects):
    """Удаляет выбранный сыр."""
    project = message.text
    user_id = message.from_user.id

    if message.text == cancel_button:
        cansel(message)
        return
    if project not in projects:
        bot.send_message(message.chat.id, 'У тебя нет такого сыра, попробуй выбрать еще раз!', reply_markup=gen_markup(projects))
        bot.register_next_step_handler(message, delete_project, projects=projects)
        return
    project_id = manager.get_project_id(project, user_id)
    manager.delete_project(user_id, project_id)
    bot.send_message(message.chat.id, f'сыр {project} удален!')

@bot.message_handler(commands=['update_cheeses'])
def update_project(message):
    """Запускает процесс обновления сыра."""
    user_id = message.from_user.id
    projects = manager.get_projects(user_id)
    if projects:
        projects = [x[2] for x in projects]
        bot.send_message(message.chat.id, "Выбери сыр, который хочешь изменить", reply_markup=gen_markup(projects))
        bot.register_next_step_handler(message, update_project_step_2, projects=projects)
    else:
        no_projects(message)

def update_project_step_2(message, projects):
    """Выбирает сыр для обновления."""
    project_name = message.text
    if message.text == cancel_button:
        cansel(message)
        return
    if project_name not in projects:
        bot.send_message(message.chat.id, "Что-то пошло не так!) Выбери сыр, который хочешь изменить еще раз:", reply_markup=gen_markup(projects))
        bot.register_next_step_handler(message, update_project_step_2, projects=projects)
        return
    bot.send_message(message.chat.id, "Выбери, что требуется изменить в сыре", reply_markup=gen_markup(attributes_of_projects.keys()))
    bot.register_next_step_handler(message, update_project_step_3, project_name=project_name)

def update_project_step_3(message, project_name):
    """Запрашивает, что нужно изменить в сыре."""
    attribute = message.text
    reply_markup = None 
    if message.text == cancel_button:
        cansel(message)
        return
    if attribute not in attributes_of_projects.keys():
        bot.send_message(message.chat.id, "Кажется, ты ошибся, попробуй еще раз!)", reply_markup=gen_markup(attributes_of_projects.keys()))
        bot.register_next_step_handler(message, update_project_step_3, project_name=project_name)
        return
    elif attribute == "Статус":
        rows = manager.get_statuses()
        reply_markup = gen_markup([x[0] for x in rows])
    bot.send_message(message.chat.id, attributes_of_projects[attribute][0], reply_markup=reply_markup)
    bot.register_next_step_handler(message, update_project_step_4, project_name=project_name, attribute=attributes_of_projects[attribute][1])

def update_project_step_4(message, project_name, attribute): 
    """Обновляет информацию о сыре"""
    update_info = message.text
    if attribute == "status_id":
        rows = manager.get_statuses()
        if update_info in [x[0] for x in rows]:
            update_info = manager.get_status_id(update_info)
        elif update_info == cancel_button:
            cansel(message)
        else:
            bot.send_message(message.chat.id, "Был выбран неверный статус, попробуй еще раз!)", reply_markup=gen_markup([x[0] for x in rows]))
            bot.register_next_step_handler(message, update_project_step_4, project_name=project_name, attribute=attribute)
            return
    user_id = message.from_user.id
    data = (update_info, project_name, user_id)
    manager.update_projects(attribute, data)
    bot.send_message(message.chat.id, "Готово! Обновления внесены!)")

@bot.message_handler(func=lambda message: True)
def text_handler(message):
    """Обрабатывает текстовые сообщения."""
    user_id = message.from_user.id
    projects = [x[2] for x in manager.get_projects(user_id)]
    project = message.text
    if project in projects:
        info_project(message, user_id, project)
        return
    bot.reply_to(message, "Тебе нужна помощь?")
    info(message)

if __name__ == '__main__':
    manager = DB_Manager(DATABASE)
    bot.infinity_polling()