from django.forms import inlineformset_factory
from django.urls import reverse_lazy, reverse
from django.utils.text import slugify
from django.views.generic import ListView, DetailView, View, CreateView, UpdateView, DeleteView
from django.http import HttpResponse
from django.shortcuts import render
from django.views.decorators.csrf import ensure_csrf_cookie
from .models import Product, BlogPost, Version
from catalog.forms import ProductForm, VersionForm


class HomeListView(ListView):
    model = Product
    template_name = 'catalog/home.html'
    context_object_name = 'products'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        products = context['products']

        # Добавляем информацию о текущей активной версии для каждого продукта
        for product in products:
            # Пытаемся найти текущую активную версию продукта
            try:
                current_version = Version.objects.filter(product=product, is_current=True).first()
            except Version.DoesNotExist:
                current_version = None

            # Присваиваем найденную версию продукту как атрибут
            product.current_version = current_version

        return context


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


class ProductCreateView(CreateView):
    model = Product
    form_class = ProductForm
    template_name = 'catalog/product_form.html'
    success_url = reverse_lazy('catalog:home')

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        VersionFormset = inlineformset_factory(Product, Version, form=VersionForm, extra=1, can_delete=True)
        if self.request.method == 'POST':
            data['versions'] = VersionFormset(self.request.POST, instance=self.object)
        else:
            data['versions'] = VersionFormset(instance=self.object)
        return data

    def form_valid(self, form):
        formset = self.get_context_data()['versions']
        self.object = form.save()
        if formset.is_valid():
            formset.instance = self.object
            formset.save()
        return super().form_valid(form)


class ProductDetailView(DetailView):
    model = Product
    template_name = 'catalog/product_detail.html'
    context_object_name = 'product'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        product = self.get_object()
        context['versions'] = product.versions.all()
        return context


class ProductUpdateView(UpdateView):
    model = Product
    form_class = ProductForm
    template_name = 'catalog/product_form.html'
    success_url = reverse_lazy('catalog:home')

    def get_context_data(self, **kwargs):
        data = super(ProductUpdateView, self).get_context_data(**kwargs)
        if self.request.POST:
            data['versions'] = inlineformset_factory(Product, Version, form=VersionForm, extra=1)(self.request.POST,
                                                                                                  self.request.FILES,
                                                                                                  instance=self.object)
        else:
            data['versions'] = inlineformset_factory(Product, Version, form=VersionForm, extra=1)(instance=self.object)
        return data

    def form_valid(self, form):
        context = self.get_context_data()
        versions = context['versions']
        if versions.is_valid():
            versions.save()
        return super(ProductUpdateView, self).form_valid(form)


class ProductDeleteView(DeleteView):
    model = Product
    template_name = 'catalog/product_confirm_delete.html'
    success_url = reverse_lazy('catalog:home')

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.object.delete()
        return HttpResponse("Продукт успешно удален")


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
