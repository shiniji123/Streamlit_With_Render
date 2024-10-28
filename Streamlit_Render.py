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
    if conn is not None:
        try:
            with conn.cursor() as cursor:
                cursor.execute(query)
                df = pd.DataFrame(cursor.fetchall(), columns=[desc[0] for desc in cursor.description])
                return df
        except psycopg2.Error as e:
            st.error(f"Database error: {e.pgcode} - {e.pgerror}")
            return pd.DataFrame()
        except Exception as e:
            st.error(f"Failed to fetch data: {e}")
            return pd.DataFrame()
        finally:
            conn.close()
    else:
        st.error("No connection to the database.")
        return pd.DataFrame()

# ฟังก์ชันสำหรับการเพิ่มข้อมูล (ปรับปรุง)
def execute_query(query, params=None):
    conn = get_connection()
    if conn is not None:
        try:
            with conn.cursor() as cursor:
                if params:
                    cursor.execute(query, params)
                else:
                    cursor.execute(query)
                conn.commit()
                st.success("Operation successful!")
        except Exception as e:
            st.error(f"Operation failed: {e}")
        finally:
            conn.close()  # ปิดการเชื่อมต่อหลังจากเสร็จสิ้น
    else:
        st.error("No connection to the database.")

# ฟังก์ชันสำหรับสร้างตารางในฐานข้อมูล
def create_tables():
    queries = [
        '''
        CREATE TABLE IF NOT EXISTS Students (
            student_id SERIAL PRIMARY KEY,        
            first_name VARCHAR(50) NOT NULL,   
            last_name VARCHAR(50) NOT NULL,                
            email VARCHAR(100) NOT NULL UNIQUE,   
            contact_number VARCHAR(15),          
            address VARCHAR(200),                         
            enrollment_date DATE NOT NULL,
            student_password VARCHAR(20)
        );
        ''',
        '''
        CREATE TABLE IF NOT EXISTS Departments (
            department_id SERIAL PRIMARY KEY,    
            department_name VARCHAR(100) NOT NULL
        );
        ''',
        '''
        CREATE TABLE IF NOT EXISTS Instructors (
            instructor_id SERIAL PRIMARY KEY,   
            first_name VARCHAR(50) NOT NULL,      
            last_name VARCHAR(50) NOT NULL,      
            department_id INT NOT NULL,           
            email VARCHAR(100) NOT NULL UNIQUE,   
            contact_number VARCHAR(15),        
            FOREIGN KEY (department_id) REFERENCES Departments(department_id) ON DELETE CASCADE
        );
        ''',
        '''
        CREATE TABLE IF NOT EXISTS Courses (
            course_id SERIAL PRIMARY KEY,       
            course_name VARCHAR(100) NOT NULL,   
            credits INT NOT NULL,                
            department_id INT NOT NULL,          
            instructor_id INT NOT NULL,          
            FOREIGN KEY (department_id) REFERENCES Departments(department_id) ON DELETE CASCADE,
            FOREIGN KEY (instructor_id) REFERENCES Instructors(instructor_id) ON DELETE CASCADE
        );
        ''',
        '''
        CREATE TABLE IF NOT EXISTS Enrollments (
            enrollment_id SERIAL PRIMARY KEY,    
            student_id INT NOT NULL,              
            course_id INT NOT NULL,               
            semester VARCHAR(10) NOT NULL,        
            year INT NOT NULL,                    
            grade VARCHAR(2),                     
            enrollment_date DATE NOT NULL,       
            FOREIGN KEY (student_id) REFERENCES Students(student_id) ON DELETE CASCADE,
            FOREIGN KEY (course_id) REFERENCES Courses(course_id) ON DELETE CASCADE
        );
        '''
    ]
    for query in queries:
        execute_query(query)
    st.success("Tables created successfully!")

# ฟังก์ชันสำหรับแทรกข้อมูลเบื้องต้นในตาราง
def insert_sample_data():
    queries = [
        '''
        INSERT INTO Students (first_name, last_name, email, contact_number, address, enrollment_date, student_password)
        VALUES
        ('Somchai', 'Suksan', 'somchai.s@email.com', '088-1234-567', '123 Phahonyothin Road Bangkok', '2024-09-01', '1'),
        ('Suda', 'Chaiyo', 'suda.c@email.com', '088-5678-910', '456 Sukhumvit Road Bangkok', '2024-09-01', 'vZ5uP7xE'),
        ('Nattapong', 'Jindarat', 'nattapong.j@email.com', '088-2345-678', '789 Phetkasem Road Bangkok', '2024-09-02', '9xF1tS3b');
        ''',
        '''
        INSERT INTO Departments (department_name)
        VALUES
        ('Computer Science'), ('Mathematics'), ('Physics'), ('Chemistry'), ('Biology');
        ''',
        '''
        INSERT INTO Instructors (first_name, last_name, department_id, email, contact_number)
        VALUES
        ('Tanakrit', 'Phromwong', 1, 'tanakrit.p@email.com', '089-1234-567'),
        ('Kanya', 'Srisai', 2, 'kanya.s@email.com', '089-5678-910'),
        ('Wirot', 'Chareonrat', 3, 'wirot.c@email.com', '089-2345-678');
        ''',
        '''
        INSERT INTO Courses (course_name, credits, department_id, instructor_id)
        VALUES
        ('Database', 3, 1, 1), ('Math Analysis', 3, 2, 2), ('Thermodynamic', 2, 3, 3);
        ''',
        '''
        INSERT INTO Enrollments (student_id, course_id, semester, year, enrollment_date)
        VALUES
        (1, 1, '1', 2024, '2024-09-01'), (2, 2, '1', 2024, '2024-09-02'), (3, 3, '1', 2024, '2024-09-03');
        '''
    ]
    for query in queries:
        execute_query(query)
    st.success("Sample data inserted successfully!")

# สร้าง Sidebar สำหรับการเลือก Role
role = st.sidebar.selectbox("Select Role", ["Admin", "Student"])

if role == "Admin":
    st.title("Admin Dashboard")
    st.write("Manage students, courses, and enrollments")

    if st.button("Create Tables"):
        create_tables()

    if st.button("Insert Sample Data"):
        insert_sample_data()

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
