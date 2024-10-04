# 🎙️ Conversational Pathways API

**Conversational Pathways API**: This is a Django RESTful API designed to manage conversational agents and pathways, integrating seamlessly with Bland AI. This project allows you to create, update, and manage conversational agents and their pathways, providing a robust backend for conversational applications.

---

## 📖 Table of Contents

- [Features](#-features)
- [Getting Started](#-getting-started)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
  - [Environment Setup](#environment-setup)
- [Usage](#-usage)
  - [Running the Server](#running-the-server)
  - [API Endpoints](#api-endpoints)
- [Testing](#-testing)
  - [Running Tests](#running-tests)
- [Deployment](#-deployment)
  - [Infrastructure as Code with Terraform](#infrastructure-as-code-with-terraform)
- [Documentation](#-documentation)
- [Contributing](#-contributing)
- [License](#-license)
- [Contact](#-contact)

---

## ✨ Features

- **Agent Management**: Create, update, delete, and retrieve conversational agents.
- **Pathway Management**: Manage conversational pathways with nodes and edges.
- **Integration with Bland AI**: Seamless integration with Bland AI for agent deployment.
- **API Documentation**: Interactive API documentation with Swagger UI and ReDoc.
- **Robust Testing Suite**: Unit tests, integration tests, end-to-end tests, and concurrency tests.
- **Continuous Integration**: Automated testing and code quality checks with GitHub Actions.
- **Infrastructure as Code**: Deployable infrastructure using Terraform.
- **Extensible and Modular**: Designed for scalability and easy integration with other services.

---

## 🚀 Getting Started

### Prerequisites

Before you begin, ensure you have met the following requirements:

- **Python 3.8+**: The project is built using Python 3.8 or higher.
- **PostgreSQL**: A Supbase PostgreSQL database instance for development (https://supabase.com).
- **Git**: Version control system to clone the repository.
- **Virtual Environment**: Recommended to use `venv` or `virtualenv`.

### Installation

1. **Clone the Repository**

   ```bash
   git clone https://github.com/Fato07/Django-REST-API-for-Conversational-Pathways.git
   cd conversational_api
   ```

2. **Create a Virtual Environment**

   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install Dependencies**

   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

### Environment Setup

Create a `.env` file in the root directory and add the following environment variables:

```env
SECRET_KEY=<your-value>
BLAND_AI_API_KEY=<your-value>
BLAND_AI_BASE_URL=https://api.bland.ai/v1
DATABASE_URL=<your-value: in my case, i used supabase>
```

---

## 📝 Usage

### Running the Server

Apply migrations and start the development server:

```bash
python manage.py migrate
python manage.py runserver
```

The API will be available at `http://127.0.0.1:8000/`.

### API Endpoints

The main endpoints are:
Full documenation for the API endpoints available and can be tested with postman [here](https://documenter.getpostman.com/view/10389328/2sAXxLDaYV):

- **Agents**
  - `GET /api/v1/agents/` : List all agents.
  - `POST /api/v1/agents/` : Create a new agent.
  - `GET /api/v1/agents/{id}/` : Retrieve a specific agent.
  - `PUT /api/v1/agents/{id}/` : Update an agent.
  - `DELETE /api/v1/agents/{id}/` : Delete an agent.

- **Conversational Pathways**
  - `GET /api/v1/pathways/` : List all pathways.
  - `POST /api/v1/pathways/` : Create a new pathway.
  - `GET /api/v1/pathways/{id}/` : Retrieve a specific pathway.
  - `PUT /api/v1/pathways/{id}/` : Update a pathway.
  - `DELETE /api/v1/pathways/{id}/` : Delete a pathway.

---

## 🧪 Testing

This project includes a comprehensive test suite.

### Running Tests

1. **Unit and Integration Tests**

   ```bash
   pytest
   ```

2. **End-to-End Tests**

   ```bash
   pytest agents/tests/test_end_to_end.py
   ```

3. **Concurrency Tests**

 to DO

---

## ☁️ Deployment

### Infrastructure as Code with Terraform

To DO

---

## 📚 Documentation

---

# 🎉