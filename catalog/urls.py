from django.urls import path
from . import views

app_name = 'catalog'

urlpatterns = [
    path('', views.HomeListView.as_view(), name='home'),
    path('contacts/', views.ContactsView.as_view(), name='contacts'),
    path('create/', views.ProductCreateView.as_view(), name='create_product'),
    path('product/<int:pk>/', views.ProductDetailView.as_view(), name='product_detail'),
    path('product/<int:pk>/edit/', views.ProductUpdateView.as_view(), name='product_update'),
    path('product/<int:pk>/delete/', views.ProductDeleteView.as_view(), name='product_delete'),
    path('product/<int:pk>/cancel_publish/', views.cancel_publish, name='cancel_publish'),
    path('blog/', views.BlogPostListView.as_view(), name='blogpost_list'),
    path('blog/new/', views.BlogPostCreateView.as_view(), name='blogpost_create'),
    path('blog/<slug:slug>/', views.BlogPostDetailView.as_view(), name='blogpost_detail'),
    path('blog/<int:pk>/edit/', views.BlogPostUpdateView.as_view(), name='blogpost_update'),
    path('blog/<int:pk>/delete/', views.BlogPostDeleteView.as_view(), name='blogpost_delete'),
]
