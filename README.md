# ProjectFlow
A comprehensive Project Management App built with Django that allows users to create, organize, and track their tasks with enhanced collaboration features. The application features user authentication, task management, project organization, and real-time notifications.
## 🔧 Features
### Core Functionality
- User Authentication: Secure register, login, logout, and profile management
- Task Management: Full CRUD operations for tasks with due dates and priorities
- Task Status Tracking: To Do (TD), In Progress (IP), Done (DN)
- Project Organization: Group tasks into projects with team collaboration
- Team Assignment: Assign tasks to team members and track progress
- Real-time Notifications: Task assignment alerts, Status change updates, Deadline reminders, New comments and mentions
### Technical Features
- Django ORM: Efficient database operations
- Bootstrap 5: Responsive, modern interface
- JWT Authentication: Secure API endpoints
- Signal Handlers: For real-time notifications
- AJAX Integration: Smooth UI interactions
- Comprehensive Error Handling: User-friendly feedback
## 🛠 Setup Instructions
1. Clone the repository
```bash
git clone https://github.com/Makihataima-Ken/ProjectFlow.git
```
2. Create and activate a virtual environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```
3. Install dependencies
```bash
pip install -r requirements.txt
```
4. Migrate database
```bash
python manage.py migrate
```
5. Run the server
```bash
python manage.py runserver
```
## URL Structure
### Authentication URLs
- ```/login/``` - User login
- ```/logout/``` - User logout
- ```/register/``` - New user registration
- ```/profile/``` - User profile
### Task URLs
- ```tasks/```- List User's Tasks
- ```'tasks/<int:pk>/```- Task detail view
- ```tasks/create/```- Create new task
- ```tasks/update/<int:pk>/```- Update task
- ```'tasks/delete/<int:pk>/```- Delete task
- ```tasks/<int:pk>/follow/```- Follow/Unfollow task
- ```'tasks/search/```- Search for tasks
### Project URLs
- ```projects/```- List User's projects
- ```'projects/<int:pk>/```- Task detail view
- ```projects/create/```- Create new task
- ```projects/update/<int:pk>/```- Update task
- ```'projects/delete/<int:pk>/```- Delete task
## Templates
- The application uses Django's template system with Bootstrap 5 for styling. Key templates:
### Task Templates
- task_list.html - Displays all tasks
- task_detail.html - Detailed task view
- task_form.html - Create/update form
- task_confirm_delete.html - Delete confirmation
### Project Templates
- project_list.html - Displays all projects
- project_detail.html - Detailed project view
- project_form.html - Create/update form
- project_confirm_delete.html - Delete confirmation
### Authentication Templates
- login.html - Login form
- register.html - Registration form
- profile.html - User profile
