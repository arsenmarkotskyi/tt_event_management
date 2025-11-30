from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Event, EventRegistration


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']
        read_only_fields = ['id']


class EventSerializer(serializers.ModelSerializer):
    organizer = UserSerializer(read_only=True)
    registered_count = serializers.IntegerField(read_only=True)
    is_full = serializers.BooleanField(read_only=True)
    is_past = serializers.BooleanField(read_only=True)
    is_registered = serializers.SerializerMethodField()

    class Meta:
        model = Event
        fields = [
            'id', 'title', 'description', 'date', 'location',
            'organizer', 'max_participants', 'registered_count',
            'is_full', 'is_past', 'is_registered', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'organizer', 'created_at', 'updated_at']

    def get_is_registered(self, obj):
        """Check if current user is registered for this event."""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return EventRegistration.objects.filter(
                event=obj,
                user=request.user
            ).exists()
        return False

    def validate_date(self, value):
        """Ensure event date is in the future."""
        from django.utils import timezone
        if value < timezone.now():
            raise serializers.ValidationError("Event date cannot be in the past.")
        return value


class EventRegistrationSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    event = EventSerializer(read_only=True)

    class Meta:
        model = EventRegistration
        fields = ['id', 'event', 'user', 'registered_at']
        read_only_fields = ['id', 'user', 'registered_at']


class EventRegistrationCreateSerializer(serializers.Serializer):
    """Serializer for creating event registration."""
    event_id = serializers.IntegerField()

    def validate_event_id(self, value):
        """Validate that event exists and is not full."""
        try:
            event = Event.objects.get(id=value)
        except Event.DoesNotExist:
            raise serializers.ValidationError("Event does not exist.")

        if event.is_past:
            raise serializers.ValidationError("Cannot register for past events.")

        if event.is_full:
            raise serializers.ValidationError("Event is full.")

        # Check if user is already registered
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            if EventRegistration.objects.filter(event=event, user=request.user).exists():
                raise serializers.ValidationError("You are already registered for this event.")

        return value

    def create(self, validated_data):
        event = Event.objects.get(id=validated_data['event_id'])
        user = self.context['request'].user
        registration = EventRegistration.objects.create(event=event, user=user)
        return registration

