from django.contrib.auth.models import User, Group

from rest_framework import viewsets

from . import models
from . import serializers


class UserViewSet(viewsets.ModelViewSet):
    """API endpoint that allows users to be viewed or edited.
    """
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = serializers.UserSerializer


class FieldViewSet(viewsets.ModelViewSet):
    """API endpoint that allows fields to be viewed or edited.
    """
    queryset = models.Field.objects.all()
    serializer_class = serializers.FieldSerializer


class DDRObjectViewSet(viewsets.ModelViewSet):
    """API endpoint that allows pointers to DDR objects to be viewed or edited.
    """
    queryset = models.DDRObject.objects.all()
    serializer_class = serializers.DDRObjectSerializer


class AnnotationViewSet(viewsets.ModelViewSet):
    """API endpoint that allows annotations to be viewed or edited.
    """
    queryset = models.Annotation.objects.all()
    serializer_class = serializers.AnnotationSerializer
