from django.urls import path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from .views import (
    ProjectAPIView,
    create_project,
    project_detail,
    project_list,
    update_project,
)

urlpatterns = [
    # API Endpoints
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/projects/', ProjectAPIView.as_view(), name='project-api-list'),
    path('api/projects/<int:pk>/', ProjectAPIView.as_view(), name='project-api-detail'),
    
    # HTML Endpoints
    path('projects/', project_list, name='project_list'),
    path('projects/<int:pk>/', project_detail, name='project_detail'),
    path('projects/create/', create_project, name='create_project'),
    path('projects/update/<int:pk>/', update_project, name='update_project'),
    # path('projects/delete/<int:pk>/', delete_project, name='delete_project'),
]