from django.contrib.auth.models import User

from rest_framework import serializers

from . import models


class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ('url', 'username', 'email', 'groups')


class FieldSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.Field
        fields = ('field_id', 'title')


class DDRObjectSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.DDRObject
        fields = ('object_id', 'title')


class AnnotationSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.Annotation
        fields = ('user', 'ddrobject', 'field', 'created', 'lastmod', 'content')
