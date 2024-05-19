from django.db import models

from users.models import User, NULLABLE


class Category(models.Model):
    objects = None
    name = models.CharField(max_length=100, verbose_name='Наименование')
    description = models.TextField(verbose_name='Описание')

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'

    def __str__(self):
        return self.name


class Product(models.Model):
    objects = None
    PUBLISH_STATUS_CHOICES = [
        ('not_published', 'Не опубликовано'),
        ('published', 'Опубликовано')
    ]
    name = models.CharField(max_length=200, verbose_name='Наименование')
    description = models.TextField(verbose_name='Описание', help_text='Введите описание продукта')
    image = models.ImageField(upload_to='product_images/', verbose_name='Изображение', **NULLABLE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, verbose_name='Категория')
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Цена за покупку')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Дата последнего изменения')
    publish_status = models.CharField(max_length=15, choices=PUBLISH_STATUS_CHOICES, default='not_published',
                                      verbose_name='Статус публикации')
    # Поле владельца
    owner = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Владелец',
                              related_name='products',  **NULLABLE)

    class Meta:
        verbose_name = 'Продукт'
        verbose_name_plural = 'Продукты'
        permissions =[
            ("can_cancel_publish_product", "Может отменять публикацию продукта"),
            ("can_change_product_description", "Может менять описание продукта"),
            ("can_change_product_category", "Может менять категорию продукта"),
        ]

    def __str__(self):
        return self.name


class BlogPost(models.Model):
    objects = None
    title = models.CharField(max_length=200, verbose_name='Заголовок')
    slug = models.SlugField(max_length=200, unique=True, verbose_name='Slug')
    content = models.TextField(verbose_name='Содержимое')
    preview = models.ImageField(upload_to='blog_previews/', verbose_name='Превью', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    is_published = models.BooleanField(default=False, verbose_name='Опубликовано')
    views_count = models.PositiveIntegerField(default=0, verbose_name='Количество просмотров')

    class Meta:
        verbose_name = 'Запись'
        verbose_name_plural = 'Записи'

    def __str__(self):
        return self.title


class Version(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name='Продукт', related_name='versions')
    version_number = models.CharField(max_length=50, verbose_name='Номер версии')
    version_title = models.CharField(max_length=200, verbose_name='Название версии')
    is_current = models.BooleanField(default=False, verbose_name='Текущая версия')

    class Meta:
        verbose_name = 'Версия'
        verbose_name_plural = 'Версии'

    def __str__(self):
        return f'{self.version_title} ({self.version_number})'

