from flask.cli import FlaskGroup

from app import app, create_app, db
from app.models import User


cli = FlaskGroup(app)


@cli.command("create_db")
def create_db():
    try:
        db.create_all()
        db.session.commit()
    except Exception as e:
        app.logger.error(e)


@cli.command("create_db_user")
def create_db_user():
    try:
        db.session.add(User(email="admin@admin.com"))
        db.session.commit()
    except Exception as e:
        app.logger.error(e)


if __name__ == "__main__":
    create_app()
    cli()


