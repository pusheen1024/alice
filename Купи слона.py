import logging
from fnmatch import fnmatch
from flask import Flask, request, jsonify


app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

sessionStorage = {}


@app.route('/post', methods=['POST'])
def main():
    logging.info(f'Request: {request.json!r}')
    response = {
        'session': request.json['session'],
        'version': request.json['version'],
        'response': {'end_session': False}
    }
    handle_dialog(request.json, response)
    logging.info(f'Response:  {response!r}')
    return jsonify(response)


def handle_dialog(req, res):
    user_id = req['session']['user_id']
    if req['session']['new']:
        sessionStorage[user_id] = {'suggests': ["Не хочу.", "Не буду.", "Отстань!"]}
        res['response']['text'] = 'Привет! Купи слона!'
        res['response']['buttons'] = get_suggests(user_id)
    else:
        if is_consent(req['request']['original_utterance']):
            res['response']['text'] = 'Слона можно найти на Яндекс.Маркете!'
            res['response']['end_session'] = True
        else:
            res['response']['text'] = f"Все говорят '{req['request']['original_utterance']}', а ты купи слона!"
        res['response']['buttons'] = get_suggests(user_id)


def get_suggests(user_id):
    session = sessionStorage[user_id]
    suggests = [{'title': suggest, 'hide': True} for suggest in session['suggests'][:2]]
    session['suggests'] = session['suggests'][1:]
    sessionStorage[user_id] = session
    if len(suggests) < 2:
        suggests.append({"title": "Хорошо",
                         "url": "https://market.yandex.ru/search?text=слон",
                         "hide": True})
    return suggests


def is_consent(phrase):
    consent_words = ['да', 'окей', 'хорошо', 'конечно', 'не против',
                     'согласен', 'согласна', 'куплю', 'покупаю']
    return any(word in phrase.lower() and not
               fnmatch(phrase.lower(), f'*не*{word}') for word in consent_words)


if __name__ == '__main__':
    app.run()
