from django.contrib import admin

from . import models

class FieldAdmin(admin.ModelAdmin):
    list_display = ('field_id', 'title')

class DDRObjectAdmin(admin.ModelAdmin):
    list_display = ('object_id', 'title')

class AnnotationAdmin(admin.ModelAdmin):
    list_display = ('admin_link', 'admin_display')
    date_hierarchy = 'created'

admin.site.register(models.Field, FieldAdmin)
admin.site.register(models.DDRObject, DDRObjectAdmin)
admin.site.register(models.Annotation, AnnotationAdmin)
