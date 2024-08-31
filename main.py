from flask import Flask, render_template, request, flash, redirect, url_for
from flask_login import login_user, logout_user, login_required, current_user, UserMixin, LoginManager
import mysql.connector

app = Flask(__name__)
app.secret_key = 'abhi'

login_manager = LoginManager()
login_manager.init_app(app)

mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    password="mySql@4321",
    database="project1"
)

mycursor = mydb.cursor()

class User(UserMixin):
    def __init__(self, id):
        self.id = id

    @property
    def is_authenticated(self):
        return True

    @property
    def is_active(self):
        return True

    @property
    def is_anonymous(self):
        return False

    def get_id(self):
        return str(self.id)

users = {'admin': {'password': 'password'}, 'user1': {'password': '123456'}}

@login_manager.user_loader
def load_user(user_id):
    user_data = users.get(user_id)
    if user_data:
        return User(user_id)
    return None

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        if username in users and users[username]['password'] == password:
            user = User(username)
            login_user(user)
            flash('Logged in successfully!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Invalid username or password', 'danger')
            return redirect(url_for('login'))
    else:
        return render_template('login.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logged out successfully!', 'success')
    return redirect(url_for('index'))

def insert_project_data(project_id, pname, domain):
    try:
        insert_sql = "INSERT INTO project (project_id, pname, domain) VALUES (%s, %s, %s)"
        insert_val = (project_id, pname, domain)
        mycursor.execute(insert_sql, insert_val)
        mydb.commit()
        return "Project data inserted successfully!"
    except mysql.connector.IntegrityError:
        return "Project with ID {} already exists.".format(project_id)

def insert_availability(FACULTY_ID,availability_status):
    try:
        insert_sql = "INSERT INTO availability (FACULTY_ID,availability_status) VALUES (%s,%s)"
        insert_val = (FACULTY_ID,availability_status)
        mycursor.execute(insert_sql, insert_val)
        mydb.commit()
        return "Availability data inserted successfully!"
    except mysql.connector.IntegrityError:
        return "Availability data for Faculty ID {} already exists.".format(FACULTY_ID)

def insert_faculty_data(FACULTY_ID, NAME, CONTACT, EMAIL, DEPARTMENT, cabin_no, location):
    try:
        insert_sql = "INSERT INTO faculty (FACULTY_ID, NAME, CONTACT, EMAIL, DEPARTMENT, cabin_no, location) VALUES (%s, %s, %s, %s, %s, %s, %s)"
        insert_val = (FACULTY_ID, NAME, CONTACT, EMAIL, DEPARTMENT,cabin_no, location)
        mycursor.execute(insert_sql, insert_val)
        mydb.commit()
        return "Faculty data inserted successfully!"
    except mysql.connector.IntegrityError:
        return "Faculty with ID {} already exists.".format(FACULTY_ID)

def insert_TA_data(ta_id, email,cabin_no, location,course_name):
    try:
        insert_sql = "INSERT INTO ta (ta_id,email,cabin_no, location,course_name) VALUES (%s, %s, %s, %s, %s)"
        insert_val = (ta_id,email,cabin_no, location,course_name)
        mycursor.execute(insert_sql, insert_val)
        mydb.commit()
        return "TA data inserted successfully!"
    except mysql.connector.IntegrityError:
        return "TA with ID {} already exists.".format(ta_id)

def insert_assists_data(faculty_id,ta_id,course_name):
    try:
        insert_sql = "INSERT INTO assists (faculty_id,ta_id,course_name) VALUES (%s, %s, %s)"
        insert_val = (faculty_id,ta_id,course_name)
        mycursor.execute(insert_sql, insert_val)
        mydb.commit()
        return "Assists data inserted successfully!"
    except mysql.connector.IntegrityError:
        return "Assists data already exists for Faculty ID {} and TA ID {}.".format(faculty_id, ta_id)

def faculty_details(FACULTY_ID):
    mycursor.execute("SELECT * FROM faculty WHERE FACULTY_ID = %s", (FACULTY_ID,))
    result = mycursor.fetchone()
    return result

def TA_details(ta_id):
    mycursor.execute("SELECT * FROM ta WHERE ta_id = %s", (ta_id,))
    result = mycursor.fetchone()
    return result

def faculty_project_details(FACULTY_ID):
    mycursor.execute("SELECT w.faculty_id,p.project_id,p.pname,p.domain FROM faculty f,project p,works_on w WHERE f.FACULTY_ID=w.FACULTY_ID and w.project_id=p.project_id AND f.FACULTY_ID= %s", (FACULTY_ID,))
    result = mycursor.fetchone()
    return result

def faculty_cabin_details(FACULTY_ID):
    mycursor.execute("SELECT a.faculty_id,f.cabin_no,f.location,a.availability_status FROM faculty f,availability a WHERE f.FACULTY_ID=a.FACULTY_ID and f.FACULTY_ID= %s", (FACULTY_ID,))
    result = mycursor.fetchone()
    return result

