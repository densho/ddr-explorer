from django.contrib.auth.models import User
from rest_framework import serializers

from . import models


class AnnotationSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    user_id = serializers.IntegerField(required=True)
    object_id = serializers.CharField(required=True)
    field_id = serializers.CharField(required=True)
    content = serializers.JSONField(required=True)
        
    def create(self, validated_data):
        """
        Create and return a new `Annotation` instance given validated data.
        """
        # check that field exists
        #try:
        #    field = models.Field.objects.get(validated_data['field_id'])
        #except:
        #    raise Exception('Field {} does not exist.'.format(field_id))
        
        # check object exists
        if not models.object_exists(validated_data['object_id']):
            raise Exception(
                'Object {} not in ddrpublic.'.format(validated_data['object_id'])
            )
        
        a = models.Annotation()
        a.user = User.objects.get(id=validated_data['user_id'])
        a.object_id = validated_data['object_id']
        a.field_id = validated_data['field_id']
        a.content = validated_data['content']
        a.save()
        return a

    def update(self, item, validated_data):
        """
        Update and return an existing `Annotation` instance given validated data.
        """
        assert False
        item.content = validated_data.get('content', item.content)
        item.save()
        return item
