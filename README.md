# IDSC Clinic System
1. HTTP Methods
HTTP Method	Use	Example
GET	Retrieve/read data	Get student ID, name, contact number, gender, address, age
POST	Create/add new data	Add a new health record or register a new student
PUT	Update an existing record	Update a student's medical/health record
DELETE	Delete/remove a specific record	Delete a specific employee record
Common HTTP Method Flow
GET → Read/Retrieve
POST → Create
PUT → Update
DELETE → Delete
Possible Landing Pages / Modules
Student Portal
Registrar
Clinic
Inventory
Faculty
Library

2. System Integration
System

Clinic Web Frontend

HTTP Methods
GET
POST
PUT
DELETE
Request Payload

JSON (JavaScript Object Notation)

API Request
The frontend sends an HTTP request to the backend API.

3. Backend / API Flow
Frontend → API → Backend → Database

The general process is:
Clinic Web Frontend
        ↓
    HTTP Request
        ↓
      REST API
        ↓
     Backend
        ↓
     Database
        ↓
    HTTP Response
        ↓
Clinic Web Frontend

4. Students
Entity: Students

 Field             Data Type       Description             

 `student_id`      INT             Unique student ID       
 `first_name`      VARCHAR/STRING  Student's first name    
 `last_name`       VARCHAR/STRING  Student's last name     
 `birth_date`      DATE            Student's date of birth 
 `sex`             VARCHAR/STRING  Student's sex           
 `course_section`  VARCHAR/STRING  Course and section      
 `contact_no`      VARCHAR/STRING   Contact number          

API Endpoints
GET    /api/students
GET    /api/students/{studentId}
POST   /api/students
PUT    /api/students/{studentId}
DELETE /api/students/{studentId}

5. Health Record
 Field              Data Type     Description                 

 `health_id`        INT            Unique health record ID     
 `student_id`       INT            ID of the student           
 `allergies`        VARCHAR/TEXT   Student's allergies         
 `blood_type`       VARCHAR        Blood type                  
 `medical_history`  TEXT           Previous medical conditions 
 `medications`      TEXT/VARCHAR   Current medications         
 `height`            DECIMAL        Student's height            
 `weight`            DECIMAL       Student's weight         

API Endpoints
GET    /api/health
GET    /api/health/{studentId}
POST   /api/health
PUT    /api/health/{healthId}
DELETE /api/health/{healthId}

6. Employees
 Field          Data Type       Description               

 `employee_id`  INT             Unique employee ID        
 `first_name`   VARCHAR/STRING  Employee's first name     
 `last_name`    VARCHAR/STRING  Employee's last name      
 `position`     VARCHAR/STRING  Employee's position       
 `contact_no`   VARCHAR/STRING  Employee's contact number 

 API Endpoints
GET    /api/employees
GET    /api/employees/{employeeId}
POST   /api/employees
PUT    /api/employees/{employeeId}
DELETE /api/employees/{employeeId}

7. REST API CRUD 
    CRUD          HTTP Method      Purpose              

 C — Create     POST            Add new data         
 R — Read       GET            Retrieve data        
 U — Update     PUT           Modify existing data 
 D — Delete    DELETE           Remove data       

8. Backend Explanation
If the program receives an unexpected or invalid request, the backend should validate the request and return an appropriate response instead of processing an empty or invalid value. For example, if an academic department sends an inquiry, the backend should properly receive, validate, and process the request.
For example:
For this clinic page, the backend flow is important because the landing page receives new visitor information and sends these records to the backend database. The backend then processes and stores the information.

9. System Structure
 




