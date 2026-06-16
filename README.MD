# Kanmind Backend 🧠🚀

The robust, secure backend for Kanmind – a collaborative Kanban board system. Built with Python 3.14, Django, and the Django REST Framework (DRF). 

The API features a granular role and permission management system for boards, tasks, and an integrated comment feed, all secured globally via Token Authentication.

## 🛠️ Features & Tech Stack

* **Framework:** Django 5.x & Django REST Framework (DRF)
* **Authentication:** Token-based Authentication (`rest_framework.authtoken`)
* **Security:** Secure by Default (Global `IsAuthenticated` restriction, explicit public exceptions)
* **Database:** SQLite (Development) / Ready for PostgreSQL (Production)
* **Permission System:** Custom, granular permissions (e.g., Board Member Validation, Task Field Locks, Comment Author Protection)
* **Automated Sorting:** Chronological comment feeds handled efficiently directly at the database level.

---

## Local Development Setup

Follow these steps to get the development server running locally:

### 1. Clone the repository & enter the directory
```bash
git clone https://github.com/KKrntzk/kanmind_project.git

cd kanmind_project
```

### 2. Create the virtual environment
To avoid environment pollution and issues with specific Python versions, create the environment without pre-installed packages first:

Windows(Powershell)
```bash
python -m venv .venv
```

### 3. Activate the virtual environment

```bash
.venv\Scripts\Activate.ps1
```

💡 Note for Windows users: If you get a script execution policy error, run Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process in your terminal first, then try activating again.

### 4. Set up package manager & install dependencies

To ensure the packages are installed correctly inside the virtual environment, use the python module path:

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 5. Configure environment variables

The project requires a .env file for local configurations and secrets. Copy the provided template and fill in your local values:

```bash
cp .env.template .env
```
Open the newly created .env file and make sure a SECRET_KEY is set (e.g., SECRET_KEY=your-local-dev-key).

### 6. Run database migrations

```bash
python manage.py migrate
```

### 7. Start the development server

```bash
python manage.py runserver
```
The server will be available locally at: http://127.0.0.1:8000/


---

## 🔌 API Endpoints (Documentation)

All endpoints (except Registration and Login) require the following header:  
`Authorization: Token <your_token>`

### 👤 Authentication
* `POST /api/auth/register/` – Registers a new user.
* `POST /api/auth/login/` – Returns an auth token upon valid credentials.

### 📋 Boards
* `GET /api/boards/` – Lists all boards where the user is either the owner or a member.
* `POST /api/boards/` – Creates a new board (current user automatically becomes the owner).
* `GET/PUT/DELETE /api/boards/<int:id>/` – Retrieve, update, or delete a board (Update/Delete restricted to the Owner).

###  Tasks
* `GET /api/tasks/assigned/` – Lists all tasks assigned to the current user.
* `GET /api/tasks/reviewing/` – Lists all tasks where the user is set as the reviewer.
* `POST /api/tasks/` – Creates a new task for a specific board (User must be a board member/owner).
* `GET/PUT/DELETE /api/tasks/<int:id>/` – Retrieve, update, or delete a specific task.

### 💬 Comment System
* `GET /api/tasks/<int:task_id>/comments/` – Fetches all comments for a task (chronologically sorted). *Permission: Board Members & Owner*.
* `POST /api/tasks/<int:task_id>/comments/` – Adds a new comment. The author is automatically extracted from the token. *Permission: Board Members & Owner*.
* `DELETE /api/tasks/<int:task_id>/comments/<int:comment_id>/` – Deletes a specific comment. *Permission: Strictly Comment Author Only*.

---

## 🔒 Permissions & Validation Matrix (Examples)

| Endpoint | Action | Allowed For | Expected Status Codes |
| :--- | :--- | :--- | :--- |
| `/api/tasks/<id>/comments/` | `POST` | Board Member / Owner | `201` (Created), `400` (Bad Request), `403` (Not a Member), `404` (Task Not Found) |
| `/api/tasks/<id>/comments/<id>/` | `DELETE` | **Strictly** the Comment Author | `204` (No Content), `403` (Forbidden/Not Author), `404` (Not Found) |

---

## 📂 Project Structure (Core Apps)
* `auth_app/` – Manages user onboarding, custom registration validation, and login token generation.
* `board_app/` – Handles board creation, invitations, and team memberships.
* `task_app/` – Core logic for tasks, assignments, status states, and the comment system.
* `kanmind_project/` – Core configuration directory (settings, root URLs).