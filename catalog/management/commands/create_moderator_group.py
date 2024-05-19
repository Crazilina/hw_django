from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from catalog.models import Product


class Command(BaseCommand):
    help = 'Создает группу модераторов и назначает права'

    def handle(self, *args, **kwargs):
        group_name = 'moderator'

        # Создаем группу, если она не существует
        group, created = Group.objects.get_or_create(name=group_name)
        if created:
            self.stdout.write(self.style.SUCCESS(f'Группа "{group_name}" создана'))
        else:
            self.stdout.write(self.style.WARNING(f'Группа "{group_name}" уже существует'))

        # Получаем права
        permissions = [
            'can_cancel_publish_product',
            'can_change_product_description',
            'can_change_product_category'
        ]
        content_type = ContentType.objects.get_for_model(Product)

        for codename in permissions:
            permission, _ = Permission.objects.get_or_create(codename=codename, content_type=content_type)
            group.permissions.add(permission)

        self.stdout.write(self.style.SUCCESS(f'Права назначены группе "{group_name}"'))
