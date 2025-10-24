# Student Incentive System (Flask REST API – MVC Refactor)

A Flask-based REST API implementing the Model-View-Controller (MVC) architecture to manage and incentivize student community service participation.  
This system refactors the original command-line application into a web-based service layer using RESTful endpoints, JWT authentication, and SQLAlchemy ORM for persistence.

---

## 🧩 Project Overview

The **Student Incentive System** enables staff to log community service hours for students, students to request confirmation of logged hours, and tracks milestones that award accolades for reaching service hour thresholds.  

This refactor transitions the CLI version into a structured **MVC Flask REST API**, maintaining existing business logic while adding REST views, modular controllers, and token-based authentication.

---

## 🎯 Objectives

- Apply the **Model-View-Controller (MVC)** architectural pattern to organize the application.  
- Expose the system’s functionality through **RESTful API endpoints** (no user interface).  
- Implement **JWT token-based authentication** for secure access control.  
- Create **unit and integration tests** using `pytest` and `unittest`.  
- Document test plans and workflows for grading and user acceptance.

---

## ⚙️ System Architecture

### **1. Models (Data Layer)**
Implements database entities using **SQLAlchemy ORM**:

- `User` – Base user model with authentication and JSON serialization methods.  
- `Student` – Inherits from `User`, tracks community service hours and accolades.  
- `Staff` – Inherits from `User`, can log, confirm, and reject hours.  
- `ActivityLog` – Records community service activities with confirmation statuses.  
- `Accolade` – Represents milestones based on total confirmed hours.  
- `LeaderBoardEntry` – Tracks ranked student performance.

### **2. Controllers (Business Logic Layer)**
Encapsulates all reusable logic previously contained in CLI commands.  
Responsible for CRUD operations, validation, and workflow management.  

Examples:
- `staff_log_hours(staff_username, student_username, hours, activity)`
- `request_confirmation(student_username, activity_log_id)`
- `view_leaderboard()`
- `view_accolades(student_username)`
- `staff_confirm_hours(staff_username, activity_log_id)`
- `staff_reject_hours(staff_username, activity_log_id)`
- `update_leaderboard()`

### **3. Views (REST API Layer)**
Implements **Flask routes** to expose controller functions as REST endpoints.  
All endpoints follow `/api/...` format and require JWT authentication where applicable.

---

## 🔐 Authentication

Implemented using **Flask-JWT-Extended**.

### Workflow:
1. User logs in using `/api/login` with valid credentials.  
2. The server responds with an **access token (JWT)**.  
3. The token must be included in the `Authorization` header for all subsequent requests.  

**Header Example:**
```

Authorization: Bearer <access_token>

````

---

## 🧱 REST API Endpoints & Examples

### 1️⃣ Register a User (Staff)
**POST** `/api/staff`

**Request:**
```json
{
  "username": "sally",
  "password": "sallypass"
}
```

**Response:**

```json
{
  "message": "Staff sally successfully created with id ..."
}
```

### 1️⃣b Register a User (Student)
**POST** `/api/student`

**Request:**
```json
{
  "username": "student1",
  "password": "studentpass"
}
```

**Response:**

```json
{
  "message": "Student student1 successfully created with id ..."
}
```

---

### 2️⃣ Login and Retrieve JWT Token

**POST** `/api/login`

**Request:**

```json
{
  "username": "student1",
  "password": "mypassword"
}
```

**Response:**

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs..."
}
```

---

### 3️⃣ Staff Logs Hours for a Student

**POST** `/api/staff/log-hours`

**Headers:**

```
Authorization: Bearer <staff_token>
```

**Request:**

```json
{
  "student_username": "student1",
  "hours": 10,
  "activity": "Beach cleanup"
}
```

**Response:**

```json
{
  "message": "Staff staff1 logged 10 hours for student1",
  "log_id": "f2b8a67d-239a-42f8-a312-51d3af21377f",
  "status": "logged"
}
```

---

### 4️⃣ Student Requests Confirmation of Hours

**POST** `/api/student/request-confirmation`

**Headers:**

```
Authorization: Bearer <student_token>
```

**Request:**

```json
{
  "activity_log_id": "f2b8a67d-239a-42f8-a312-51d3af21377f"
}
```

**Response:**

```json
{
  "message": "Confirmation requested successfully.",
  "status": "pending"
}
```

---

### 5️⃣ Staff Confirms Student Hours

**PUT** `/api/staff/confirm-hours/<log_id>`

**Headers:**

```
Authorization: Bearer <staff_token>
```

**Response:**

```json
{
  "message": "Activity log f2b8a67d-239a-42f8-a312-51d3af21377f confirmed.",
  "status": "confirmed"
}
```

---

### 6️⃣ Staff Rejects Student Hours

**PUT** `/api/staff/reject-hours/<log_id>`

**Headers:**

```
Authorization: Bearer <staff_token>
```

**Response:**

```json
{
  "message": "Activity log f2b8a67d-239a-42f8-a312-51d3af21377f rejected.",
  "status": "rejected"
}
```

