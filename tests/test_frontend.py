import pytest
from playwright.sync_api import Page, expect
from subprocess import Popen, PIPE
import time

# Fixture to start Vue development server before tests
@pytest.fixture(scope="module")
def vue_server():
    # Start Vue server in psy_admin_vue directory
    server = Popen(
        ["npm", "run", "serve"],
        cwd="../psy_admin_vue",
        stdout=PIPE,
        stderr=PIPE,
        text=True
    )
    # Wait for server to start (adjust timeout if needed)
    time.sleep(5)
    yield server
    # Terminate server after tests
    server.terminate()

def test_student_management_component_renders(page: Page, vue_server):
    # Navigate to Student Management page
    page.goto("http://localhost:8080/#/student-management")
    
    # Verify page title and header
    expect(page).to_have_title("学生管理 - 心理测评系统")
    expect(page.locator("h2.page-title")).to_have_text("学生信息管理")
    
    # Verify table structure and sample data
    expect(page.locator("table.student-table")).to_be_visible()
    expect(page.locator("table.student-table th")).to_have_texts(["学号", "姓名", "年龄", "操作"])
    
    # Verify initial student records (assuming 2 sample students exist)
    student_rows = page.locator("table.student-table tbody tr")
    expect(student_rows).to_have_count(2)
    expect(student_rows.nth(0)).to_contain_text("20230001 Alice Smith 18")
    expect(student_rows.nth(1)).to_contain_text("20230002 Bob Johnson 19")

def test_student_management_api_call(page: Page, vue_server):
    # Navigate to Student Management page
    page.goto("http://localhost:8080/#/student-management")
    
    # Wait for API data to load
    page.wait_for_selector("table.student-table tbody tr", state="visible")
    
    # Verify API request was made (using network intercept)
    with page.expect_request("**/api/students") as request_info:
        # Refresh page to trigger API call
        page.reload()
    request = request_info.value
    
    # Verify request details
    assert request.method == "GET", "Should send GET request to students API"
    assert request.url == "http://localhost:8000/api/students", "Should call correct API endpoint"
    
    # Verify response data (using network response)
    with page.expect_response("**/api/students") as response_info:
        page.reload()
    response = response_info.value
    
    assert response.status == 200, "API response should be 200 OK"
    students = response.json()
    assert len(students) == 2, "Should return 2 student records"
    assert students[0]["student_id"] == 20230001, "First student ID mismatch"

def test_add_student_interaction(page: Page, vue_server):
    page.goto("http://localhost:8080/#/student-management")
    
    # Fill and submit new student form
    page.fill("#student-id-input", "20230003")
    page.fill("#student-name-input", "Charlie Brown")
    page.fill("#student-age-input", "20")
    page.click("#add-student-btn")
    
    # Wait for new row to appear
    page.wait_for_selector("table.student-table tbody tr:nth-child(3)")
    
    # Verify new student was added
    new_student_row = page.locator("table.student-table tbody tr:nth-child(3)")
    expect(new_student_row).to_contain_text("20230003 Charlie Brown 20")
    
    # Verify API call was made
    with page.expect_request("**/api/students") as request_info:
        pass  # Request was already sent by click action
    request = request_info.value
    
    assert request.method == "POST", "Should send POST request to create student"
    payload = request.post_data_json
    assert payload == {
        "student_id": 20230003,
        "name": "Charlie Brown",
        "age": 20
    }, "POST payload mismatch"
