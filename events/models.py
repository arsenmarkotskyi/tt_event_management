from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from django.utils import timezone


class Event(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    date = models.DateTimeField()
    location = models.CharField(max_length=200)
    organizer = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='organized_events'
    )
    max_participants = models.PositiveIntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(1)],
        help_text="Maximum number of participants. Leave empty for unlimited."
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-date']
        indexes = [
            models.Index(fields=['-date']),
            models.Index(fields=['organizer']),
        ]

    def __str__(self):
        return self.title

    @property
    def registered_count(self):
        """Return the number of registered participants."""
        return self.registrations.count()

    @property
    def is_full(self):
        """Check if event is full."""
        if self.max_participants is None:
            return False
        return self.registered_count >= self.max_participants

    @property
    def is_past(self):
        """Check if event date has passed."""
        return self.date < timezone.now()


class EventRegistration(models.Model):
    event = models.ForeignKey(
        Event,
        on_delete=models.CASCADE,
        related_name='registrations'
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='event_registrations'
    )
    registered_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['event', 'user']
        ordering = ['-registered_at']
        indexes = [
            models.Index(fields=['event', 'user']),
        ]

    def __str__(self):
        return f"{self.user.username} - {self.event.title}"
