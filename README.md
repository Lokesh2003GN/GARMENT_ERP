# Garment ERP

A comprehensive ERP system for garment manufacturing and management, built with Django. This project helps manage staff, wages, yarn, warp designs, transactions, and more, tailored for textile businesses.

## Features
- Staff and account management
- Yarn and warp design tracking
- Piece and wage management
- Transaction history and reporting
- Role-based dashboards (Owner, Staff, Warper, Weaver)

## Folder Structure
```
core/                # Main Django app with models, views, templates, static files
  migrations/        # Database migrations
  static/core/       # CSS, images, and static assets
  templates/core/    # HTML templates for all pages
  templatetags/      # Custom Django template tags and filters
garment_erp/         # Project settings and configuration
manage.py            # Django management script
db.sqlite3           # SQLite database
requirements.txt     # Python dependencies
```

## Setup Instructions
1. **Clone the repository**
	```bash
	git clone https://github.com/Lokesh2003GN/GARMENT_ERP.git
	cd garment_erp
	```
2. **Install dependencies**
	```bash
	pip install -r requirements.txt
	```
3. **Apply migrations**
	```bash
	python manage.py migrate
	```
4. **Run the development server**
	```bash
	python manage.py runserver
	```
5. **Access the app**
	Open your browser and go to `http://127.0.0.1:8000/`

## Usage
- Log in with your account credentials.
- Use the dashboard to manage staff, yarn, warp designs, and transactions.
- Owners, staff, warpers, and weavers have dedicated dashboards and permissions.

## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

## License
This project is licensed under the MIT License.