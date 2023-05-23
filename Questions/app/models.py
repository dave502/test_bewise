from app import db


class Question(db.Model):
    __tablename__ = 'questions'

    id = db.Column(db.Integer, primary_key=True)
    question_id = db.Column(db.Integer, unique=True)
    question = db.Column(db.String(), nullable=False)
    answer = db.Column(db.String(), nullable=False)
    date = db.Column(db.DateTime(timezone=True))

    def __init__(self, question_id: int, question: str, answer: str, date: str):
        self.question_id = question_id
        self.question = question
        self.answer = answer
        self.date = date

    def __repr__(self) -> str:
        return f'<Question {self.question} with answer {self.question} (date: {self.date})'

    def as_dict(self) -> dict:
        return {col.name: getattr(self, col.name) for col in self.__table__.columns}


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(128), unique=True, nullable=False)
    active = db.Column(db.Boolean(), default=True, nullable=False)

    def __init__(self, email):
        self.email = email
