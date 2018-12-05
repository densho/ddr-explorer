from django.contrib.auth.models import User
from django.db import models


class Field(models.Model):
    field_id = models.CharField(max_length=255, primary_key=True)
    title = models.CharField(max_length=255)
    
    def __repr__(self):
        return '<Field {}>'.format(self.field_id)


class DDRObject(models.Model):
    object_id = models.CharField(max_length=255, primary_key=True)
    title = models.CharField(max_length=255)
    
    def __repr__(self):
        return '<DDRObject %s>' % (self.object_id)


class Annotation(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    ddrobject = models.ForeignKey(DDRObject, on_delete=models.CASCADE)
    field = models.ForeignKey(Field, on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)
    lastmod = models.DateTimeField(auto_now=True)
    content = models.TextField()
    
    def __repr__(self):
        return '<Annotation {}:{}:{}'.format(
            self.user.id, self.object_id, self.field_id
        )
    
    def admin_link(self):
        return '{}:{}:{}'.format(
            self.user.username, self.ddrobject.object_id, self.field.field_id
        )
    
    def admin_display(self):
        return '{}:{}:{}'.format(
            self.user.username, self.ddrobject.object_id, self.field.field_id
        )
