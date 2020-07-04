from django.shortcuts import get_object_or_404
from rest_framework import viewsets, permissions, status, filters
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from django.contrib.auth.models import User

from .models import Post, Comment, Follow, Group
from .serializers import (PostSerializer, CommentSerializer,
                          FollowingSerializer, GroupSerializer)

class PostViewSet(viewsets.ModelViewSet):
    serializer_class = PostSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)

    def get_queryset(self):
        if not self.request.query_params.get('group'):
            return Post.objects.all()
        return Post.objects.filter(
            group=self.request.query_params.get('group')
        )

    def perform_create(self, serializer):
            serializer.save(author=self.request.user)

    def update(self, request, *args, **kwargs):
        post = self.get_object()
        serializer = PostSerializer(post, data=request.data, partial=True)
        if request.user == post.author:
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.data,
                            status=status.HTTP_400_BAD_REQUEST)
        return Response(status=status.HTTP_403_FORBIDDEN)

    def destroy(self, request, *args, **kwargs):
        post = self.get_object()
        if request.user == post.author:
            post.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(status=status.HTTP_403_FORBIDDEN)


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer

    def get_queryset(self):
        post = get_object_or_404(Post, pk=self.kwargs.get('post_id'))
        queryset = Comment.objects.filter(post=post)
        return queryset

    def perform_create(self, serializer):
        post = get_object_or_404(Post, pk=self.kwargs.get('post_id'))
        return serializer.save(author = self.request.user, post=post)

    def update(self, request, *args, **kwargs):
        comment = self.get_object()
        serializer = PostSerializer(comment, data=request.data, partial=True)
        if request.user == comment.author:
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors,
                            status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(status=status.HTTP_403_FORBIDDEN)

    def destroy(self, request, *args, **kwargs):
        comment = self.get_object()
        if request.user == comment.author:
            comment.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            return Response(status=status.HTTP_403_FORBIDDEN)


class FollowViewSet(viewsets.ModelViewSet):
    queryset = Follow.objects.all()
    serializer_class = FollowingSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    filter_backends = [filters.SearchFilter]
    search_fields = ['=following__username', '=user__username']

    def perform_create(self, serializer):
        if User.objects.filter(username=self.request.data.get('following')).count() == 1:
            print('im here if')
            following = User.objects.get(username=self.request.data.get('following'))
            user = self.request.user
            followers = Follow.objects.filter(user=user,
                                              following=following).count()
            if followers > 0:
                raise ValidationError
            serializer.save(user=user, following=following)
        else:
            print(f'Im here')
            print(User.objects.filter(username=self.request.data.get('following')).count())
            raise ValidationError


class GroupViewSet(viewsets.ModelViewSet):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
