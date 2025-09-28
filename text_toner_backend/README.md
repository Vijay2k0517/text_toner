# Tone Analyzer Backend

A comprehensive Python backend for a tone-analyzing chatbot application that uses FastAPI, Hugging Face NLP models, and MongoDB to provide intelligent text tone analysis and improvement suggestions.

## Features

- **Text Tone Analysis**: Analyze text to detect tones like formal, friendly, apologetic, assertive, emotional, professional, casual, and enthusiastic
- **AI-Powered Suggestions**: Get intelligent suggestions for improving message tone
- **User Management**: Complete user authentication and management system
- **Message History**: Store and retrieve user messages with tone analysis
- **Feedback System**: Collect and analyze user feedback on tone accuracy and suggestions
- **RESTful API**: Clean, well-documented API endpoints for React Native frontend integration
- **Scalable Architecture**: Modular design with separate services for different functionalities

## Tech Stack

- **Framework**: FastAPI (Python)
- **Database**: MongoDB with PyMongo
- **AI/ML**: Hugging Face Transformers (sentiment analysis)
- **Authentication**: JWT tokens with bcrypt password hashing
- **Documentation**: Auto-generated OpenAPI/Swagger docs
- **Testing**: pytest for unit and integration tests

## Prerequisites

- Python 3.8+
- MongoDB (local or cloud instance)
- Hugging Face account (optional, for custom models)

## Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd text_toner
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   cp env.example .env
   # Edit .env with your configuration
   ```

5. **Configure MongoDB**
   - Install MongoDB locally or use MongoDB Atlas
   - Update `MONGODB_URI` in your `.env` file

6. **Run the application**
   ```bash
   python -m app.main
   ```

## Environment Configuration

Create a `.env` file with the following variables:

```env
# MongoDB Configuration
MONGODB_URI=mongodb://localhost:27017
MONGODB_DATABASE=tone_analyzer_db

# Hugging Face Model Configuration
HUGGINGFACE_MODEL=cardiffnlp/twitter-roberta-base-sentiment-latest
HUGGINGFACE_TOKEN=your_huggingface_token_here

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
DEBUG=True

# Security
SECRET_KEY=your_secret_key_here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# CORS Configuration
ALLOWED_ORIGINS=["http://localhost:3000", "http://localhost:8081"]
```

## API Endpoints

### Authentication
- `POST /api/v1/auth/register` - Register a new user
- `POST /api/v1/auth/login` - Login and get access token
- `GET /api/v1/auth/me` - Get current user info
- `POST /api/v1/auth/change-password` - Change password
- `DELETE /api/v1/auth/deactivate` - Deactivate account

### Tone Analysis
- `POST /api/v1/tone/analyze` - Analyze text tone (public)
- `POST /api/v1/tone/messages` - Create message with analysis
- `GET /api/v1/tone/messages` - Get user messages
- `GET /api/v1/tone/messages/{id}` - Get specific message
- `GET /api/v1/tone/messages/tone/{tone}` - Filter by tone
- `GET /api/v1/tone/messages/search` - Search messages
- `DELETE /api/v1/tone/messages/{id}` - Delete message
- `GET /api/v1/tone/stats` - Get user statistics
- `GET /api/v1/tone/supported-tones` - Get supported tones

### Feedback
- `POST /api/v1/feedback/` - Create feedback
- `GET /api/v1/feedback/{id}` - Get feedback
- `GET /api/v1/feedback/message/{id}` - Get feedback by message
- `GET /api/v1/feedback/user/me` - Get user feedback
- `PUT /api/v1/feedback/{id}` - Update feedback
- `DELETE /api/v1/feedback/{id}` - Delete feedback
- `GET /api/v1/feedback/stats/overall` - Get feedback statistics

### System
- `GET /` - API information
- `GET /health` - Health check
- `GET /api/v1/info` - Detailed API info
- `GET /docs` - Interactive API documentation

## Usage Examples

### 1. Register a User
```bash
curl -X POST "http://localhost:8000/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "john_doe",
    "email": "john@example.com",
    "password": "securepassword123",
    "confirm_password": "securepassword123"
  }'
```

### 2. Login and Get Token
```bash
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=john_doe&password=securepassword123"
```

### 3. Analyze Text Tone
```bash
curl -X POST "http://localhost:8000/api/v1/tone/analyze" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Hey there! How are you doing today?",
    "context": "casual conversation"
  }'
```

### 4. Create Message with Analysis
```bash
curl -X POST "http://localhost:8000/api/v1/tone/messages" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "I would like to request a meeting to discuss the project timeline.",
    "context": "professional email"
  }'
```

### 5. Get User Messages
```bash
curl -X GET "http://localhost:8000/api/v1/tone/messages" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

## React Native Integration

The API is designed to work seamlessly with React Native applications. Here's a basic example:

```javascript
// API configuration
const API_BASE_URL = 'http://localhost:8000/api/v1';

// Analyze text tone
const analyzeTone = async (text) => {
  try {
    const response = await fetch(`${API_BASE_URL}/tone/analyze`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ text }),
    });
    return await response.json();
  } catch (error) {
    console.error('Error analyzing tone:', error);
  }
};

// Create message with authentication
const createMessage = async (text, token) => {
  try {
    const response = await fetch(`${API_BASE_URL}/tone/messages`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`,
      },
      body: JSON.stringify({ text }),
    });
    return await response.json();
  } catch (error) {
    console.error('Error creating message:', error);
  }
};
```

## Project Structure

```
text_toner/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI application
│   ├── config.py            # Configuration settings
│   ├── database.py          # MongoDB connection
│   ├── models.py            # Pydantic models
│   ├── routes/              # API routes
│   │   ├── __init__.py
│   │   ├── auth.py          # Authentication routes
│   │   ├── tone_analysis.py # Tone analysis routes
│   │   └── feedback.py      # Feedback routes
│   └── services/            # Business logic
│       ├── __init__.py
│       ├── tone_analyzer.py # AI model integration
│       ├── message_service.py # Message management
│       ├── user_service.py  # User management
│       └── feedback_service.py # Feedback management
├── requirements.txt         # Python dependencies
├── env.example             # Environment variables template
├── README.md               # This file
└── tests/                  # Test files (to be added)
```

## Testing

Run the test suite:
```bash
pytest tests/
```

## Development

### Running in Development Mode
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Accessing API Documentation
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Deployment

### Docker Deployment
```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Environment Variables for Production
- Set `DEBUG=False`
- Use a strong `SECRET_KEY`
- Configure production MongoDB URI
- Set appropriate CORS origins

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

This project is licensed under the MIT License.

## Support

For support and questions, please open an issue in the repository.