---

### 7️⃣ View Leaderboard

**GET** `/api/leaderboard`

**Headers:**

```
Authorization: Bearer <staff_token or student_token>
```

**Response:**

```json
{
  "leaderboard": [
    {"rank": 1, "student": "student1", "confirmed_hours": 50},
    {"rank": 2, "student": "student2", "confirmed_hours": 25}
  ]
}
```

---

### 8️⃣ View Student Accolades

**GET** `/api/student/accolades/<username>`

**Headers:**

```
Authorization: Bearer <student_token>
```

**Response:**

```json
{
  "student": "student1",
  "total_hours": 50,
  "accolades": ["10 Hour Milestone", "25 Hour Milestone", "50 Hour Milestone"]
}
```

---

## 🧰 Installation & Setup

1. **Clone Repository**

   ```bash
   git clone https://github.com/SoftwareEngineeringAssignmentTwo/SoftwareEngineeringTwoAssignmentTwo.git
   ```

2. **Install Dependencies**

   ```bash
   pip install -r requirements.txt
   ```

3. **Initialize Database**

   ```bash
   flask init
   ```

4. **Run Server**

   ```bash
   flask run
   ```

   API will be available at: `http://127.0.0.1:8080/`

---

## 🧪 Testing Implementation

Testing is implemented using both `pytest` and Python's built-in `unittest` framework.

### **Unit Tests**

Located in `App/tests/`:

**Modules Tested in Isolation:**
* User model creation and validation
* Password hashing and verification
* JSON serialization methods
* Staff hour logging controller
* Student confirmation request controller
* Accolade creation logic
* Leaderboard calculation

### **Integration Tests**

**End-to-End Workflows Tested:**
* Complete student-staff confirmation workflow
* Accolade awarding at 10, 25, 50 hour milestones
* Leaderboard ranking and updates
* JWT-based authentication and authorization
* Hour rejection and status transitions
* Multi-user interaction scenarios

### **API Tests (Postman/Newman)**

**Automated Collection Tests:**
* User registration endpoints
* Login and token generation
* Protected route authorization
* Hour logging API
* Confirmation workflow API
* Leaderboard retrieval
* Accolade viewing
* Edge cases and error handling

**Run Unit & Integration Tests:**

```bash
pytest -v
```

**Run API Tests:**

```bash
newman run "e2e/Student Incentive System API Tests.postman_collection.json" -e "e2e/config.json" --insecure --color on
```

**Example Unit Test:**

```python
def test_staff_log_hours(self):
    log = Staff.logHoursForStudent("staffID", 5, "Community Service")
    self.assertEqual(log.status, "logged")
```

---

## 📋 Example Integration Test

```python
def test_student_workflow(self):
    student = create_user("alice", "alicepass", user_type="student")
    staff = create_user("admin", "adminpass", user_type="staff")
    log = Staff.logHoursForStudent(student.studentID, 5, "Volunteering")
    log.status = "pending"
    db.session.commit()
    Staff.confirmHours(self, log.logID)
    updated_log = ActivityLog.query.filter_by(logID=log.logID).first()
    self.assertEqual(updated_log.status, "confirmed")
```

---

## 🧩 Postman API Testing

A **Postman collection** is provided:
`Student Incentive System API Tests.postman_collection.json`

To use:

1. Import into Postman.
2. Obtain a token via `/api/login`.
3. Add this header to requests:

   ```
   Authorization: Bearer {{token}}
   ```

Requests are grouped under **Student** and **Staff** folders for clarity.

---

## 🧠 Assignment Requirements Mapping

| Requirement            | Implementation                         |
| ---------------------- | -------------------------------------- |
| Refactor to MVC        | Models, Controllers, Views implemented |
| REST API with Auth     | JWT authentication added               |
| Test Planning          | Unit & Integration tests created       |
| Test Implementation    | Implemented with `pytest` + `unittest` |
| Postman Collection     | Included for API verification          |
| Low-Fidelity Wireframe | Provided separately (see report)       |

---

## 🧩 Status Tracking

Activity logs transition through the following states:

* **logged** – hours recorded by staff
* **pending** – student requests confirmation
* **confirmed** – verified and approved by staff
* **rejected** – denied by staff

Only **confirmed** hours count toward:

* Accolades
* Leaderboard rankings

---

## 🧾 Technical Stack

* **Language:** Python 3.9 or 3.10
* **Framework:** Flask
* **Database:** SQLite (SQLAlchemy ORM)
* **Authentication:** Flask-JWT-Extended
* **Testing:** Pytest + Unittest
* **API Tooling:** Postman

---

## 🧍 Contributors

| Name           |
|----------------|
| Nie-l Constance |
| Allin Ramjit   |
| Rana Salim     |
| Satyam Mahadeo |
---

## 🙏 Acknowledgements

Developed for **COMP 3613 – Software Engineering II**
**Lecturer:** Mr. Nicholas Mendez
Certain implementations were adapted from in-class examples for educational purposes.

---