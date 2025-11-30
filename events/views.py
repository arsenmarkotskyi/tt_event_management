from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django_filters import FilterSet, rest_framework
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from .models import Event, EventRegistration
from .serializers import (
    EventSerializer,
    EventRegistrationSerializer,
    EventRegistrationCreateSerializer
)
from .permissions import IsOwnerOrReadOnly


class EventFilter(FilterSet):
    """Filter for events by date range, location, and organizer."""
    date_from = rest_framework.DateTimeFilter(field_name='date', lookup_expr='gte')
    date_to = rest_framework.DateTimeFilter(field_name='date', lookup_expr='lte')
    location = rest_framework.CharFilter(field_name='location', lookup_expr='icontains')
    organizer = rest_framework.NumberFilter(field_name='organizer__id', method='filter_organizer')
    is_upcoming = rest_framework.BooleanFilter(method='filter_upcoming')

    class Meta:
        model = Event
        fields = ['date_from', 'date_to', 'location', 'organizer', 'is_upcoming']

    def filter_organizer(self, queryset, name, value):
        """Filter events by organizer ID with validation."""
        if value is not None:
            try:
                # Переконатися, що value - це число
                organizer_id = int(value)
                return queryset.filter(organizer__id=organizer_id)
            except (ValueError, TypeError):
                # Якщо не число, повернути порожній queryset
                return queryset.none()
        return queryset

    def filter_upcoming(self, queryset, name, value):
        """Filter events that are upcoming (date >= now)."""
        if value:
            return queryset.filter(date__gte=timezone.now())
        return queryset


class EventViewSet(viewsets.ModelViewSet):
    """
    ViewSet for viewing and editing Event instances.
    
    list:
    Return a list of all events with search and filtering capabilities.
    
    retrieve:
    Return a specific event by id.
    
    create:
    Create a new event. Requires authentication.
    
    update:
    Update an event. Only the organizer can update.
    
    destroy:
    Delete an event. Only the organizer can delete.
    """
    queryset = Event.objects.all()
    serializer_class = EventSerializer
    permission_classes = [IsOwnerOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = EventFilter
    search_fields = ['title', 'description', 'location']
    ordering_fields = ['date', 'created_at', 'title']
    ordering = ['-date']

    def get_serializer_context(self):
        """Add request to serializer context."""
        context = super().get_serializer_context()
        context['request'] = self.request
        return context

    def perform_create(self, serializer):
        """Set the organizer to the current user when creating an event."""
        serializer.save(organizer=self.request.user)

    @swagger_auto_schema(
        method='post',
        request_body=None,  # Не потрібен body
        responses={
            201: openapi.Response(
                description='Successfully registered for event',
                schema=openapi.Schema(type=openapi.TYPE_OBJECT)
            ),
            400: openapi.Response(description='Bad request - already registered, event full, or past event'),
            401: openapi.Response(description='Authentication required'),
            404: openapi.Response(description='Event not found'),
        },
        operation_description='Register the current authenticated user for an event. No request body required. The user is automatically determined from the authentication token.',
        security=[{'Token': []}]
    )
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def register(self, request, pk=None):
        """
        Register the current user for an event.
        
        No request body is required. The user is automatically determined from the authentication token.
        """
        event = self.get_object()
        serializer = EventRegistrationCreateSerializer(
            data={'event_id': event.id},
            context={'request': request}
        )

        if serializer.is_valid():
            registration = serializer.save()

            # Send email notification (bonus feature)
            try:
                send_registration_email(event, request.user)
            except Exception as e:
                # Log error but don't fail the registration
                print(f"Failed to send email: {e}")

            response_serializer = EventRegistrationSerializer(
                registration,
                context={'request': request}
            )
            return Response(
                response_serializer.data,
                status=status.HTTP_201_CREATED
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['delete'], permission_classes=[IsAuthenticated])
    def unregister(self, request, pk=None):
        """
        Unregister the current user from an event.
        """
        event = self.get_object()
        try:
            registration = EventRegistration.objects.get(
                event=event,
                user=request.user
            )
            registration.delete()
            return Response(
                {'message': 'Successfully unregistered from event'},
                status=status.HTTP_200_OK
            )
        except EventRegistration.DoesNotExist:
            return Response(
                {'error': 'You are not registered for this event'},
                status=status.HTTP_404_NOT_FOUND
            )

    @action(detail=True, methods=['get'], permission_classes=[IsAuthenticated])
    def registrations(self, request, pk=None):
        """
        Get list of all registrations for an event.
        Only the organizer can view registrations.
        """
        event = self.get_object()
        if event.organizer != request.user:
            return Response(
                {'error': 'Only the organizer can view registrations'},
                status=status.HTTP_403_FORBIDDEN
            )

        registrations = EventRegistration.objects.filter(event=event)
        serializer = EventRegistrationSerializer(registrations, many=True)
        return Response(serializer.data)


class EventRegistrationViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for viewing EventRegistration instances.
    Users can only view their own registrations.
    """
    serializer_class = EventRegistrationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Return only registrations for the current user."""
        return EventRegistration.objects.filter(user=self.request.user)


def send_registration_email(event, user):
    """Send email notification when user registers for an event."""
    subject = f'Registration Confirmation: {event.title}'
    message = f"""
    Hello {user.username},

    You have successfully registered for the event:

    Event: {event.title}
    Date: {event.date.strftime('%Y-%m-%d %H:%M')}
    Location: {event.location}

    Description:
    {event.description}

    We look forward to seeing you there!

    Best regards,
    Event Management Team
    """
    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL or 'noreply@eventmanagement.com',
        [user.email],
        fail_silently=False,
    )
