# AI-Based Facial Recognition Authentication System

## Overview

The AI-Based Facial Recognition Authentication System is a desktop application developed using Python, Tkinter, OpenCV, SQLite, and the `face_recognition` library.

The system provides secure user authentication by combining:

* Username verification
* Password authentication
* Facial Recognition (128-dimensional face encoding)
* Audit logging of all authentication attempts

The application features a modern graphical user interface (GUI) with separate Administrator and User access modes.

---

# Project Structure

```text
FaceAuthSystem/
│
├── main.py                 # Application entry point
├── gui_app.py              # Complete GUI application
├── face_utils.py           # Face detection, encoding and matching
├── database.py             # SQLite database operations
├── log_utils.py            # Authentication logging utilities
│
├── dataset/                # Stored user face images
│   ├── user1.jpg
│   ├── user2.jpg
│   └── ...
│
├── users.db                # SQLite database (auto-generated)
├── README.md
├── requirements.txt
│
└── __pycache__/
```

---

# Technologies Used

* Python 3.11
* Tkinter
* OpenCV
* face_recognition
* dlib
* NumPy
* SQLite
* Pillow (PIL)

---

# Installation

## 1. Clone or Download Project

Place the project folder anywhere on your system.

```bash
cd FaceAuthSystem
```

---

## 2. Create Virtual Environment

### Windows

```bash
python -m venv venv
venv\Scripts\activate
```

### Linux / macOS

```bash
python3 -m venv venv
source venv/bin/activate
```

---

## 3. Install Dependencies

```bash
pip install -r requirements.txt
```

Current requirements:

```text
opencv-python==4.10.0.84
face_recognition==1.3.0
numpy==1.26.4
dlib==19.24.6
Pillow==10.4.0
```

---

# Running the Application

Launch the application:

```bash
python main.py
```

The system will open the graphical interface.

---

# Application Workflow

## Landing Page

When the application starts, users are presented with two options:

### Administrator

Administrators can:

* Register new users
* Login using facial recognition
* Access dashboard
* View authentication logs
* View registered user images

### User

Regular users can:

* Login using username, password and face verification
* View their profile image
* View their login history
* Logout securely

---

# Registration Process

Administrator registers a new user.

### Step 1

Capture user's face through webcam.

### Step 2

Enter:

* Username
* Password
* Confirm Password

### Step 3

System:

* Detects exactly one face
* Extracts facial features
* Generates a 128-dimensional facial encoding
* Stores data inside SQLite database
* Saves user image inside `dataset/`

---

# Login Process

The login procedure requires:

1. Username
2. Password
3. Live facial verification

The system:

* Captures a webcam frame
* Extracts a face encoding
* Compares it with the stored encoding
* Verifies password
* Grants access only if both checks pass

Authentication threshold:

```python
FACE_MATCH_THRESHOLD = 0.45
```

Located in:

```text
face_utils.py
```

---

# Face Recognition Module

Implemented in:

```text
face_utils.py
```

Functions include:

### Face Detection

```python
detect_faces_haar()
```

Uses:

```text
OpenCV Haar Cascade
```

### Face Encoding

```python
get_face_encoding()
```

Uses:

```text
face_recognition library
dlib ResNet model
128-D feature vector
```

### Face Comparison

```python
compare_faces()
```

Uses Euclidean distance to determine similarity.

---

# Dashboard Features

After successful administrator login:

### Dashboard Overview

Displays:

* Total login attempts
* Granted authentications
* Denied authentications

### Registered Face Image

Displays:

* Stored user image

### Access Logs

Displays:

* Timestamp
* Username
* Status
* Face distance
* Reason

---

# Logging System

Authentication attempts are automatically recorded.

Each log entry contains:

| Field     | Description           |
| --------- | --------------------- |
| Timestamp | Login time            |
| Username  | User account          |
| Status    | GRANTED / DENIED      |
| Distance  | Face similarity score |
| Reason    | Authentication result |

Example:

```text
2026-06-15 14:25:18
john
GRANTED
0.3271
Face and password matched
```

---

# Database Design

SQLite database:

```text
users.db
```

Stores:

```text
User ID
Username
Password
Face Encoding
Image Path
```

---

# Security Features

Implemented:
✔ Face Recognition Authentication
✔ Password Verification
✔ Audit Logging
✔ User Image Storage
✔ Administrator/User Separation

---

# Current Limitations

The current implementation:

* Stores passwords in plaintext
* Does not include liveness detection
* Can be vulnerable to photo spoofing attacks
* Uses a fixed similarity threshold

---

# Future Enhancements

Possible improvements:

* Password hashing using bcrypt
* FaceNet embeddings (512-dimensional vectors)
* Anti-spoofing / liveness detection
* Multi-user recognition
* Email notifications
* Role-based access control
* Cloud database integration
* Real-time security monitoring

---

# Academic Relevance

This project demonstrates:

* Artificial Intelligence
* Computer Vision
* Facial Recognition
* Biometric Authentication
* Human-Computer Interaction
* Secure Access Control Systems

---

# Author

AI-Based Facial Recognition Authentication System

Built using Python, OpenCV, SQLite, and Facial Recognition Technology.
