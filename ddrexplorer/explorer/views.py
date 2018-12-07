from collections import OrderedDict

from django.contrib.auth.models import User
from django.http import HttpResponseRedirect

from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.reverse import reverse

from . import models


def index(request):
    return HttpResponseRedirect(
        reverse('api-index')
    )

@api_view(['GET'])
def api_index(request, format=None):
    """API Index
    Use the main DDR API (http://ddr.densho.org/api/0.2/) to browse collections.
    Register /accounts/register/
    Login /api/v1/auth/login/
    """
    data = OrderedDict()
    data['types'] = reverse('api-types', request=request)
    data['objects'] = reverse('api-objects', request=request)
    return Response(data)

@api_view(['GET'])
def types(request):
    """
    Lists valid annotation types.
    """
    return Response(
        models.Field.fields(request)
    )

@api_view(['GET'])
def objects(request):
    """
    Lists objects with annotations.
    """
    return Response(
        models.objects_all(request)
    )

@api_view(['GET'])
def object_detail(request, object_id):
    """
    Lists all annotations for object.
    POST api/v1/annotations/new/ to create a new annotation.
    """
    return Response(
        models.Annotation.for_object(object_id, request)
    )

@api_view(['GET'])
def user(request, username):
    """
    Lists all objects annotated by user.
    """
    # TODO 404 if not logged in or not this user
    user = User.objects.get(username=username)
    data = OrderedDict()
    data['username'] = user.username
    data['objects'] = models.Annotation.for_user(user, request)
    return Response(data)

@api_view(['GET', 'POST', 'DELETE'])
def annotation(request, annotation_id=None):
    """
    POST api/v1/annotations/new/ to create a new annotation.
    POST api/v1/annotations/ID/ to edit an existing one.
    Users may only edit their own annotations.
    Use annotation types from /api/v1/types/.
    """
    # TODO POST,DELETE only if logged in AND matches annotation user
    if annotation_id:
        return Response(
            models.Annotation.objects.get(id=annotation_id).dict(request)
        )
    # new Annotation
    return Response({})
