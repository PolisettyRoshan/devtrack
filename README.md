# DevTrack - Django Backend Assignment

DevTrack is a simple GitHub Issues-like backend built with Django.

## Features

- OOP entities using `BaseEntity`
- `Reporter` and `Issue` classes
- `CriticalIssue` and `LowPriorityIssue` subclasses
- JSON file storage
- REST-style Django endpoints
- Validation and error responses
- Issue filtering by status

## 1. Install dependencies

Open a terminal in this project folder:

```bash
pip install -r requirements.txt
```

## 2. Check the project

```bash
python manage.py check
```

## 3. Start the server

```bash
python manage.py runserver
```

The API will be available at:

`http://127.0.0.1:8000/`

## Endpoints

### Create Reporter

POST `/api/reporters/`

Example:

```json
{
    "id": 1,
    "name": "Rahul Kumar",
    "email": "rahul@example.com",
    "team": "backend"
}
```

### Get All Reporters

GET `/api/reporters/`

### Get Reporter by ID

GET `/api/reporters/?id=1`

### Create Issue

POST `/api/issues/`

Example:

```json
{
    "id": 1,
    "title": "Login button not working on mobile",
    "description": "Users on iOS 17 cannot tap the login button",
    "status": "open",
    "priority": "critical",
    "reporter_id": 1
}
```

### Get All Issues

GET `/api/issues/`

### Get Issue by ID

GET `/api/issues/?id=1`

### Filter Issues by Status

GET `/api/issues/?status=open`

## Validation

Allowed statuses:

- open
- in_progress
- resolved
- closed

Allowed priorities:

- low
- medium
- high
- critical

Example validation failure:

```json
{
    "error": "Title cannot be empty"
}
```

## Storage

Application data is stored in:

- `reporters.json`
- `issues.json`

No Django database is used for application data.

## OOP Design Decision

`BaseEntity` defines the common interface for entities. `CriticalIssue` and
`LowPriorityIssue` inherit from `Issue` and override `describe()` so that
different priorities can produce different messages while using the same API.
