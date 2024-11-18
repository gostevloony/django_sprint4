from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse, reverse_lazy
from django.views.generic import (CreateView, DeleteView, DetailView,
                                  ListView, UpdateView)

from blog.forms import CommentForm, PostForm
from blog.models import Category, Comment, Post, User
from constants import PAGE_NUMBER
from core.utils import get_published_objects


class TestAuthorMixin(UserPassesTestMixin):
    def test_func(self):
        return self.get_object().author == self.request.user

    def handle_no_permission(self):
        return redirect(
            'blog:post_detail',
            post_id=self.kwargs['post_id']
        )


class PostListView(ListView):
    """Список всех публикаций"""

    model = Post
    paginate_by = PAGE_NUMBER
    template_name = 'blog/index.html'

    def get_queryset(self):
        return Post.postpub.published().count_comment().order()


class PostDetailView(DetailView):
    """Отдельная публикация"""

    model = Post
    template_name = 'blog/detail.html'
    pk_url_kwarg = 'post_id'

    def get_object(self, queryset=None):
        post_obj = super().get_object()
        if post_obj.author == self.request.user:
            return post_obj
        return super().get_object(
            queryset=Post.postpub.published(
            ).filter(pk=self.kwargs[self.pk_url_kwarg])
        )

    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .prefetch_related(
                'comments',
            )
        )

    def get_context_data(self, **kwargs):
        return dict(
            **super().get_context_data(**kwargs),
            form=CommentForm(),
            comments=self.object.comments.select_related('author')
        )


class CategoryListView(ListView):
    """Список постов в категории"""

    model = Post
    paginate_by = PAGE_NUMBER
    slug_url_kwarg = 'category_slug'
    template_name = 'blog/category.html'

    def get_queryset(self):
        return Post.postpub.published(
        ).filter(category__slug=self.kwargs[self.slug_url_kwarg]
                 ).count_comment().order()

    def get_context_data(self, **kwargs):
        return dict(
            **super().get_context_data(**kwargs),
            category=get_published_objects(
                Category,
                slug=self.kwargs[self.slug_url_kwarg]
            )
        )


class PostCreateView(LoginRequiredMixin, CreateView):
    """Добавление новой публикации."""

    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'
    slug_url_kwarg = 'username'

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse(
            'blog:profile',
            kwargs={'username': self.request.user.username}
        )


class PostUpdateDeleteView(TestAuthorMixin):
    """Миксин для редактирования и удаления публикации"""

    model = Post
    pk_url_kwarg = 'post_id'
    template_name = 'blog/create.html'


class PostUpdateView(PostUpdateDeleteView, UpdateView):
    """Редактирование публикации."""

    form_class = PostForm


class PostDeleteView(PostUpdateDeleteView, DeleteView):
    """Удаление публикации."""

    success_url = reverse_lazy('blog:index')


class ProfileView(ListView):
    """Страница пользователя"""

    model = Post
    paginate_by = PAGE_NUMBER
    slug_url_kwarg = 'username'
    template_name = 'blog/profile.html'

    def get_queryset(self):
        author = get_object_or_404(
            User,
            username=self.kwargs[self.slug_url_kwarg]
        )
        queryset = super().get_queryset().filter(author=author)
        if author != self.request.user:
            queryset = Post.postpub.published(
            ).filter(author=author).count_comment().order()
        return queryset

    def get_context_data(self, **kwargs):
        return dict(
            **super().get_context_data(**kwargs),
            profile=get_object_or_404(
                User,
                username=self.kwargs[self.slug_url_kwarg]
            )
        )


class UserEditView(LoginRequiredMixin, UpdateView):
    """Редактирование профиля"""

    model = User
    fields = ('first_name', 'last_name', 'username', 'email')
    template_name = 'blog/user.html'

    def get_object(self, queryset=None):
        return self.request.user

    def get_success_url(self):
        return reverse(
            'blog:profile',
            kwargs={'username': self.request.user.username}
        )


class CommentCreateView(LoginRequiredMixin, CreateView):
    """Добавление комментария"""

    model = Comment
    form_class = CommentForm

    def form_valid(self, form):
        post = get_object_or_404(Post, pk=self.kwargs['post_id'])
        form.instance.author = self.request.user
        form.instance.post = post
        return super().form_valid(form)

    def get_success_url(self):
        return reverse(
            'blog:post_detail',
            kwargs={'post_id': self.kwargs['post_id']}
        )


class CommentUpdateDeleteMixin(TestAuthorMixin):
    """Миксин для редактирования и удаления комментария"""

    model = Comment
    pk_url_kwarg = 'comment_id'
    template_name = 'blog/comment.html'

    def get_success_url(self):
        return reverse(
            'blog:post_detail',
            kwargs={'post_id': self.kwargs['post_id']}
        )


class CommentUpdateView(CommentUpdateDeleteMixin, UpdateView):
    """Редактирование комментария"""

    form_class = CommentForm


class CommentDeleteView(CommentUpdateDeleteMixin, DeleteView):
    """Удаление комментария"""
