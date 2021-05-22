from rest_framework import serializers

from .models import Category, Tag, Post, Comment


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ('title', 'image')

    def validate_title(self, title):
        if self.Meta.model.objects.filter(title=title).exists():
            raise serializers.ValidationError('Заголовок не может повторяться')
        return title


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ('title', )

    def validate_title(self, title):
        if self.Meta.model.objects.filter(title=title).exists():
            raise serializers.ValidationError('Заголовок не может повторяться')
        return title


class PostSerializer(serializers.ModelSerializer):

    class Meta:
        model = Post
        fields = '__all__'

    def create(self, validated_data):
        request = self.context.get('request')
        user = request.user
        tags = validated_data.pop('tags', [])
        post = Post.objects.create(author=user, **validated_data)
        post.tags.add(*tags)
        return post

    def get_fields(self):
        action = self.context.get('action')
        fields = super().get_fields()
        if action == 'create':
            fields.pop('slug')
            fields.pop('author')
        return fields

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['category'] = CategorySerializer(instance.category, context=self.context).data
        representation['tags'] = TagSerializer(instance.tags.all(), many=True, context=self.context).data
        representation['comments'] = CommentSerializer(instance.comments.all(), many=True).data
        representation['likes_count'] = instance.likes.count()
        return representation


class PostsListSerializer(serializers.ModelSerializer):
    details = serializers.HyperlinkedIdentityField(view_name='post-detail',
                                                   lookup_field='slug')

    class Meta:
        model = Post
        fields = ('title', 'slug', 'image', 'created_at', 'details')


class CommentSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Comment
        fields = '__all__'

    def validate_rating(self, rating):
        if rating not in range(1, 6):
            raise serializers.ValidationError('Укажите рейтинг от 1 до 5')
        return rating

    def create(self, validated_data):
        request = self.context.get('request')
        user = request.user
        comment = Comment.objects.create(user=user, **validated_data)
        return comment