def work_on(Project_id,FACULTY_ID):
    insert_sql = "INSERT INTO works_on (Project_id,FACULTY_ID) VALUES (%s, %s)"
    insert_val = (Project_id,FACULTY_ID)
    mycursor.execute(insert_sql, insert_val)
    mydb.commit()

def modify_availability_status(FACULTY_ID, availability_status):
    mycursor.execute("SELECT * FROM availability WHERE FACULTY_ID = %s", (FACULTY_ID,))
    existing_faculty = mycursor.fetchone()
    
    if existing_faculty:
        update_sql = "UPDATE availability SET availability_status = %s WHERE FACULTY_ID = %s"
        update_val = (availability_status, FACULTY_ID)
        mycursor.execute(update_sql, update_val)
        mydb.commit()
        return "Availability status modified successfully"
    else:
        return "Faculty ID does not exist"

@app.route('/')
def index():
    return render_template('index.html', current_user=current_user)

@app.route('/addproject', methods=['POST', 'GET'])
@login_required
def submit():
    if request.method == 'POST':
        FACULTY_ID = request.form['FACULTY_ID']
        project_id = request.form['project_id']
        pname = request.form['pname']
        domain = request.form['domain']
        message = insert_project_data(project_id, pname, domain)
        message1 = work_on(project_id,FACULTY_ID)
        return message,message1
    else:
        return render_template('addproject.html', current_user=current_user)

@app.route('/addfaculty', methods=['POST', 'GET'])
@login_required
def facultyit():
    if request.method == 'POST':
        FACULTY_ID = request.form['FACULTY_ID']
        NAME = request.form['NAME']
        CONTACT = request.form['CONTACT']
        EMAIL = request.form['EMAIL']
        DEPARTMENT = request.form['DEPARTMENT']
        cabin_no = request.form['cabin_no']
        location = request.form['location']
        availability_status='-'
        message = insert_faculty_data(FACULTY_ID, NAME, CONTACT, EMAIL, DEPARTMENT,cabin_no, location)
        message1 = insert_availability(FACULTY_ID,availability_status)
        return message,message1
    else:
        return render_template('addfaculty.html', current_user=current_user)

@app.route('/addTA', methods=['POST', 'GET'])
@login_required
def TA():
    if request.method == 'POST':
        faculty_id = request.form['faculty_id']
        ta_id = request.form['ta_id']
        email = request.form['email']
        cabin_no = request.form['cabin_no']
        location = request.form['location']
        course_name = request.form['course_name']
        message = insert_TA_data(ta_id,email,cabin_no, location,course_name)
        message1 = insert_assists_data(faculty_id,ta_id,course_name)
        return message,message1
    else:
        return render_template('addTA.html', current_user=current_user)

@app.route('/triggers', methods=['GET', 'POST'])
def triggers():
    if request.method == 'POST':
        FACULTY_ID = request.form['FACULTY_ID']
        faculty_data = faculty_details(FACULTY_ID)
        if faculty_data:
            return render_template('triggers.html', faculty_data=faculty_data)
        else:
            flash('Faculty with ID {} not found.'.format(FACULTY_ID), 'danger')
            return render_template('triggers.html')
    else:
        return render_template('triggers.html', current_user=current_user)

@app.route('/fetchdetails', methods=['GET', 'POST'])
def triggers1():
    if request.method == 'POST':
        FACULTY_ID = request.form['FACULTY_ID']
        faculty_data = faculty_project_details(FACULTY_ID)
        if faculty_data:
            return render_template('triggers1.html', faculty_data=faculty_data)
        else:
            flash('Faculty with ID {} not found.'.format(FACULTY_ID), 'danger')
            return render_template('triggers1.html')
    else:
        return render_template('triggers1.html', current_user=current_user)

@app.route('/cabin', methods=['GET', 'POST'])
def triggers2():
    if request.method == 'POST':
        FACULTY_ID = request.form['FACULTY_ID']
        faculty_data = faculty_cabin_details(FACULTY_ID)
        if faculty_data:
            return render_template('triggers2.html', faculty_data=faculty_data)
        else:
            flash('Faculty with ID {} not found.'.format(FACULTY_ID), 'danger')
            return render_template('triggers2.html')
    else:
        return render_template('triggers2.html', current_user=current_user)

@app.route('/availability_satus', methods=['GET', 'POST'])
@login_required
def triggers3():
    if request.method == 'POST':
        FACULTY_ID = request.form['FACULTY_ID']
        availability_status = request.form['availability_status']
        faculty_data = modify_availability_status(FACULTY_ID, availability_status)
        return render_template('triggers3.html', faculty_data=faculty_data)
    else:
        return render_template('triggers3.html', current_user=current_user)

@app.route('/fetchTAdetails', methods=['GET', 'POST'])
def triggers4():
    if request.method == 'POST':
        ta_id = request.form['ta_id']
        faculty_data = TA_details(ta_id)
        if faculty_data:
            return render_template('triggers4.html', faculty_data=faculty_data)
        else:
            flash('TA with ID {} not found.'.format(ta_id), 'danger')
            return render_template('triggers4.html')
    else:
        return render_template('triggers4.html', current_user=current_user)

if __name__ == '__main__':
    app.run(debug=True)
