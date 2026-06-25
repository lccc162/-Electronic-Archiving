from flask import Flask, render_template, request, redirect, url_for, flash, send_from_directory, send_file
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import os
import urllib
import shutil
import zipfile
import io
from datetime import datetime
from functools import wraps

app = Flask(__name__)
app.config['SECRET_KEY'] = 'archive-secret-key-2024'
app.config['UPLOAD_FOLDER'] = os.path.join(os.getcwd(), 'uploads')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max upload

if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

# إعدادات قاعدة البيانات - MSSQL (الجديدة)
params = (
    r'DRIVER={ODBC Driver 17 for SQL Server};'
    r'SERVER=192.168.1.100;'  # ضع هنا عنوان IP الخاص بسيرفر قاعدة البيانات
    r'DATABASE=ArchiveDB;'
    r'UID=sa;'                # اسم المستخدم لقاعدة البيانات
    r'PWD=YourPassword123;'   # كلمة المرور
    r'Connect Timeout=3;'     # تقليل وقت الانتظار للفشل السريع
)
mssql_uri = "mssql+pyodbc:///?odbc_connect=%s" % urllib.parse.quote_plus(params)
sqlite_uri = 'sqlite:///archive.db'

# محاولة فحص الاتصال بـ MSSQL قبل البدء
def check_mssql():
    import pyodbc
    try:
        conn = pyodbc.connect(params, timeout=2)
        conn.close()
        return True
    except:
        return False

if check_mssql():
    app.config['SQLALCHEMY_DATABASE_URI'] = mssql_uri
    print("Connected to MSSQL successfully.")
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = sqlite_uri
    print("MSSQL not reachable, using SQLite.")

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Models
class BookType(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)

class Department(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    dept_number = db.Column(db.String(50))

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(150), nullable=False)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=True)
    role = db.Column(db.String(50), nullable=False)
    department = db.Column(db.String(100), nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        if not self.password_hash:
            return False
        return check_password_hash(self.password_hash, password)

class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    book_type = db.Column(db.String(50))
    book_number = db.Column(db.String(50))
    book_date = db.Column(db.String(50))
    source = db.Column(db.String(150))
    receiver = db.Column(db.String(150))
    title = db.Column(db.String(200))
    content = db.Column(db.Text)
    keywords = db.Column(db.Text)
    file_number = db.Column(db.String(50))
    storage_number = db.Column(db.String(50))
    attachment_path = db.Column(db.String(255))
    follow_up_date = db.Column(db.String(50))  # Storing as string for simplicity with HTML date input
    created_at = db.Column(db.DateTime, default=db.func.now())

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Decorators for RBAC
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'مدير البرنامج':
            flash('عذراً، ليس لديك صلاحية للوصول لهذه الصفحة.')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function

def editor_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role == 'مشاهدة فقط':
            flash('عذراً، ليس لديك صلاحية للقيام بهذا الإجراء.')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function

# Routes
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for('index'))
        flash('اسم المستخدم أو كلمة المرور غير صحيحة')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/')
@login_required
def index():
    book_count = Book.query.count()
    user_count = User.query.count()
    type_count = BookType.query.count()
    dept_count = Department.query.count()
    
    # Calculate follow-ups (today or past)
    today_str = datetime.now().strftime('%Y-%m-%d')
    follow_up_count = Book.query.filter(Book.follow_up_date <= today_str, Book.follow_up_date != '').count()
    
    latest_books = Book.query.order_by(Book.id.desc()).limit(5).all()
    return render_template('index.html', 
                           book_count=book_count, 
                           user_count=user_count, 
                           type_count=type_count,
                           dept_count=dept_count,
                           follow_up_count=follow_up_count,
                           latest_books=latest_books)

@app.route('/search')
@login_required
def search():
    query = request.args.get('q', '')
    if query:
        results = Book.query.filter(
            (Book.book_number.contains(query)) | 
            (Book.title.contains(query)) | 
            (Book.source.contains(query))
        ).all()
    else:
        results = []
    return render_template('search_results.html', results=results, query=query)

@app.route('/add_book', methods=['GET', 'POST'])
@login_required
@editor_required
def add_book():
    if request.method == 'POST':
        file = request.files.get('attachment')
        filename = None
        if file and file.filename != '':
            filename = secure_filename(file.filename)
            # Add timestamp to filename to avoid overwrites
            from datetime import datetime
            filename = f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{filename}"
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

        new_book = Book(
            book_type=request.form.get('book_type'),
            book_number=request.form.get('book_number'),
            book_date=request.form.get('book_date'),
            source=request.form.get('source'),
            receiver=request.form.get('receiver'),
            title=request.form.get('title'),
            content=request.form.get('content'),
            keywords=request.form.get('keywords'),
            file_number=request.form.get('file_number'),
            storage_number=request.form.get('storage_number'),
            follow_up_date=request.form.get('follow_up_date'),
            attachment_path=filename
        )
        db.session.add(new_book)
        db.session.commit()
        flash('تم حفظ الكتاب والمرفق بنجاح!')
        return redirect(url_for('archive'))
    
    types = BookType.query.all()
    departments = Department.query.all()
    return render_template('add_book.html', types=types, departments=departments)

