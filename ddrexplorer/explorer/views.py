from collections import OrderedDict

from django.contrib.auth.models import User
from django.http import Http404, HttpResponseRedirect

from rest_framework import exceptions
from rest_framework import status
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework.views import APIView
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema

from . import models
from . import serializers


def index(request):
    return HttpResponseRedirect(
        reverse('api-index')
    )

@api_view(['GET'])
def api_index(request, format=None):
    """
    API Index
    Use the main DDR API (http://ddr.densho.org/api/0.2/) to browse collections.
    /accounts/register/ -- Register
    /api/v1/auth/login/ -- Login
    /api/swagger/ -- Swagger
    """
    data = OrderedDict()
    data['types'] = reverse('api-types', request=request)
    data['objects'] = reverse('api-objects', request=request)
    return Response(data)

@api_view(['GET'])
def types(request, format=None):
    """
    Lists valid annotation types.
    """
    return Response(
        models.Field.fields(request)
    )

@api_view(['GET'])
def objects(request, format=None):
    """
    Lists objects with annotations.
    """
    return Response(
        models.objects_all(request)
    )

@api_view(['GET'])
def object_detail(request, object_id, format=None):
    """
    Lists all annotations for object.
    """
    return Response(
        models.Annotation.for_object(object_id, request)
    )

@api_view(['GET'])
def user(request, username, format=None):
    """
    Lists all objects annotated by user.
    """
    # TODO 404 if not logged in or not this user
    user = User.objects.get(username=username)
    data = OrderedDict()
    data['username'] = user.username
    data['objects'] = models.Annotation.for_user(user, request)
    return Response(data)


class Annotations(APIView):
    """
    Lists Annotations belonging to logged-in User
    """
    @permission_classes((IsAuthenticated, ))
    def get(self, request, format=None):
        """
        Lists Annotations belonging to the logged-in User
        """
        data = OrderedDict()
        data['username'] = request.user.username
        data['objects'] = models.Annotation.for_user(request.user, request)
        return Response(data)

    @permission_classes((IsAuthenticated, ))
    @swagger_auto_schema(manual_parameters=[
        openapi.Parameter(
            'user_id', description='string',
            in_=openapi.IN_FORM, type=openapi.TYPE_STRING),
        openapi.Parameter(
            'object_id', description='string',
            in_=openapi.IN_FORM, type=openapi.TYPE_STRING),
        openapi.Parameter(
            'field_id', description='string',
            in_=openapi.IN_FORM, type=openapi.TYPE_STRING),
        openapi.Parameter(
            'content', description='JSON document containing annotation.',
            in_=openapi.IN_FORM, type=openapi.TYPE_STRING),
    ])
    def post(self, request, format=None):
        """
        Create a new Annotation for the logged-in user.
        """
        data = {
            'user_id': request.user.id,
            'object_id': object_id,
            'field_id': field_id,
            'content': request.data,
        }
        serializer = serializers.AnnotationSerializer(
            data=data,
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AnnotationDetail(APIView):
    """
    """
    def get_object(self, annotation_id):
        try:
            return models.Annotation.objects.get(id=annotation_id)
        except Annotation.DoesNotExist:
            raise Http404
    
    def get(self, request, annotation_id, format=None):
        """
        Get an Annotation
        """
        a = self.get_object(annotation_id)
        return Response(
            a.dict(request)
        )
    
    @permission_classes((IsAuthenticated, ))
    @swagger_auto_schema(manual_parameters=[
        openapi.Parameter(
            'content', description='JSON document containing annotation.',
            in_=openapi.IN_FORM, type=openapi.TYPE_STRING),
    ])
    def post(self, request, annotation_id, format=None):
        """
        Update an Annotation
        """
        a = self.get_object(annotation_id)
        if not (request.user.id == a.user_id):
            raise exceptions.PermissionDenied(detail=None, code=None)
        data = {
            'user_id': request.user.id,
            'object_id': annotation_id,
            'field_id': field_id,
            'content': request.data,
        }
        serializer = serializers.AnnotationSerializer(
            annotation,
            request.data,
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
    @permission_classes((IsAuthenticated, ))
    def delete(self, request, annotation_id, format=None):
        """
        Delete an Annotation
        """
        a = self.get_object(annotation_id)
        if not (request.user.id == a.user_id):
            raise exceptions.PermissionDenied(detail=None, code=None)
        a.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class CustomAuthToken(ObtainAuthToken):
    """
    Wrapper around rest_framework.authtoken.views.obtain_auth_token that works
    with Swagger UI.
    see https://www.django-rest-framework.org/api-guide/authentication/#tokenauthentication
    """

    @swagger_auto_schema(manual_parameters=[
        openapi.Parameter(
            'username', description='string',
            in_=openapi.IN_FORM, type=openapi.TYPE_STRING),
        openapi.Parameter(
            'password', description='string',
            in_=openapi.IN_FORM, type=openapi.TYPE_STRING),
    ])
    def post(self, request, *args, **kwargs):
        """Get a token for the given username and password.
        
        POST with form fields "username" and "password".
        Can't get it to work with Swagger UI sorry.
        """
        serializer = self.serializer_class(
            data=request.data,
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        return Response({
            'token': token.key,
        })
