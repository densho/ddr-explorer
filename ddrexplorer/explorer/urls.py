from django.urls import include, path, re_path

from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import permissions

from . import views

API_DESCRIPTION = """
API DESCRIPTION TEXT GOES HERE.
"""

api_info = openapi.Info(
    title="DDR Explorer API",
    default_version='v1',
    description=API_DESCRIPTION,
    terms_of_service="http://ddr.densho.org/terms/",
    contact=openapi.Contact(email="info@densho.org"),
    license=openapi.License(name="License TBD"),
)
schema_view = get_schema_view(
    #api_info,
    url=settings.SWAGGER_BASE_URL,
    #patterns=
    #urlconf=
    public=True,
    #validators=['flex', 'ssv'],
    #generator_class=
    #authentication_classes=
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path(r'api/v1/auth/',
         include('rest_framework.urls', namespace='rest_framework')
    ),
    path(r'api/v1/objects/<slug:object_id>/',
         views.object_detail, name='api-object'
    ),
    path(r'api/v1/annotation/<slug:annotation_id>/',
         views.AnnotationDetail.as_view(), name='api-annotation'
    ),
    path(r'api/v1/annotations/',
         views.Annotations.as_view(), name='api-annotations'
    ),
    path(r'api/v1/objects/', views.objects, name='api-objects'),
    path(r'api/v1/types/', views.types, name='api-types'),
    path(r'api/v1/', views.api_index, name='api-index'),
    
    path(r'api/swagger<slug:format>\.json|\.yaml)',
         schema_view.without_ui(cache_timeout=0), name='schema-json'
    ),
    path(r'api/swagger/',
         schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'
    ),
    path(r'api/redoc/',
         schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'
    ),
    
    path(r'', views.index)
]