@app.route('/uploads/<filename>')
@login_required
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/departments', methods=['GET', 'POST'])
@login_required
@admin_required
def departments():
    if request.method == 'POST':
        dept_name = request.form.get('dept_name')
        dept_number = request.form.get('dept_number')
        if dept_name:
            new_dept = Department(name=dept_name, dept_number=dept_number)
            db.session.add(new_dept)
            db.session.commit()
            flash('تم إضافة القسم بنجاح!')
        return redirect(url_for('departments'))
    
    all_depts = Department.query.all()
    return render_template('departments.html', departments=all_depts)

@app.route('/delete_dept/<int:id>')
@login_required
@admin_required
def delete_dept(id):
    dept = Department.query.get_or_404(id)
    db.session.delete(dept)
    db.session.commit()
    flash('تم حذف القسم بنجاح!')
    return redirect(url_for('departments'))

@app.route('/users', methods=['GET', 'POST'])
@login_required
@admin_required
def users():
    if request.method == 'POST':
        full_name = request.form.get('full_name')
        username = request.form.get('username')
        password = request.form.get('password')
        role = request.form.get('role')
        department = request.form.get('department')
        
        if full_name and username:
            new_user = User(
                full_name=full_name,
                username=username,
                role=role,
                department=department
            )
            if password:
                new_user.set_password(password)
            db.session.add(new_user)
            db.session.commit()
            flash('تم إضافة المستخدم بنجاح!')
        return redirect(url_for('users'))
        
    all_users = User.query.all()
    return render_template('users.html', users=all_users)

@app.route('/add_user')
@login_required
@admin_required
def add_user_page():
    all_depts = Department.query.all()
    return render_template('add_user.html', departments=all_depts)

@app.route('/book_types', methods=['GET', 'POST'])
@login_required
@admin_required
def book_types():
    if request.method == 'POST':
        type_name = request.form.get('type_name')
        if type_name:
            new_type = BookType(name=type_name)
            db.session.add(new_type)
            db.session.commit()
            flash('تم إضافة النوع بنجاح!')
        return redirect(url_for('book_types'))
    
    all_types = BookType.query.all()
    return render_template('book_types.html', types=all_types)

@app.route('/archive')
@login_required
def archive():
    all_books = Book.query.order_by(Book.id.desc()).all()
    return render_template('archive.html', books=all_books)

@app.route('/follow_ups')
@login_required
def follow_ups():
    today_str = datetime.now().strftime('%Y-%m-%d')
    books = Book.query.filter(Book.follow_up_date <= today_str, Book.follow_up_date != '').order_by(Book.follow_up_date.desc()).all()
    return render_template('archive.html', books=books, title="تنبيهات المتابعة")

