from peewee import *
import datetime


db = PostgresqlDatabase('learn', user='hakuro')


class BaseModel(Model):

    class Meta:
        database = db


class User(Model):
    username = CharField(max_length=32, unique=True)
    email = CharField(max_length=100)
    password = CharField(max_length=32)
    join_date = DateTimeField(default=datetime.datetime.utcnow)

    class Meta:
        database = db
        db_table = 'user_account'


class Section(BaseModel):
    title = CharField(max_length=50)
    user = ForeignKeyField(User, related_name='sections')


class Subsection(BaseModel):
    title = CharField(max_length=50)
    user = ForeignKeyField(User, related_name='subsections')
    section = ForeignKeyField(Section, related_name='subsections')
    goals_num = IntegerField(default=0)


class Goal(BaseModel):
    title = CharField(max_length=200)
    user = ForeignKeyField(User, related_name='goals')
    subsection = ForeignKeyField(Subsection, related_name='goals')
    note = TextField()
    progress = IntegerField(default=0)


def create_db():
    db.connect()
    db.create_tables([User, Section, Subsection, Goal])


# create_db()
