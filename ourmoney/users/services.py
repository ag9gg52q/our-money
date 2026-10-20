from .models import User


def register_user(*, username, password, email='', first_name='', last_name=''):
    return User.objects.create_user(
        username=username,
        password=password,
        email=email,
        first_name=first_name,
        last_name=last_name,
    )
