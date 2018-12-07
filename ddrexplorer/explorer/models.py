"""
app logs in using django_registration (for now)
app knows username
app gets object ids from ddrpublic API
annotations are attached to objects and users
users can add annotation to any object in ddrpublic
new annotation.object_id has to match a ddrpublic API object_id
users can only edit their own annotations
annotation.field has to match a field_id
users can only edit their own user info
"""

from collections import OrderedDict
from datetime import datetime
import json

from django.contrib.auth.models import User
from django.db import models

import requests
from rest_framework.exceptions import NotFound
from rest_framework.reverse import reverse


class Field(models.Model):
    id = models.CharField(max_length=255, primary_key=True)
    title = models.CharField(max_length=255)
    
    def __repr__(self):
        return '<Field {}>'.format(self.id)
    
    @staticmethod
    def fields(request):
        return [
            x.dict(request)
            for x in Field.objects.all()
        ]
    
    def dict(self, request):
        data = OrderedDict()
        data['id'] = self.id
        data['title'] = self.title
        return data


def objects_all(request):
    return set([
        reverse('api-object', args=(x.object_id,), request=request)
        for x in Annotation.objects.all()
    ])

def object_exists(object_id):
    """Indicates whether object_id present in ddrpublic
    """
    url = 'https://ddr.densho.org/api/0.2/{}/'.format(object_id)
    print(url)
    r = requests.get(url)
    print(r)
    if r.status_code == 200:
        try:
            o = json.loads(r.text)
            if o.get('id') and (o['id'] == object_id):
                return True
        except json.decoder.JSONDecodeError:
            pass
    return False


class Annotation(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    object_id = models.CharField(max_length=255)
    field_id = models.CharField(max_length=255)
    created = models.DateTimeField(auto_now_add=True)
    lastmod = models.DateTimeField(auto_now=True)
    content = models.TextField()
    
    def __repr__(self):
        return '<Annotation {}:{}:{}:{}>'.format(
            self.id, self.user.username, self.object_id, self.field_id
        )
    
    @staticmethod
    def for_object(object_id, request=None):
        try:
            return [
                a.dict(request)
                for a in Annotation.objects.filter(object_id=object_id)
            ]
        except Annotation.DoesNotExist:
            raise NotFound('No annotations for {}'.format(object_id))
    
    @staticmethod
    def for_user(user, request=None):
        return set([
            reverse('api-object', args=(x.object_id,), request=request)
            for x in Annotation.objects.filter(user=user)
        ])
            
    @staticmethod
    def new(user, object_id, field_id, contents):
        # check that field exists
        try:
            field = Field.objects.get(field_id)
        except:
            raise Exception('Field {} does not exist.'.format(field_id))
        # check object exists
        if not object_exists(object_id):
            raise Exception('Object {} not in ddrpublic.'.format(object_id))
        
        a = Annotation()
        a.user_id = user.id
        a.username = user.username
        a.object_id = object_id
        a.field_id = field_id
        a.created = datetime.now()
        a.lastmod = datetime.now()
        a.content = content
    
    def can_edit(self, user):
        if user.username == self.user.username:
            return True
        return False
    
    def dict(self, request):
        data = OrderedDict()
        data['id'] = reverse(
            'api-annotation', args=(self.id,), request=request
        )
        data['object_id'] = reverse(
            'api-object', args=(self.object_id,), request=request
        )
        data['username'] = reverse(
            'api-user', args=(self.user.username,), request=request
        )
        data['field_id'] = self.field_id
        data['created'] = self.created
        data['lastmod'] = self.lastmod
        data['content'] = self.content
        return data
    
    def admin_link(self):
        return '{}:{}:{}'.format(
            self.user.username, self.object_id, self.field_id
        )
    
    def admin_display(self):
        return '<Annotation {}:{}:{}'.format(
            self.user.username, self.object_id, self.field_id
        )
