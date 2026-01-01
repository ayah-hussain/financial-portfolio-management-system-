# PortfolioVantage

A comprehensive financial portfolio management system with news tracking capabilities, developed as part of the ITU BLG317E Database Systems course project.

## Course Information
- **Course**: BLG317E - Database Systems
- **CRN**: 13594
- **Department**: ITU Department of AI and Data Engineering

### Team Members
- Ruşen Birben - 150220755
- Anıl Dervişoğlu - 150220344
- Ayah A M Hussein - 150220917
- Göktürk Batın Dervişoğlu - 150210307

## Project Overview

PortfolioVantage is a financial system that combines portfolio management with news tracking and user interactions. The system enables users to:
- Manage investment portfolios
- Track various assets
- Monitor price history
- Interact with financial news
- Analyze portfolio performance

## Technical Stack

### Backend
- Python 3.8+
- Django 5.0
- PostgreSQL 12+
- Django REST Framework
- JWT Authentication
- Swagger/OpenAPI Documentation

### Key Dependencies
- Django==5.0
- psycopg2-binary==2.9.9
- django-cors-headers==4.3.1
- PyJWT==2.8.0
- python-dotenv==1.0.0
- djangorestframework==3.15.2
- drf-yasg==1.21.8

## Installation and Setup

1. **Clone the Repository**
   ```bash
   git clone <repository-url>
   cd portfoliovantage
   ```

2. **Set Up Virtual Environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Database Setup**
   ```bash
   # Create PostgreSQL database
   createdb portfoliovantage
   
   # Initialize database schema
   psql -d portfoliovantage -f database_setup.sql
   
   # Run Django migrations
   python manage.py migrate
   ```

5. **Load Sample Data (Optional)**
   ```bash
   python populate_dummy_data.py
   ```

6. **Start Development Server**
   ```bash
   python manage.py runserver
   ```

## Database Structure

The system implements a complex database schema with the following key components:

### Core Tables
- Users
- Portfolios
- Assets
- PriceHistory
- News
- NewsInteractions
- PortfolioAssets
- NewsAssetTags

### Key Features
- Proper normalization
- Efficient indexing
- Complex relationships
- Raw SQL queries (as per course requirements)

## API Documentation

### Authentication Endpoints

#### Register
```http
POST /api/auth/register/
Content-Type: application/json

{
    "username": "string",
    "password": "string",
    "email": "string"
}
```

#### Login
```http
POST /api/auth/login/
Content-Type: application/json

{
    "username": "string",
    "password": "string"
}
```

### Portfolio Management

#### Create Portfolio
```http
POST /api/portfolios/create/
Authorization: Bearer <token>
Content-Type: application/json

{
    "portfolio_name": "string"
}
```

#### Get Portfolio Details
```http
GET /api/portfolios/{portfolio_id}/
Authorization: Bearer <token>
```

#### Add Asset to Portfolio
```http
POST /api/portfolios/{portfolio_id}/assets/add/
Authorization: Bearer <token>
Content-Type: application/json

{
    "ticker": "string",
    "quantity": number,
    "purchase_price": number
}
```

### News Integration

#### Get Portfolio-Related News
```http
GET /api/portfolios/{portfolio_id}/news/
Authorization: Bearer <token>
```

#### Add News Interaction
```http
POST /api/news/{news_id}/interact/
Authorization: Bearer <token>
Content-Type: application/json

{
    "sentiment": "string",
    "comment": "string"
}
```

## Security Implementation

- JWT-based authentication
- Password hashing
- Role-based access control
- Secure environment variables
- CORS protection
- Input validation

## Development Guidelines

1. **Code Style**
   - Follow PEP 8 guidelines
   - Use meaningful variable names
   - Document complex functions

2. **Database Queries**
   - Use raw SQL (course requirement)
   - Optimize for performance
   - Include proper indexing

3. **API Development**
   - RESTful principles
   - Proper status codes
   - Consistent error handling

## Testing

1. **Run Tests**
   ```bash
   python manage.py test
   ```

2. **API Testing Tools**
   - Postman
   - Swagger UI (available at `/api/docs/`)
   - test_api.py script

## Documentation

- API documentation available at `/api/docs/`
- Swagger JSON at `/api/docs.json`
- Swagger YAML at `/api/docs.yaml`
- PDF documentation can be generated using `export_swagger_to_pdf.py`

## Error Handling

The API uses standard HTTP status codes:
- 200: Success
- 400: Bad Request
- 401: Unauthorized
- 403: Forbidden
- 404: Not Found
- 500: Internal Server Error

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit changes
4. Push to the branch
5. Create a Pull Request

## License

This project is part of the ITU BLG317E Database Systems course and is subject to academic integrity policies. 
