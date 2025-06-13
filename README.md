# 💾 DBMS Project – Group 8

A full-stack web application developed as part of an academic **Database Management Systems** course. It demonstrates CRUD operations, role-based access control, and modular design using Python (Flask) and a relational database.

🌐 **Live Demo**: [dbms-project-fci-management.onrender.com](https://dbms-project-fci-management.onrender.com)

---

## 🚀 Features

🔐 **Role-Based Login System**

* **Admin**: Manage users and global data
* **Dealer**: Handle inventory, product listings, and orders
* **Employee**: Perform daily transactions and operations

🗄️ **Database-Driven**

* Structured schema using a relational database (e.g., MySQL)
* Operations for insert, update, delete, and search

📦 **Modular Codebase**

* Separate logic for each user role (admin, employee, dealer)
* Clean separation of frontend (`templates`, `static`) and backend (`app.py`, role modules)

🎨 **Responsive Interface**

* Styled HTML templates and forms
* Basic CSS and JavaScript for interactivity

---

## 🛠️ Tech Stack

* **Backend**: Python, Flask
* **Frontend**: HTML5, CSS3, JS
* **Database**: MySQL (or compatible RDBMS)
* **Hosting**: [Render](https://render.com)

---

## 📁 Folder Structure

```
dbms-project-group8/
├── admin/                  # Admin-specific routes and logic
├── Dealer/                 # Dealer-specific routes and logic
├── employee/               # Employee-specific routes and logic
├── static/                 # CSS, JS, images
├── templates/              # HTML pages
├── app.py                  # Main Flask app
├── requirements.txt        # Python dependencies
├── runtime.txt             # Deployment runtime version
└── README.md               # Project documentation
```

---

## ⚙️ Setup Instructions

### 1. Clone the Repo

```bash
git clone https://github.com/k-u-kiran01/dbms-project-group8.git
cd dbms-project-group8
```

### 2. Create Virtual Environment (Optional but Recommended)

```bash
python -m venv venv
source venv/bin/activate      # macOS/Linux
venv\Scripts\activate         # Windows
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Database

* Create a MySQL database
* Update DB credentials and connection logic in `app.py` or relevant config file

### 5. Run the App

```bash
python app.py
```

App should be available at `http://localhost:5000`

---

## 👤 Users & Roles

| Role     | Permissions                                            |
| -------- | ------------------------------------------------------ |
| Admin    | Create/Delete users, oversee data, system-wide control |
| Dealer   | Manage products, stocks, and orders                    |
| Employee | Perform day-to-day operations                          |

---

## 🤝 Contributing

Pull requests are welcome! Follow these steps:

```bash
git checkout -b feature/my-feature
git commit -m "Add something cool"
git push origin feature/my-feature
```

Then open a pull request 🎉

---

## 📜 License

MIT License
Feel free to use, fork, and contribute.

---

## 📧 Contact

**Maintainer**: [@k-u-kiran01](https://github.com/k-u-kiran01)
Feel free to raise issues or feature requests via GitHub!

---
