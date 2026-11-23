# Leave Approval System - Testing Documentation
**Project:** Leave Approval System  
**Testing Frameworks:** Postman (API Testing) & Selenium WebDriver (UI Automation Testing)  
**Live Deployed URL:** `https://alfiyazareen.github.io/leave-approval-system/`  

---

## Part 1: Selenium UI Automated Test Cases

| Test Case ID | Test Scenario | Test Steps | Expected Result | Status |
| :--- | :--- | :--- | :--- | :--- |
| **TC_UI_01** | Page Load & Title Verification | Open Application URL in Chrome. Inspect page title & login box visibility. | Title contains "Leave Approval System" and Login card is displayed. | **PASS** |
| **TC_UI_02** | Login Input Validation | Leave Username field empty and click "Login" button. | Browser alert dialog triggers displaying `"Enter username"`. | **PASS** |
| **TC_UI_03** | Employee Leave Application | 1. Enter username: `"Alfiya"`<br>2. Select Role: `"Employee"`<br>3. Fill Start Date, End Date, Reason<br>4. Click "Apply Leave" | Alert `"Leave applied!"` appears; request is rendered under the **Pending** column. | **PASS** |
| **TC_UI_04** | Manager Dashboard Navigation | 1. Click "← Back"<br>2. Enter username: `"ManagerJane"`<br>3. Select Role: `"Manager"`<br>4. Click "Login" | Manager dashboard loads displaying all submitted employee leave requests. | **PASS** |
| **TC_UI_05** | Manager Leave Approval | Locate pending leave request under Manager dashboard and click "Approve". | Request instantly moves from **Pending** section to **Approved** section. | **PASS** |
| **TC_UI_06** | Manager Leave Rejection | Locate pending leave request and click "Reject". | Request moves to **Rejected** section. | **PASS** |

### How to Run Selenium Tests (Python)
1. Install dependencies:
   ```bash
   pip install selenium webdriver-manager
   ```
2. Execute the test suite:
   ```bash
   python test_leave_approval.py
   ```
3. Automatic screenshots will be saved in the `screenshots/` directory for submission.

---

## Part 2: Postman API Test Suite

The API server runs locally at `http://localhost:3000`.

| Request Name | HTTP Method | Endpoint | Request Payload | Expected Status | Postman Assertion |
| :--- | :---: | :--- | :--- | :---: | :--- |
| **1. Health Check** | `GET` | `/api/health` | None | `200 OK` | `pm.expect(jsonData.status).to.eql("UP");` |
| **2. User Login** | `POST` | `/api/login` | `{"username":"Alfiya","role":"employee"}` | `200 OK` | `pm.expect(jsonData.message).to.eql("Login successful");` |
| **3. Apply Leave** | `POST` | `/api/leaves` | `{"user":"Alfiya","reason":"Medical","start":"2026-12-01","end":"2026-12-05"}` | `201 Created` | `pm.expect(jsonData.leave.status).to.eql("Pending");` |
| **4. Get All Leaves** | `GET` | `/api/leaves` | None | `200 OK` | `pm.expect(jsonData.leaves).to.be.an("array");` |
| **5. Approve Leave** | `PUT` | `/api/leaves/1` | `{"status":"Approved"}` | `200 OK` | `pm.expect(jsonData.leave.status).to.eql("Approved");` |
| **6. Reject Leave** | `PUT` | `/api/leaves/1` | `{"status":"Rejected"}` | `200 OK` | `pm.expect(jsonData.leave.status).to.eql("Rejected");` |

### How to Run Postman Tests
1. Start the API server in your terminal:
   ```bash
   node server.js
   ```
2. Open Postman:
   - Click **Import** (top left).
   - Select `leave_approval_api.postman_collection.json`.
3. Click the three dots `...` next to the imported collection → **Run collection**.
4. Click **Run Leave Approval System API Tests**. All tests will execute with green pass indicators.
