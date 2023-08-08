from django.core.management.base import BaseCommand
from django.contrib.auth.models import User

from rest_framework.authtoken.models import Token


class Command(BaseCommand):
    help = "Creates pallete types"

    def add_arguments(self, parser):
        parser.add_argument('-s', '--silent', action='store_true')

    def handle(self, *args, **kwargs):
        user, _ = User.objects.get_or_create(username='username')
        token, _ = Token.objects.get_or_create(user=user)

        if not kwargs['silent']:
            print(f'token: {token.key}')
            print(f'Header example:\nAuthorization: Token {token.key}')

