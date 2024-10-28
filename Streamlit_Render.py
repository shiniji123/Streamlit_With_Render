import streamlit as st
import psycopg2
import pandas as pd
from datetime import datetime

# Connection string สำหรับ PostgreSQL บน Render
CONNECTION_STRING = "postgresql://anucha:q9D3933OODrMo7hIJHLfaxPeqQlLFQat@dpg-csfqptij1k6c73b2k240-a.singapore-postgres.render.com/enrollments_sj13"

# ฟังก์ชันสำหรับเชื่อมต่อกับฐานข้อมูล
@st.cache_resource
def get_connection():
    try:
        conn = psycopg2.connect(CONNECTION_STRING)
        return conn
    except Exception as e:
        st.error(f"Failed to connect to the database: {e}")
        return None

# ฟังก์ชันสำหรับการดึงข้อมูล
def fetch_data(query):
    conn = get_connection()
    df = pd.read_sql(query, conn)
    conn.close()
    return df

# ฟังก์ชันสำหรับการเพิ่มข้อมูล
def execute_query(query, params=None):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        conn.commit()
        st.success("Operation successful!")
    except Exception as e:
        st.error(f"Operation failed: {e}")
    finally:
        cursor.close()
        conn.close()

# สร้าง Sidebar สำหรับการเลือก Role
role = st.sidebar.selectbox("Select Role", ["Admin", "Student"])

if role == "Admin":
    st.title("Admin Dashboard")
    st.write("Manage students, courses, and enrollments")

    tab1, tab2, tab3 = st.tabs(["Manage Students", "Manage Courses", "Manage Enrollments"])

    # Tab 1: Manage Students
    with tab1:
        st.subheader("Students List")
        students = fetch_data("SELECT * FROM students")
        st.dataframe(students)

        st.subheader("Add/Update Student")
        with st.form("student_form"):
            student_id = st.text_input("Student ID")
            first_name = st.text_input("First Name")
            last_name = st.text_input("Last Name")
            email = st.text_input("Email")
            contact_number = st.text_input("Contact Number")
            address = st.text_input("Address")
            enrollment_date = st.date_input("Enrollment Date", datetime.now())
            student_password = st.text_input("Password", type="password")
            submit_student = st.form_submit_button("Submit")

            if submit_student:
                if student_id:
                    query = '''
                        INSERT INTO students (student_id, first_name, last_name, email, contact_number, address, enrollment_date, student_password)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                        ON CONFLICT (student_id) DO UPDATE SET 
                        first_name = EXCLUDED.first_name,
                        last_name = EXCLUDED.last_name,
                        email = EXCLUDED.email,
                        contact_number = EXCLUDED.contact_number,
                        address = EXCLUDED.address,
                        enrollment_date = EXCLUDED.enrollment_date,
                        student_password = EXCLUDED.student_password;
                    '''
                    params = (student_id, first_name, last_name, email, contact_number, address, enrollment_date, student_password)
                    execute_query(query, params)

    # Tab 2: Manage Courses
    with tab2:
        st.subheader("Courses List")
        courses = fetch_data("SELECT * FROM courses")
        st.dataframe(courses)

        st.subheader("Add/Update Course")
        with st.form("course_form"):
            course_id = st.text_input("Course ID")
            course_name = st.text_input("Course Name")
            credits = st.number_input("Credits", min_value=1, step=1)
            department_id = st.text_input("Department ID")
            instructor_id = st.text_input("Instructor ID")
            submit_course = st.form_submit_button("Submit")

            if submit_course:
                if course_id:
                    query = '''
                        INSERT INTO courses (course_id, course_name, credits, department_id, instructor_id)
                        VALUES (%s, %s, %s, %s, %s)
                        ON CONFLICT (course_id) DO UPDATE SET 
                        course_name = EXCLUDED.course_name,
                        credits = EXCLUDED.credits,
                        department_id = EXCLUDED.department_id,
                        instructor_id = EXCLUDED.instructor_id;
                    '''
                    params = (course_id, course_name, credits, department_id, instructor_id)
                    execute_query(query, params)

    # Tab 3: Manage Enrollments
    with tab3:
        st.subheader("Enrollments List")
        enrollments = fetch_data("SELECT * FROM enrollments")
        st.dataframe(enrollments)

        st.subheader("Add Enrollment")
        with st.form("enrollment_form"):
            student_id = st.text_input("Student ID for Enrollment")
            course_id = st.text_input("Course ID for Enrollment")
            semester = st.text_input("Semester")
            year = st.number_input("Year", min_value=2020, step=1)
            enrollment_date = st.date_input("Enrollment Date", datetime.now())
            submit_enrollment = st.form_submit_button("Submit")

            if submit_enrollment:
                if student_id and course_id:
                    query = '''
                        INSERT INTO enrollments (student_id, course_id, semester, year, enrollment_date)
                        VALUES (%s, %s, %s, %s, %s);
                    '''
                    params = (student_id, course_id, semester, year, enrollment_date)
                    execute_query(query, params)

elif role == "Student":
    st.title("Student Dashboard")
    student_id = st.text_input("Enter Your Student ID")

    if student_id:
        enrolled_courses = fetch_data(f"SELECT * FROM enrollments WHERE student_id = {student_id}")
        st.subheader(f"Enrolled Courses for Student ID: {student_id}")
        st.dataframe(enrolled_courses)

        st.subheader("Withdraw Course")
        course_to_withdraw = st.text_input("Enter Course ID to Withdraw")
        if st.button("Withdraw"):
            if course_to_withdraw:
                query = '''
                    DELETE FROM enrollments WHERE student_id = %s AND course_id = %s;
                '''
                params = (student_id, course_to_withdraw)
                execute_query(query, params)

