from django.contrib import admin
from .models import Event, EventRegistration


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ['title', 'organizer', 'date', 'location', 'registered_count', 'max_participants']
    list_filter = ['date', 'organizer', 'location']
    search_fields = ['title', 'description', 'location']
    readonly_fields = ['created_at', 'updated_at', 'registered_count']
    date_hierarchy = 'date'


@admin.register(EventRegistration)
class EventRegistrationAdmin(admin.ModelAdmin):
    list_display = ['user', 'event', 'registered_at']
    list_filter = ['registered_at', 'event']
    search_fields = ['user__username', 'event__title']
    readonly_fields = ['registered_at']
