from wtforms import Form, TextField, PasswordField, validators


class RegistrationForm(Form):

    username = TextField('username', [
        validators.length(min=4, max=20),
        validators.Required()])

    email = TextField('e-mail', [validators.email()])

    password = PasswordField('password', [
        validators.Required(),
        validators.EqualTo('confirm_password', message='Passwords must match')])

    confirm_password = PasswordField('confirm', [validators.Required()])


class LoginForm(Form):

    username = TextField('username', [
        validators.length(min=4, max=20),
        validators.Required()])

    password = PasswordField('password', [validators.Required()])
