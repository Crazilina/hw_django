from django.core.management.base import BaseCommand
from catalog.models import Category, Product
import json


class Command(BaseCommand):
    help = 'Fill the database with data from JSON files'

    @staticmethod
    def json_read_categories():
        with open('catalog/fixtures/categories.json', 'r') as file:
            return json.load(file)

    @staticmethod
    def json_read_products():
        with open('catalog/fixtures/products.json', 'r') as file:
            return json.load(file)

    def handle(self, *args, **options):
        # Удаляем все продукты
        Product.objects.all().delete()

        # Удаляем все категории
        Category.objects.all().delete()

        # Создаем категории
        category_for_create = []
        for category_data in Command.json_read_categories():
            category_for_create.append(Category(**category_data))
        Category.objects.bulk_create(category_for_create)

        # Создаем продукты
        product_for_create = []
        for product_data in Command.json_read_products():
            category_id = product_data.pop('category')
            category = Category.objects.get(pk=category_id)
            product_data['category'] = category
            product_for_create.append(Product(**product_data))
        Product.objects.bulk_create(product_for_create)

        self.stdout.write(self.style.SUCCESS('Data successfully loaded into the database'))
