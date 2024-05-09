from django.urls import reverse_lazy, reverse
from django.utils.text import slugify
from django.views.generic import ListView, DetailView, View, CreateView, UpdateView, DeleteView
from django.http import HttpResponse
from django.shortcuts import render
from django.views.decorators.csrf import ensure_csrf_cookie
from .models import Product, BlogPost
from catalog.forms import ProductForm


class HomeListView(ListView):
    model = Product
    template_name = 'catalog/home.html'
    context_object_name = 'products'


class ContactsView(View):
    @staticmethod
    def get(request):
        return render(request, 'catalog/contacts.html')

    @ensure_csrf_cookie
    def post(self, request):
        name = request.POST.get('name')
        email = request.POST.get('email')
        message = request.POST.get('message')

        # Обработка данных формы

        print(f"Пользователь {name} с email {email} отправил следующее сообщение:")
        print(message)

        return HttpResponse("Спасибо за обратную связь!")


class ProductDetailView(DetailView):
    model = Product
    template_name = 'catalog/product_detail.html'
    context_object_name = 'product'


class ProductCreateView(CreateView):
    model = Product
    form_class = ProductForm
    success_url = reverse_lazy('catalog:home')

    def form_valid(self, form):
        formset = self.get_context_data()['formset']
        self.object = form.save()
        if formset.is_valid():
            formset.instance = self.object
            formset.save()

        return super().form_valid(form)


class BlogPostListView(ListView):
    model = BlogPost
    # По умолчанию использует 'blogpost_list.html'

    def get_queryset(self):
        # Возвращаем только опубликованные статьи
        return BlogPost.objects.filter(is_published=True)


class BlogPostDetailView(DetailView):
    model = BlogPost
    slug_field = 'slug'
    slug_url_kwarg = 'slug'

    def get_object(self, queryset=None):
        """ Получаем объект и увеличиваем счетчик просмотров. """
        obj = super().get_object(queryset)  # вызов метода базового класса для получения объекта
        obj.views_count += 1  # увеличиваем счетчик просмотров
        obj.save()  # сохраняем изменения в объекте
        return obj


class BlogPostCreateView(CreateView):
    model = BlogPost
    fields = ['title', 'content', 'preview', 'is_published']
    success_url = reverse_lazy('catalog:blogpost_list')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.object = None

    def form_valid(self, form):
        self.object = form.save(commit=False)
        title = form.cleaned_data['title']
        slug = slugify(title)
        count = 1
        while BlogPost.objects.filter(slug=slug).exists():
            slug = f"{slugify(title)}-{count}"
            count += 1
        self.object.slug = slug
        self.object.save()
        return super().form_valid(form)


class BlogPostUpdateView(UpdateView):
    model = BlogPost
    fields = ['title', 'content', 'preview', 'is_published']

    def get_success_url(self):
        # Перенаправляем пользователя на просмотр этой статьи после редактирования
        return reverse('catalog:blogpost_detail', args=[self.object.slug])


class BlogPostDeleteView(DeleteView):
    model = BlogPost
    success_url = reverse_lazy('catalog:blogpost_list')
    # По умолчанию использует 'blogpost_confirm_delete.html'
