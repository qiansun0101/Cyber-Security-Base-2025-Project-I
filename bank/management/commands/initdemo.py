from decimal import Decimal

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand

from bank.models import Account, Comment, Note


DEMO_USERS = {
    'alice': 'redqueen',
    'bob': 'squarepants',
    'patrick': 'asteroid',
}


class Command(BaseCommand):
    help = 'Create deterministic demo users and data for the security project.'

    def handle(self, *args, **options):
        Comment.objects.all().delete()
        Note.objects.all().delete()
        Account.objects.all().delete()

        users = {}
        for username, password in DEMO_USERS.items():
            user, _ = User.objects.get_or_create(username=username)
            user.set_password(password)
            user.save()
            users[username] = user

        Account.objects.update_or_create(owner=users['alice'], defaults={'balance': Decimal('9000.00')})
        Account.objects.update_or_create(owner=users['bob'], defaults={'balance': Decimal('150.00')})
        Account.objects.update_or_create(owner=users['patrick'], defaults={'balance': Decimal('420.00')})

        Note.objects.create(owner=users['alice'], title='salary', body='Alice private note: bonus = 5000')
        Note.objects.create(owner=users['bob'], title='shopping', body='Bob private note: buy coffee')
        Note.objects.create(owner=users['patrick'], title='weekend', body='Patrick private note: visit beach')

        self.stdout.write(self.style.SUCCESS('Demo data created.'))
        self.stdout.write('Users:')
        for username, password in DEMO_USERS.items():
            self.stdout.write(f'  {username} / {password}')
        self.stdout.write('Account URLs: /account/alice/  /account/bob/  /account/patrick/')
