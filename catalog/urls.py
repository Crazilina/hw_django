from django.urls import path
from django.views.decorators.cache import cache_page

from . import views

app_name = 'catalog'

urlpatterns = [
    path('', views.HomeListView.as_view(), name='home'),
    path('contacts/', views.ContactsView.as_view(), name='contacts'),
    path('create/', views.ProductCreateView.as_view(), name='create_product'),
    path('product/<int:pk>/', cache_page(60)(views.ProductDetailView.as_view()), name='product_detail'),
    path('product/<int:pk>/edit/', views.ProductUpdateView.as_view(), name='product_update'),
    path('product/<int:pk>/delete/', views.ProductDeleteView.as_view(), name='product_delete'),
    path('product/<int:pk>/cancel_publish/', views.cancel_publish, name='cancel_publish'),
    path('category/<int:pk>/', views.ProductListByCategoryView.as_view(), name='product_list_by_category'),
    path('categories/', views.CategoryListView.as_view(), name='category_list'),
    path('blog/', views.BlogPostListView.as_view(), name='blogpost_list'),
    path('blog/new/', views.BlogPostCreateView.as_view(), name='blogpost_create'),
    path('blog/<slug:slug>/', views.BlogPostDetailView.as_view(), name='blogpost_detail'),
    path('blog/<int:pk>/edit/', views.BlogPostUpdateView.as_view(), name='blogpost_update'),
    path('blog/<int:pk>/delete/', views.BlogPostDeleteView.as_view(), name='blogpost_delete'),
]
