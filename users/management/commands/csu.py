import os
from django.core.management import BaseCommand
from users.models import User
from dotenv import load_dotenv


class Command(BaseCommand):
    help = 'Create a superuser with environment variables'

    def handle(self, *args, **kwargs):
        # Загружаем переменные окружения из файла .env
        load_dotenv()

        email = os.getenv('SUPERUSER_EMAIL')
        password = os.getenv('SUPERUSER_PASSWORD')

        if not email or not password:
            self.stdout.write(self.style.ERROR('SUPERUSER_EMAIL and SUPERUSER_PASSWORD must be set'))
            return

        if User.objects.filter(email=email).exists():
            self.stdout.write(self.style.WARNING(f'Superuser with email {email} already exists.'))
        else:
            user = User.objects.create(
                email=email,
                first_name='Alina',
                last_name='Salakhova',
                is_active=True,
                is_staff=True,
                is_superuser=True
            )
            user.set_password(password)
            user.save()
            self.stdout.write(self.style.SUCCESS(f'Superuser {email} created successfully.'))
