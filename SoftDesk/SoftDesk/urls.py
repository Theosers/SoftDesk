from django.contrib import admin
from django.urls import path
from django.conf.urls import include
from myApp.views import UserRegistrationViewset, ProjectViewSet, ProjectsView, ContributorsView, IssuesView, \
    ContributorsDeletionView, SoloCommentView, CommentsView
from rest_framework import routers
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

router = routers.SimpleRouter()

router.register('signup', UserRegistrationViewset, basename='signup')
router.register('projects', ProjectsView, basename='projects')
# router.register('project', ProjectViewSet, basename='project')
urlpatterns = [
    path('admin/', admin.site.urls),
    path('api-auth/', include('rest_framework.urls')),
    path('', include(router.urls)),
    path('login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('project/<int:id>/', ProjectViewSet.as_view({'get': 'retrieve', 'put': 'update', 'delete': 'destroy'})),
    path('project/<int:id>/users/', ContributorsView.as_view({'get': 'list', 'post': 'create'})),
    path('project/<int:id>/users/<int:user_id>/', ContributorsDeletionView.as_view({'delete': 'destroy'})),
    path('project/<int:id>/issues/', IssuesView.as_view({'get': 'list', 'post': 'create'})),
    path('project/<int:id>/issues/<int:issue_id>/', IssuesView.as_view({'put': 'update', 'delete': 'destroy'})),
    path('project/<int:id>/issues/<int:issue_id>/comments/', CommentsView.as_view({'post': 'create', 'get': 'list'})),
    path('project/<int:id>/issues/<int:issue_id>/comments/<int:comment_id>/',
         SoloCommentView.as_view({'get': 'retrieve', 'delete': 'destroy', "put": "update"})),

]
