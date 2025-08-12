
# Service Ease API

**Service Ease** is a Django REST framework-based backend API for a household service providing platform. It manages users, profiles, services, categories, carts, orders, and reviews with role-based permissions.

---

## Table of Contents

* [Features](#features)
* [Tech Stack](#tech-stack)
* [Installation](#installation)
* [Configuration](#configuration)
* [Running the Server](#running-the-server)
* [API Documentation](#api-documentation)
* [Usage](#usage)
* [Permissions](#permissions)
* [Project Structure](#project-structure)
* [Future Improvements](#future-improvements)
* [License](#license)
* [Contact](#contact)

---

## Features

* User registration, authentication (JWT) & profile management.
* Role-based access control (Admin and Client).
* CRUD operations for Services and Categories.
* Shopping cart system linked to users.
* Order management and status tracking.
* Service reviews with rating system.
* Search, filtering, and ordering for services.
* Swagger and Redoc API documentation.
* Debug toolbar integration for development.

---

## Tech Stack

* Python 3.x
* Django 4.x
* Django REST Framework
* DRF-YASG (Swagger / OpenAPI docs)
* Djoser (Authentication)
* PostgreSQL (recommended)
* Redis (optional, for caching and async tasks)

---

## Installation

1. **Clone the repository**

```bash
git clone https://github.com/tanbinali/ServiceEaseProject.git
cd service-ease
```

2. **Create and activate a virtual environment**

```bash
python -m venv venv
source venv/bin/activate   # Linux/macOS
venv\Scripts\activate      # Windows
```

3. **Install dependencies**

```bash
pip install -r requirements.txt
```

4. **Set up environment variables**

Create a `.env` file (or configure environment variables) including:

```env
SECRET_KEY=your_django_secret_key
DEBUG=True
DATABASE_URL=postgres://user:password@localhost:5432/serviceease
DJOSER_SECRET=your_secret_for_djoser
```

---

## Configuration

* Configure your database connection in `settings.py` or via `DATABASE_URL`.
* Configure media storage and static files.
* Setup JWT authentication with Djoser defaults or customize as needed.

---

## Running the Server

```bash
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

---

## API Documentation

Interactive API docs are available at:

* Swagger UI: `/swagger/`
* ReDoc UI: `/redoc/`
* Raw JSON/YAML schema: `/swagger.json` or `/swagger.yaml`

---

## Usage

* Register and login users via `/auth/` endpoints (powered by Djoser).
* Admin users can create and manage services, categories, orders, and users.
* Clients can browse services, manage carts, place orders, and write reviews.
* Use nested endpoints to manage related data (e.g., services under categories, reviews under services).

---

## Permissions

* **Admin:** Full access to all endpoints.
* **Client:** Restricted access, primarily to their own data and public information.
* **Anonymous:** Read-only access to categories, services, and public reviews.

---

## Project Structure

* `accounts/` - User and profile management.
* `services/` - Categories and services.
* `orders/` - Cart, orders, and order items.
* `reviews/` - Service reviews.
* `common/` - Shared utilities, permissions, and helpers.

---

## Future Improvements

* Email and SMS notifications.
* Payment gateway integration.
* Advanced search and filtering capabilities.
* Analytics dashboard for admins.
* Service provider role with distinct permissions.
* Soft delete implementation.
* Frontend SPA integration.

---

## License

This project is licensed under the **BSD License** — see the [LICENSE](LICENSE) file for details.

---

## Contact

For questions or support, please reach out:

* Email: [tanbinali@gmail.com](mailto:tanbinali@gmail.com)
* GitHub: [tanbinali](https://github.com/tanbinali)

