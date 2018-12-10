from django.urls import include, path, re_path

#from rest_framework import routers
from rest_framework_swagger.views import get_swagger_view
schema_view = get_swagger_view(title='Pastebin API')

from . import views

#router = routers.DefaultRouter()
#router.register(r'users', views.UserViewSet)
#router.register(r'fields', views.FieldViewSet)
#router.register(r'objects', views.DDRObjectViewSet)
#router.register(r'annotations', views.AnnotationViewSet)

# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browsable API.
urlpatterns = [
    path(r'api/v1/auth/', include('rest_framework.urls', namespace='rest_framework')),
    #path('api/v1/', include(router.urls)),
    path(r'api/v1/annotations/new/', views.annotation, name='api-annotation'),
    path(r'api/v1/annotations/<slug:annotation_id>/', views.annotation, name='api-annotation'),
    path(r'api/v1/objects/<slug:object_id>/', views.object_detail, name='api-object'),
    path(r'api/v1/users/<slug:username>/', views.user, name='api-user'),
    path(r'api/v1/objects/', views.objects, name='api-objects'),
    path(r'api/v1/types/', views.types, name='api-types'),
    path(r'api/v1/', views.api_index, name='api-index'),
    path(r'', schema_view)
]
