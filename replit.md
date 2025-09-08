# Overview

This is a Flask MVC (Model-View-Controller) web application template built with Python. The application provides a structured foundation for building web applications with user management, authentication, and administrative capabilities. It follows the MVC architectural pattern to separate concerns between data models, business logic controllers, and presentation views. The template includes JWT-based authentication, database integration with SQLAlchemy, and both server-side rendered pages and client-side API endpoints.

# User Preferences

Preferred communication style: Simple, everyday language.

# System Architecture

## Backend Architecture
The application follows a modular Flask MVC structure:

- **Models**: SQLAlchemy ORM models define data structures, with a base `User` model and extended `Student` model using table inheritance. Users have UUID primary keys and secure password hashing.
- **Controllers**: Business logic is separated into controller modules for user management, authentication, and database initialization. Controllers handle data processing and database operations.
- **Views**: Flask blueprints organize routes into logical groups (user, auth, index, admin). Views handle HTTP requests/responses and template rendering.
- **Templates**: Jinja2 templates provide server-side rendering with a base layout and component-specific templates.

## Authentication & Authorization
JWT (JSON Web Tokens) authentication system using Flask-JWT-Extended:
- Cookie and header-based token storage
- User identity resolution with database lookups
- Context processors inject authentication state into all templates
- Protected routes require JWT verification
- Admin interface with role-based access control

## Database Layer
SQLAlchemy with Flask-Migrate for database management:
- Development uses SQLite by default
- Production-ready PostgreSQL support via psycopg2
- Database migrations and schema versioning
- UUID-based primary keys for better scalability

## Configuration Management
Environment-based configuration system:
- Default development config with SQLite
- Environment variable override support
- Custom config file option for deployment-specific settings
- Secure handling of secrets and API keys

## Static Asset Management
Flask-Uploads handles file uploads and static assets:
- Support for documents, images, and text files
- Configurable upload destinations
- Static file serving for client-side applications

## Testing Infrastructure
Comprehensive testing setup:
- Unit tests for models and pure functions
- Integration tests for database operations
- End-to-end browser testing with Puppeteer
- Pytest and Mocha test runners

## Deployment Architecture
Production deployment configuration:
- Gunicorn WSGI server with gevent workers
- Multi-process scaling (4 workers by default)
- Containerized deployment support via DevContainer
- Environment-specific logging and monitoring

# External Dependencies

## Core Framework
- **Flask**: Web application framework with extensions for SQLAlchemy, CORS, JWT, and Admin
- **SQLAlchemy**: Object-relational mapping and database abstraction
- **Flask-Migrate**: Database schema migration management

## Authentication & Security
- **Flask-JWT-Extended**: JWT token management and authentication
- **Werkzeug**: Password hashing and security utilities
- **Flask-CORS**: Cross-origin resource sharing support

## Database
- **SQLite**: Default development database
- **psycopg2-binary**: PostgreSQL adapter for production deployments

## Development & Testing
- **pytest**: Python testing framework
- **Mocha**: JavaScript testing framework for e2e tests
- **Puppeteer**: Browser automation for end-to-end testing
- **Chai**: JavaScript assertion library

## Production Deployment
- **Gunicorn**: WSGI HTTP server for production
- **gevent**: Asynchronous networking library for worker processes

## File Management
- **Flask-Uploads**: File upload handling and management
- **python-dotenv**: Environment variable management

## UI Framework
- **Materialize CSS**: Frontend CSS framework for responsive design
- **Google Fonts**: Icon fonts and typography