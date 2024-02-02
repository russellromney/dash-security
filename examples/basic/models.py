from sqlalchemy.orm import Mapped, mapped_column, DeclarativeBase
from flask_login import UserMixin


class Base(DeclarativeBase):
    pass


class User(UserMixin, Base):
    __tablename__ = "users"

    email: Mapped[str] = mapped_column(primary_key=True)
    name: Mapped[str]
    password: Mapped[str]
    org: Mapped[str]

    def __repr__(self):
        return f"<User {self.email} {self.name} {self.org}"

    # for flask_login to get the primary key
    def get_id(self):
        return self.email
