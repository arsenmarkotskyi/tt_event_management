# Event Management API

Django REST API for managing events (conferences, meetups, etc.) with user registration functionality.

## Features

- ✅ **Event Management**: Full CRUD operations for events
- ✅ **User Authentication**: Registration and login with token-based authentication
- ✅ **Event Registration**: Users can register/unregister for events
- ✅ **Search & Filtering**: Search events by title, description, location and filter by date, organizer
- ✅ **Email Notifications**: Automatic email notifications when users register for events
- ✅ **API Documentation**: Interactive Swagger/OpenAPI documentation
- ✅ **Docker Support**: Ready-to-use Docker configuration

## Requirements

- Python 3.11+
- Django 5.2.8
- Django REST Framework 3.16.1
- PostgreSQL (for production) or SQLite (for development)

## Installation

### Local Development

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd tt_event_management
   ```

2. **Create and activate virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run migrations**
   ```bash
   python manage.py migrate
   ```

5. **Create superuser (optional)**
   ```bash
   python manage.py createsuperuser
   ```

6. **Run development server**
   ```bash
   python manage.py runserver
   ```

The API will be available at `http://localhost:8000/`

### Docker

1. **Build and run with Docker Compose**
   ```bash
   docker-compose up --build
   ```

2. **Create superuser (in a new terminal)**
   ```bash
   docker-compose exec web python manage.py createsuperuser
   ```

The API will be available at `http://localhost:8000/`

## API Endpoints

### Authentication

- `POST /api/accounts/register/` - Register a new user
- `POST /api/accounts/login/` - Login and get authentication token
- `POST /api/accounts/logout/` - Logout (delete token)
- `GET /api/accounts/profile/` - Get current user profile

### Events

- `GET /api/events/` - List all events (with search and filtering)
- `POST /api/events/` - Create a new event (requires authentication)
- `GET /api/events/{id}/` - Get event details
- `PUT /api/events/{id}/` - Update event (only organizer)
- `PATCH /api/events/{id}/` - Partially update event (only organizer)
- `DELETE /api/events/{id}/` - Delete event (only organizer)

### Event Registration

- `POST /api/events/{id}/register/` - Register for an event
- `DELETE /api/events/{id}/unregister/` - Unregister from an event
- `GET /api/events/{id}/registrations/` - Get list of registrations (organizer only)
- `GET /api/registrations/` - Get current user's registrations

### API Documentation

- `GET /swagger/` - Swagger UI documentation
- `GET /redoc/` - ReDoc documentation
- `GET /api/docs/` - Alternative Swagger UI endpoint

## API Usage Examples

### 1. Register a new user

```bash
curl -X POST http://localhost:8000/api/accounts/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "john_doe",
    "email": "john@example.com",
    "password": "securepass123",
    "password_confirm": "securepass123",
    "first_name": "John",
    "last_name": "Doe"
  }'
```

Response:
```json
{
  "user": {
    "id": 1,
    "username": "john_doe",
    "email": "john@example.com",
    "first_name": "John",
    "last_name": "Doe"
  },
  "token": "abc123...",
  "message": "User created successfully"
}
```

### 2. Login

```bash
curl -X POST http://localhost:8000/api/accounts/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "john_doe",
    "password": "securepass123"
  }'
```

### 3. Create an event

```bash
curl -X POST http://localhost:8000/api/events/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Token abc123..." \
  -d '{
    "title": "Python Conference 2024",
    "description": "Annual Python developers conference",
    "date": "2024-12-15T10:00:00Z",
    "location": "Kyiv, Ukraine",
    "max_participants": 100
  }'
```

### 4. List events with filtering

```bash
# Filter by date range
curl "http://localhost:8000/api/events/?date_from=2024-12-01T00:00:00Z&date_to=2024-12-31T23:59:59Z"

# Search by title or description
curl "http://localhost:8000/api/events/?search=Python"

# Filter by location
curl "http://localhost:8000/api/events/?location=Kyiv"

# Filter upcoming events only
curl "http://localhost:8000/api/events/?is_upcoming=true"

# Combine filters
curl "http://localhost:8000/api/events/?search=conference&is_upcoming=true&ordering=-date"
```

### 5. Register for an event

```bash
curl -X POST http://localhost:8000/api/events/1/register/ \
  -H "Authorization: Token abc123..."
```

### 6. Get event details

```bash
curl http://localhost:8000/api/events/1/ \
  -H "Authorization: Token abc123..."
```

Response includes:
- Event information
- `is_registered`: Whether current user is registered
- `registered_count`: Number of registered participants
- `is_full`: Whether event is full
- `is_past`: Whether event date has passed

## Filtering and Search

The API supports advanced filtering and search:

- **Search**: `?search=keyword` - Searches in title, description, and location
- **Date Range**: `?date_from=YYYY-MM-DDTHH:MM:SSZ&date_to=YYYY-MM-DDTHH:MM:SSZ`
- **Location**: `?location=city` - Case-insensitive partial match
- **Organizer**: `?organizer=user_id` - Filter by organizer ID
- **Upcoming**: `?is_upcoming=true` - Only future events
- **Ordering**: `?ordering=-date` - Order by date (descending)
- **Pagination**: Results are paginated (20 per page by default)

## Email Notifications

When a user registers for an event, an email notification is automatically sent (in development mode, emails are printed to console).

To configure SMTP for production, update `settings.py`:

```python
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'your-email@gmail.com'
EMAIL_HOST_PASSWORD = 'your-password'
```

## Project Structure

```
tt_event_management/
├── accounts/          # User authentication app
│   ├── serializers.py
│   ├── views.py
│   └── urls.py
├── events/            # Events management app
│   ├── models.py
│   ├── serializers.py
│   ├── views.py
│   ├── permissions.py
│   └── urls.py
├── event_management/  # Main project settings
│   ├── settings.py
│   └── urls.py
├── Dockerfile
├── docker-compose.yml
└── requirements.txt
```

## Testing

Run tests:
```bash
python manage.py test
```

## License

This project is licensed under the BSD License.
