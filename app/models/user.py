from app import db


class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), nullable=False)
    is_blocked = db.Column(db.Boolean, nullable=False, default=False)
    is_admin = db.Column(db.Boolean, nullable=False, default=False)
    password = db.Column(db.Text, nullable=False)


    @classmethod
    def add_entry(cls, name, password, is_admin=False):
        new_user = cls(
            name = name,
            password = password,
            is_admin = is_admin
        )

        # Add the new instance to the session and commit it
        db.session.add(new_user)
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            raise e

        return new_user