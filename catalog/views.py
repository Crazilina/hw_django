from django.contrib.auth.decorators import permission_required
from django.core.exceptions import PermissionDenied
from django.forms import inlineformset_factory
from django.urls import reverse_lazy, reverse
from django.utils.text import slugify
from django.views.generic import ListView, DetailView, View, CreateView, UpdateView, DeleteView
from django.http import HttpResponse, HttpResponseForbidden
from django.shortcuts import render, get_object_or_404, redirect
from django.views.decorators.csrf import ensure_csrf_cookie
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from .models import Product, BlogPost, Version
from catalog.forms import ProductForm, VersionForm, ProductModeratorForm


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

        # Добавляем текущего пользователя в контекст
        context['user'] = self.request.user

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


class ProductCreateView(LoginRequiredMixin, CreateView):
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
        form.instance.owner = self.request.user  # Привязываем продукт к авторизованному пользователю
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


class ProductUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Product
    form_class = ProductForm
    template_name = 'catalog/product_form.html'
    success_url = reverse_lazy('catalog:home')

    def get_context_data(self, **kwargs):
        data = super(ProductUpdateView, self).get_context_data(**kwargs)
        data['product'] = self.get_object()
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
            active_versions = [version for version in versions if version.cleaned_data.get('is_current')]
            if len(active_versions) > 1:
                form.add_error(None,
                               'Может быть только одна активная версия продукта. Пожалуйста, выберите только одну.')
                return self.form_invalid(form)
            versions.save()
        return super(ProductUpdateView, self).form_valid(form)

    def get_form_class(self):
        user = self.request.user
        if user == self.get_object().owner:
            return ProductForm
        if user.has_perm('catalog.can_change_product_description') \
                and user.has_perm('catalog.can_change_product_category') \
                and user.has_perm('catalog.can_cancel_publish_product'):
            return ProductModeratorForm
        raise PermissionDenied

    def test_func(self):
        product = self.get_object()
        user = self.request.user
        return user == product.owner or (
            user.has_perm('catalog.can_change_product_description') and
            user.has_perm('catalog.can_change_product_category') and
            user.has_perm('catalog.can_cancel_publish_product')
        )


class ProductDeleteView(LoginRequiredMixin, DeleteView):
    model = Product
    template_name = 'catalog/product_confirm_delete.html'
    success_url = reverse_lazy('catalog:home')

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.object.delete()
        return HttpResponse("Продукт успешно удален")


@permission_required('catalog.can_cancel_publish_product', raise_exception=True)
def cancel_publish(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if not request.user.has_perm('catalog.can_cancel_publish_product'):
        return HttpResponseForbidden()
    product.publish_status = 'not_published'
    product.save()
    return redirect(reverse('catalog:product_detail', args=[pk]))


class BlogPostListView(LoginRequiredMixin, ListView):
    model = BlogPost

    # По умолчанию использует 'blogpost_list.html'

    def get_queryset(self):
        # Возвращаем только опубликованные статьи
        return BlogPost.objects.filter(is_published=True)


class BlogPostDetailView(LoginRequiredMixin, DetailView):
    model = BlogPost
    slug_field = 'slug'
    slug_url_kwarg = 'slug'

    def get_object(self, queryset=None):
        """ Получаем объект и увеличиваем счетчик просмотров. """
        obj = super().get_object(queryset)  # вызов метода базового класса для получения объекта
        obj.views_count += 1  # увеличиваем счетчик просмотров
        obj.save()  # сохраняем изменения в объекте
        return obj


class BlogPostCreateView(LoginRequiredMixin, CreateView):
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


class BlogPostUpdateView(LoginRequiredMixin, UpdateView):
    model = BlogPost
    fields = ['title', 'content', 'preview', 'is_published']

    def get_success_url(self):
        # Перенаправляем пользователя на просмотр этой статьи после редактирования
        return reverse('catalog:blogpost_detail', args=[self.object.slug])


class BlogPostDeleteView(LoginRequiredMixin, DeleteView):
    model = BlogPost
    success_url = reverse_lazy('catalog:blogpost_list')
    # По умолчанию использует 'blogpost_confirm_delete.html'
