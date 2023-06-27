from flask import Flask, session, request, redirect, url_for, render_template
from db_scripts import get_question_after, get_quises, check_answer
import os
from random import shuffle
 
def start_quis(quiz_id):
    '''создаёт нужные значения в словаре session'''
    session['quiz'] = quiz_id
    session['last_question'] = 0
    session["total"] = 0
    session["answers"] = 0

def save_answers():
    answer = request.form.get('ans_text')
    quest_id = request.form.get('q_id')
    session["last_question"] = quest_id
    session["total"] += 1
    if check_answer(quest_id, answer):
        session["answers"] += 1
 
def end_quiz():
    session.clear()
 
def quiz_form():
    q_list = get_quises()
    return render_template("start.html", q_list=q_list)

def question_form(question):
    answers_list = [question[2], question[3], question[4], question[5]]
    shuffle(answers_list)
    print(answers_list)
    return render_template("test.html", answers_list=answers_list, question=question[1], quest_id=question[0])
    
       
def index():
    ''' Первая страница: если пришли запросом GET, то выбрать викторину, 
    если POST - то запомнить id викторины и отправлять на вопросы'''
    if request.method == 'GET':
        # викторина не выбрана, сбрасываем id викторины и показываем форму выбора
        start_quis(-1)
        return quiz_form()
    else:
        # получили дополнительные данные в запросе! Используем их:
        quest_id = request.form.get('quiz') # выбранный номер викторины 
        start_quis(quest_id)
        return redirect(url_for('test'))
 
def test():
    '''возвращает страницу вопроса'''
    # что если пользователь без выбора викторины пошел сразу на адрес '/test'? 
    if not ('quiz' in session) or int(session['quiz']) < 0:
        return redirect(url_for('index'))
    else:
        # тут пока старая версия функции:
        if request.method == "POST":
            save_answers()
        next_question = get_question_after(session["last_question"], session["quiz"])
        if next_question is None or len(next_question) == 0:
            return redirect(url_for("result"))
        else:
            return question_form(next_question)
 
def result():
    answers = session['answers']
    total = session['total']
    end_quiz()
    return render_template("result.html", total=total, right=answers)
 
# Создаём объект веб-приложения:
folder = os.getcwd()
app = Flask(__name__, template_folder=folder)

app.add_url_rule('/', 'index', index, methods=['post', 'get']) # правило для '/index' 
app.add_url_rule('/test', 'test', test, methods=['post', 'get']) # создаёт правило для URL '/test'
app.add_url_rule('/result', 'result', result) # создаёт правило для URL '/test'

app.config['SECRET_KEY'] = 'ThisIsSecretSecretSecretLife'
 
if __name__ == "__main__":
    # Запускаем веб-сервер:
    app.run(host='0.0.0.0', port=8000, debug=False)