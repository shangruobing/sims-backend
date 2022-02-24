from django.contrib import admin
from django.urls import path
from sims.views import *

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/login/', LoginAPIView.as_view()),

    path('api/student/', StudentListView.as_view()),
    path('api/student/<int:pk>/', StudentView.as_view()),

    path('api/user/', UserListView.as_view()),
    path('api/user/<int:pk>/', UserView.as_view()),

    path('api/course/', CourseListView.as_view()),
    path('api/course/<int:pk>/', CourseView.as_view()),

    path('api/teacher/', TeacherListView.as_view()),
    path('api/teacher/<int:pk>/', TeacherView.as_view()),

    path('api/class/', ClassViewSet.as_view({'get': 'list', 'post': 'list'})),
    path('api/class/<int:pk>/', ClassViewSet.as_view({'get': 'retrieve'})),

    path('api/score/', ScoreListView.as_view()),
    path('api/score/<int:pk>/', ScoreView.as_view()),

    # path('test/user/', UserListGenericViewSet.as_view({'get': 'list', 'post': 'list'})),
]
