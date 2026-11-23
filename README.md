# Leave Approval System - Testing & Automation Suite

A full-stack, lightweight web application for employee leave requests and manager approvals, accompanied by an academic and enterprise-grade software testing implementation covering **Manual Testing (STLC)**, **Selenium WebDriver UI Automation**, **Page Object Model (POM) Framework**, and **Postman & Python REST API Automation with Request Chaining**.

---

## 🌟 Key Highlights & Academic Objectives

1. **Software Testing Life Cycle (STLC) & Manual Testing**:
   - Detailed phases from Requirement Analysis to Test Closure.
   - Comprehensive Manual Test Case document with execution statuses and RTM.
   - Bug Life Cycle & Bug Reporting template.
2. **Selenium WebDriver in PyCharm & Python Automation**:
   - Element locators via `By` class (`ID`, `NAME`, `CSS_SELECTOR`, `XPATH`, `LINK_TEXT`, `PARTIAL_LINK_TEXT`, `TAG_NAME`, `CLASS_NAME`).
   - Web element interaction methods (`click`, `send_keys`, `clear`, `text`, `get_attribute`).
   - Dropdown handling with `Select` class.
   - JavaScript Alert handling (`alert.text`, `alert.accept()`).
   - In-depth Wait Types: **Implicit Wait**, **Explicit Wait**, and **Fluent Wait**.
3. **End-to-End Test Workflow**:
   - Employee demands leave -> Verified in Pending column.
   - Manager logs in -> Views pending request -> Approves leave -> Verified in Approved column.
   - Manager rejection scenario.
4. **Complete Automation Framework**:
   - Built on **Page Object Model (POM)** architecture (`automation_framework/`).
   - Clean separation of Page Objects, Driver Configuration, and Test Cases.
5. **REST API Architecture & Testing**:
   - REST vs SOAP vs Web Services architectural comparison.
   - Python automated API test suite (`test_api_leave_approval.py`) with 6 test scenarios.
   - **Request Chaining**: Create leave (`POST /api/leaves`) -> Extract ID -> Manager Approve (`PUT /api/leaves/{{id}}`) -> Verify status (`GET /api/leaves`).
6. **Advanced Postman Suite**:
   - Exported Collection (`leave_approval_api.postman_collection.json`) and Environment (`leave_approval_environment.postman_environment.json`).
   - Automated Chai assertions (`pm.test`, `pm.expect`).
   - Newman CLI execution support.

---

## 📁 Project Structure

```
leave-approval-system-main/
├── index.html                               # Web application UI
├── server.js                                # REST API Server (Node.js)
│
├── test_selenium_leave_approval.py          # Selenium WebDriver UI Test Suite
├── test_api_leave_approval.py               # Python REST API Test Suite with Request Chaining
├── run_all_tests.py                         # Master test runner (auto-boots server & executes all 12 tests)
│
├── automation_framework/                    # Complete Page Object Model (POM) Framework
│   ├── config/config.py                     # Configuration & driver factory
│   ├── pages/base_page.py                   # Base Page Object with explicit wait wrappers
│   ├── pages/login_page.py                  # Login Page Object
│   ├── pages/employee_page.py               # Employee Dashboard Page Object
│   ├── pages/manager_page.py                # Manager Dashboard Page Object
│   └── tests/test_leave_approval_pom.py     # End-to-End POM test case
│
├── leave_approval_api.postman_collection.json   # Postman API Collection
├── leave_approval_environment.postman_environment.json # Postman Environment Variables
├── drivers/chromedriver.exe                 # Local ChromeDriver binary
├── screenshots/                             # Automatically captured test run screenshots
├── TEACHER_PRESENTATION_MANUAL.md           # Comprehensive presentation & viva study guide
└── README.md                                # Project documentation
```

---

## 🚀 Quick Execution Guide

### 1. Prerequisites & Installation
Ensure Python 3.10+ and Node.js are installed. In PyCharm terminal or PowerShell:
```bash
pip install selenium webdriver-manager pytest requests
```

### 2. Run All Tests (1-Command Runner)
```bash
python run_all_tests.py
```
*This launches `node server.js` in the background, executes all 12 Selenium UI, POM, and API test cases, generates screenshots in `screenshots/`, and prints a formatted summary.*

### 3. Run Selenium UI Tests Individually
```bash
python test_selenium_leave_approval.py
```

### 4. Run Page Object Model (POM) Suite
```bash
python -m unittest automation_framework.tests.test_leave_approval_pom
```

### 5. Run Python API Tests
Start the server in one terminal:
```bash
node server.js
```
In another terminal:
```bash
python test_api_leave_approval.py
```

### 6. Run Postman Collection via Newman CLI
```bash
npx newman run leave_approval_api.postman_collection.json -e leave_approval_environment.postman_environment.json
```

---

## 📖 Complete Documentation & Viva Guide
For a deep dive into every topic requested by your teacher (STLC, Wait types, Locators, REST vs SOAP, Postman Request Chaining), refer to [TEACHER_PRESENTATION_MANUAL.md](file:///F:/leave-approval-system-main/TEACHER_PRESENTATION_MANUAL.md).
