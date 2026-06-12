from django.contrib import admin
from .models import Event, EventPhoto, EventDocument


class PhotoInline(admin.TabularInline):
    model = EventPhoto
    extra = 1


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('title', 'date', 'location', 'created_by')
    search_fields = ('title', 'location')
    list_filter = ('date',)
    inlines = [PhotoInline]


@admin.register(EventPhoto)
class PhotoAdmin(admin.ModelAdmin):
    list_display = ('event', 'caption', 'uploaded_by', 'uploaded_at')
    list_filter = ('event', 'uploaded_by')


@admin.register(EventDocument)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ('event', 'title', 'uploaded_by', 'uploaded_at')
    list_filter = ('event', 'uploaded_by')
    search_fields = ('title', 'event__title')
