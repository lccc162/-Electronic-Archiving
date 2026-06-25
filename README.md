# 📁 نظام أرشفة الوثائق والكتب | Document Archiving System

مرحباً بك في نظام الأرشيف الإلكتروني. هذا الملف يوفر دليلاً مختصراً للبرنامج باللغتين العربية والإنجليزية.
Welcome to the Electronic Archiving System. This file provides a brief guide for the application in both Arabic and English.

---

## 🌍 اللغة العربية (Arabic)

### 📝 نبذة عن النظام
نظام ويب متكامل مصمم لإدارة وأرشفة الكتب والوثائق الرسمية. يتيح النظام إدخال تفاصيل الكتب، البحث عنها، تصنيفها، ومتابعتها، مع دعم كامل لصلاحيات المستخدمين والاتصال بقواعد البيانات المختلفة.

### ✨ المميزات الرئيسية
* **أرشفة ذكية**: حفظ الكتب وتصنيفها (نوع الكتاب، الرقم، التاريخ، الجهة المرسلة، الجهة المستقبلة، والموضوع).
* **إدارة المرفقات**: إمكانية رفع وتصفح الملفات والوثائق المرفقة مع كل كتاب.
* **نظام متابعة**: تنبيهات وتواريخ لمتابعة الكتب الهامة والمهام المعلقة.
* **صلاحيات مرنة (RBAC)**: ثلاثة أدوار للمستخدمين:
  1. **مدير البرنامج**: صلاحيات كاملة لإدارة المستخدمين، الأقسام، وأنواع الكتب.
  2. **محرر/مدخل بيانات**: صلاحية إضافة وتعديل الكتب والمرفقات.
  3. **مشاهدة فقط**: صلاحية البحث والاستعراض فقط دون إمكانية التعديل.
* **قاعدة بيانات مرنة**: يدعم الاتصال بسيرفر **MS SQL Server** بشكل أساسي، مع التحول التلقائي لقاعدة بيانات محلية **SQLite** في حال عدم توفر السيرفر.
* **جاهز للتشغيل**: يعمل بخادم ويب خارجي سريع وآمن (Waitress).

### 🚀 كيفية التشغيل والاستخدام
1. **التشغيل السريع (Windows)**:
   * قم بتشغيل الملف المساعد `run_program.bat` بالنقر المزدوج عليه.
   * سيقوم الملف بتشغيل البرنامج تلقائياً.
2. **رابط الدخول**:
   * افتح المتصفح واذهب إلى الرابط: [http://localhost:8080](http://localhost:8080)
3. **تجميع البرنامج (للحصول على ملف `exe` مستقل)**:
   * قم بتشغيل الملف `package_app.py` عبر الأمر:
     ```bash
     python package_app.py
     ```
   * سينتج عن ذلك ملف تشغيلي مستقل باسم `ArchiveSystem.exe` داخل مجلد `dist`.

---

## 🇬🇧 English Version (الإنجليزية)

### 📝 About the System
A comprehensive web-based application designed for managing and archiving official letters and documents. The system allows users to archive, search, categorize, and track documents, with full support for user roles and multiple database backends.

### ✨ Key Features
* **Smart Archiving**: Store and categorize documents (Type, Number, Date, Source, Receiver, and Subject).
* **Attachments Management**: Easily upload and browse attached files or scanned documents.
* **Follow-up System**: Set dates and alerts to track important documents and pending actions.
* **Role-Based Access Control (RBAC)**: Three distinct user roles:
  1. **Program Manager (Admin)**: Full control to manage users, departments, and document types.
  2. **Editor/Data Entry**: Permission to add and modify documents and attachments.
  3. **View Only**: Read-only access to search and browse documents.
* **Flexible Database**: Connects to **MS SQL Server** as the primary database, with an automatic fallback to local **SQLite** if the server is unreachable.
* **Production-Ready**: Served via a secure and high-performance WSGI server (Waitress).

### 🚀 How to Run & Use
1. **Quick Start (Windows)**:
   * Double-click on `run_program.bat`.
   * This script will automatically boot up the application server.
2. **Accessing the App**:
   * Open your web browser and navigate to: [http://localhost:8080](http://localhost:8080)
3. **Packaging the App (Building a standalone `exe`)**:
   * Run the packaging script with:
     ```bash
     python package_app.py
     ```
   * This will compile the application into a single executable `ArchiveSystem.exe` inside the `dist/` directory.

---

### 📂 هيكلية المجلدات | Folder Structure
* `app.py`: منطق التطبيق البرمجي وقواعد البيانات (The main application and database logic).
* `wsgi.py`: نقطة انطلاق خادم التشغيل Waitress (Waitress production server entry point).
* `run_program.bat`: ملف التشغيل السريع للمستخدمين (Quick start batch script).
* `templates/`: واجهات العرض الخاصة بالنظام (HTML templates/pages).
* `static/`: ملفات التنسيق والصور والتصميم (CSS styles & assets).
* `uploads/`: المجلد الذي تحفظ فيه الملفات المرفوعة (Directory for uploaded attachments).
