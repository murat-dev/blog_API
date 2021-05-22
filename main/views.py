from django.shortcuts import render

# Create your views here.
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from rest_framework.decorators import api_view, action
from rest_framework.generics import ListAPIView, CreateAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework.viewsets import ModelViewSet

from .models import Category, Tag, Post, Comment, Like
from .permissions import IsAdminPermission, IsAuthorPermission
from .serializers import CategorySerializer, TagSerializer, PostSerializer, CommentSerializer, PostsListSerializer


@api_view()
def categories_list(request):
    categories = Category.objects.all()
    print(categories)
    serializer = CategorySerializer(categories, many=True)
    categories = serializer.data
    print(categories)
    return Response(categories)


class CategoriesListView(ListAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class TagsListView(ListAPIView):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class PostsListView(ListAPIView):
    queryset = Post.objects.all()
    serializer_class = PostSerializer


# api/v1/posts/tag/
# api/v1/posts?tags=sport,interesting
class PostViewSet(ModelViewSet):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    lookup_url_kwarg = 'slug'
    filter_backends = [DjangoFilterBackend,
                       filters.SearchFilter,
                       filters.OrderingFilter]
    filterset_fields = ['tags__slug', 'category', 'author']
    search_fields = ['title', 'text', 'tags__title']
    ordering_fields = ['created_at', 'title']

    def get_serializer_class(self):
        if self.action == 'list':
            return PostsListSerializer
        return self.serializer_class

    @action(['GET'], detail=True)
    def comments(self, request, slug=None):
        post = self.get_object()
        comments = post.comments.all()
        serializer = CommentSerializer(comments, many=True)
        return Response(serializer.data)

    @action(['POST'], detail=True)
    def like(self, request, slug=None):
        post = self.get_object()
        user = request.user
        try:
            like = Like.objects.get(post=post, user=user)
            like.is_liked = not like.is_liked
            like.save()
            message = 'liked' if like.is_liked else 'disliked'
        except Like.DoesNotExist:
            Like.objects.create(post=post, user=user, is_liked=True)
            message = 'liked'
        return Response(message, status=200)

    def get_permissions(self):
        if self.action == 'create':
            permissions = [IsAdminPermission]
        elif self.action in ['update', 'partial_update', 'destroy']:
            permissions = [IsAuthorPermission]
        elif self.action == 'like':
            permissions = [IsAuthenticated]
        else:
            permissions = []
        return [perm() for perm in permissions]

    def get_serializer_context(self):
        return {'request': self.request, 'action': self.action}


@api_view(['GET'])
def api_root(request, format=None):
    return Response({
        'posts': reverse('post-list', request=request, format=format),
        'categories': reverse('categories-list', request=request, format=format),
        'tags': reverse('tags-list', request=request, format=format)
    })


class CommentCreateView(CreateAPIView):
    queryset = Comment.objects.none()
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated, ]

#TODO: сделать отдельный сериализатор для листинга постов
#TODO: сделать избранное(лайки)
#TODO: сделать восстановление и смену пароля
#TODO: сделать пояснения к коду
#TODO: сделать пошаговый документ
#TODO: разобрать все в Postman

# CRUD (Create, Read, Upd   ate, Delete)
# CRUD(Create, Retrieve, Update, Destroy)

# router.register('posts', PostViewSet)
# path('api/v1/', include(router.urls))

# POST - api/v1/posts/ - создание
# GET - api/v1/posts/ - листинг
# GET - api/v1/posts/pk/ - детали
# PUT/PATCH - api/v1/posts/pk/ изменение
# DELETE - /api/v1/posts/pk/ удаление

# BasicAuth - username, password
# TokenAuth - Authorization: Token awafsefrr3r321323123132312
# SessionAuth - состояние пользователя хранится в сессии
