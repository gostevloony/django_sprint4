from django.urls import include, path

from . import views

app_name = 'blog'

urls = [
    path('', views.PostDetailView.as_view(), name='post_detail'),
    path('create/', views.PostCreateView.as_view(), name='create_post'),
    path('edit/', views.PostUpdateView.as_view(), name='edit_post'),
    path('delete/', views.PostDeleteView.as_view(), name='delete_post'),
    path('comment/', views.CommentCreateView.as_view(), name='add_comment'),
    path(
        'edit_comment/<int:comment_id>/',
        views.CommentUpdateView.as_view(),
        name='edit_comment'),
    path(
        'delete_comment/<int:comment_id>/',
        views.CommentDeleteView.as_view(),
        name='delete_comment'),
]

posts_urls = [
    path('<int:post_id>/', include(urls)),
    path('create/', views.PostCreateView.as_view(), name='create_post'),
]

profile_urls = [
    path('edit/', views.UserEditView.as_view(), name='edit_profile'),
    path('<slug:username>/', views.ProfileView.as_view(), name='profile'),
]

urlpatterns = [
    path('', views.PostListView.as_view(), name='index'),
    path('posts/', include(posts_urls)),
    path('category/<slug:category_slug>/',
         views.CategoryListView.as_view(),
         name='category_posts'),
    path('profile/', include(profile_urls)),
]
