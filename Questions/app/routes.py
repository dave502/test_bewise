
from flask import Flask, jsonify, request, make_response, abort, current_app
from flask import Blueprint
import requests
import json

from app.models import Question
from app import db
import re

app_route = Blueprint('route', __name__)
re_tags = re.compile(r'<[^>]+>')


def remove_tags(text: str) -> str:
    return re_tags.sub('', text)


@app_route.route('/')
def index():
    return "Available api pathes are:<br><a href=/api/questions>api/questions</a>"


@app_route.route('/api/questions', methods=['POST'])
def get_question() -> tuple([dict, int]):

    def request_questions(count: int = 1) -> list[dict]:

        _questions: list[dict] = []

        # * get questions from jservice
        URL: str = 'https://jservice.io/api/random'
        questions_data: bytes = requests.get(URL, params={'count': count}).content

        # * abort if didn't get answers from jservice
        if not questions_data:
            current_app.logger.error(f'The questions was not recieved')
            abort(500)

        # * transform answer to dict
        try:
            _questions = json.loads(questions_data)
        except Exception as e:
            current_app.logger.error(f'Error: {e}. Problem with converting recieved data')
            abort(500)

        # * check the number of questions received
        if len(_questions) != count:
            current_app.logger.warning(f"Count of recieved records doesn't match to {payload['count']}")

        return _questions

    payload: dict = dict()

    # * get payload dict from POST request
    try:
        payload = json.loads(request.data)
        if not payload.get('questions_num'):
            raise Exception("The key \'questions_num\' is wrong")
    except Exception as e:
        current_app.logger.warning(f'Error: {e}. Please check the payload {request.data}. '
                       'It must be {"questions_num" : <int>}')
        abort(400)
    current_app.logger.debug(f"{payload=}")

    # * get questions from jservice
    questions: list[dict] = request_questions(payload.get('questions_num'))

    # * check for duplicates
    # get questions with ids from jservice answer from database
    duplicates: list[dict] = Question.query.with_entities(Question.question_id).filter(Question.question_id.in_([q["id"] for q in questions])).all()
    if duplicates:
        duplicates = [i[0] for i in duplicates]  # ids to simple list from list of tuples
        # remove duplicated questions from jservice answer
        questions = [question for question in questions if question.get("id") not in duplicates]

        while duplicates:
            current_app.logger.debug(f"{len(duplicates)} duplicates was recieved with ids: {duplicates}.")
            # get new questions
            new_questions: list[dict] = request_questions(len(duplicates))
            # check for duplicates
            duplicates = Question.query.with_entities(Question.question_id).filter(
                Question.question_id.in_([q["id"] for q in questions])).all()
            # append new questions to general questions list if they aren't duplicates
            [questions.append(question) for question in new_questions if question.get("question_id") not in duplicates]

    # * get last question for function's return
    last_question: Question = db.session.query(Question).order_by(Question.id.desc()).first()

    # * add questions to database
    for question in questions:

        new_question = Question(
            question_id=question['id'],
            question=remove_tags(question['question']),
            answer=remove_tags(question['answer']),
            date=question['created_at'])
        db.session.add(new_question)

    try:
        db.session.commit()
    except Exception as e:
        current_app.logger.error(f'The error was occured while commiting to database')
        abort(500)
    else:
        current_app.logger.info(f'{len(questions)} questions was added to database')
    return last_question.as_dict() if last_question else {}, 201


@app_route.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found. Available api pathes are:<br><a href=/api/questions>api/questions</a>"'}), 404)


