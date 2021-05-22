from django.contrib.auth import get_user_model
from django.db import models
from django.db.models import CheckConstraint
from pytils.translit import slugify
from django.utils import timezone


User = get_user_model()


class Category(models.Model):
    title = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, primary_key=True)
    image = models.ImageField(upload_to='categories/', null=True, blank=True)

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save()


class Tag(models.Model):
    title = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(primary_key=True)

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save()


class Post(models.Model):
    title = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100, primary_key=True)
    text = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE,
                               related_name='posts')
    category = models.ForeignKey(Category, on_delete=models.CASCADE,
                                 related_name='posts')
    tags = models.ManyToManyField(Tag)
    image = models.ImageField(upload_to='posts/')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            current = timezone.now().strftime('%s')
            self.slug = slugify(self.title) + current
        super().save()


class Comment(models.Model):
    text = models.TextField()
    post = models.ForeignKey(Post,
                             on_delete=models.CASCADE,
                             related_name='comments')
    # post.comments.all()
    # post.comment_set.all()
    user = models.ForeignKey(User,
                             on_delete=models.CASCADE,
                             related_name='comments')
    rating = models.PositiveSmallIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        constraints = [
            CheckConstraint(
                check=models.Q(rating__gte=1) & models.Q(rating__lte=5),
                name='rating_range'
            )
        ]


class Like(models.Model):
    post = models.ForeignKey(Post,
                             on_delete=models.CASCADE,
                             related_name='likes')
    user = models.ForeignKey(User,
                             on_delete=models.CASCADE,
                             related_name='likes')
    is_liked = models.BooleanField(default=False)
