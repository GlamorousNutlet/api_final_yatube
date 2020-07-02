from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    )
from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import PostViewSet, CommentViewSet, FollowViewSet, GroupViewSet

post_router = DefaultRouter()
comment_router = DefaultRouter()
follow_router = DefaultRouter()
group_router = DefaultRouter()

comment_router.register(r'api/v1/posts/(?P<post_id>\d+)/comments',
                        CommentViewSet, basename='comment')
post_router.register(r'api/v1/posts', PostViewSet, basename='post')
follow_router.register(r'follow', FollowViewSet, basename='follow')
group_router.register(r'group', GroupViewSet, basename='group')

urlpatterns = (
        post_router.urls +
        comment_router.urls +
        follow_router.urls +
        group_router.urls
)

urlpatterns += [
    path('api/v1/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/v1/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]