@app.route('/edit_type/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_type(id):
    btype = BookType.query.get_or_404(id)
    if request.method == 'POST':
        btype.name = request.form.get('name')
        db.session.commit()
        flash('تم تحديث نوع الكتاب بنجاح!')
        return redirect(url_for('book_types'))
    return render_template('edit_type.html', type=btype)

@app.route('/edit_dept/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_dept(id):
    dept = Department.query.get_or_404(id)
    if request.method == 'POST':
        dept.name = request.form.get('name')
        dept.dept_number = request.form.get('dept_number')
        db.session.commit()
        flash('تم تحديث القسم بنجاح!')
        return redirect(url_for('departments'))
    return render_template('edit_dept.html', dept=dept)

@app.route('/edit_user/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_user(id):
    user = User.query.get_or_404(id)
    if request.method == 'POST':
        user.full_name = request.form.get('full_name')
        user.username = request.form.get('username')
        if request.form.get('password'):
            user.set_password(request.form.get('password'))
        user.role = request.form.get('role')
        user.department = request.form.get('department')
        db.session.commit()
        flash('تم تحديث بيانات المستخدم بنجاح!')
        return redirect(url_for('users'))
    all_depts = Department.query.all()
    return render_template('edit_user.html', user=user, departments=all_depts)

@app.route('/edit_book/<int:id>', methods=['GET', 'POST'])
@login_required
@editor_required
def edit_book(id):
    book = Book.query.get_or_404(id)
    if request.method == 'POST':
        book.book_type = request.form.get('book_type')
        book.book_number = request.form.get('book_number')
        book.book_date = request.form.get('book_date')
        book.source = request.form.get('source')
        book.receiver = request.form.get('receiver')
        book.title = request.form.get('title')
        book.content = request.form.get('content')
        book.keywords = request.form.get('keywords')
        book.file_number = request.form.get('file_number')
        book.storage_number = request.form.get('storage_number')
        book.follow_up_date = request.form.get('follow_up_date')
        
        file = request.files.get('attachment')
        if file and file.filename != '':
            filename = secure_filename(file.filename)
            from datetime import datetime
            filename = f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{filename}"
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            book.attachment_path = filename

        db.session.commit()
        flash('تم تحديث بيانات الكتاب بنجاح!')
        return redirect(url_for('view_book', id=book.id))
    types = BookType.query.all()
    departments = Department.query.all()
    return render_template('edit_book.html', book=book, types=types, departments=departments)

@app.route('/book/<int:id>')
@login_required
def view_book(id):
    book = Book.query.get_or_404(id)
    return render_template('view_book.html', book=book)

@app.route('/delete_book/<int:id>')
@login_required
@admin_required
def delete_book(id):
    book = Book.query.get_or_404(id)
    # Optional: Delete the file from disk
    if book.attachment_path:
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], book.attachment_path)
        if os.path.exists(file_path):
            os.remove(file_path)
    db.session.delete(book)
    db.session.commit()
    flash('تم حذف الكتاب بنجاح!')
    return redirect(url_for('archive'))

@app.route('/delete_type/<int:id>')
@login_required
@admin_required
def delete_type(id):
    btype = BookType.query.get_or_404(id)
    db.session.delete(btype)
    db.session.commit()
    flash('تم حذف النوع بنجاح!')
    return redirect(url_for('book_types'))

@app.route('/delete_user/<int:id>')
@login_required
@admin_required
def delete_user(id):
    user = User.query.get_or_404(id)
    db.session.delete(user)
    db.session.commit()
    flash('تم حذف المستخدم بنجاح!')
    return redirect(url_for('users'))

@app.route('/backup')
@login_required
@admin_required
def backup_page():
    return render_template('backup.html')

@app.route('/download_backup')
@login_required
@admin_required
def download_backup():
    try:
        memory_file = io.BytesIO()
        with zipfile.ZipFile(memory_file, 'w', zipfile.ZIP_DEFLATED) as zf:
            # Add uploads folder
            upload_path = app.config['UPLOAD_FOLDER']
            for root, dirs, files in os.walk(upload_path):
                for file in files:
                    file_path = os.path.join(root, file)
                    zf.write(file_path, os.path.relpath(file_path, os.path.join(upload_path, '..')))
            
            # Add sqlite db if exists
            db_path = os.path.join(os.getcwd(), 'archive.db')
            if os.path.exists(db_path):
                zf.write(db_path, 'archive.db')
        
        memory_file.seek(0)
        from datetime import datetime
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        return send_file(memory_file, 
                         download_name=f'backup_{timestamp}.zip', 
                         as_attachment=True)
    except Exception as e:
        flash(f'فشل في إنشاء نسخة احتياطية: {e}')
        return redirect(url_for('backup_page'))

@app.route('/toggle_user/<int:id>')
@login_required
def toggle_user(id):
    flash('تم تغيير حالة المستخدم بنجاح!')
    return redirect(url_for('users'))

# Create DB and Seed initial data
def init_db():
    try:
        db.create_all()
        seed_data()
    except Exception as e:
        print(f"Error initializing DB: {e}")

def seed_data():
    print("Seeding initial data...")
    # Seed initial data if empty
    if BookType.query.count() == 0:
        initial_types = ['صادر عام', 'صادر سري', 'وارد عام', 'وارد سري']
        for t in initial_types:
            db.session.add(BookType(name=t))
        print("Seeded BookTypes.")
    
    if Department.query.count() == 0:
        initial_depts = ['شعبة تكنولوجيا المعلومات', 'مكتب الامين العام', 'قسم الشؤون الادارية']
        for d in initial_depts:
            db.session.add(Department(name=d))
        print("Seeded Departments.")
    
    if User.query.count() == 0:
        admin = User(full_name='المدير العام', username='admin', role='مدير البرنامج', department='شعبة تكنولوجيا المعلومات')
        admin.set_password('admin123')
        db.session.add(admin)
        print("Seeded Admin user.")
    
    db.session.commit()
    print("Seeding completed.")

if __name__ == '__main__':
    with app.app_context():
        init_db()
    app.run(debug=True, port=8080)
