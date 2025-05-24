import os
from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from werkzeug.utils import secure_filename
from .models import db, Airline, Aircraft, Registration
from flask import abort, send_from_directory

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

@admin_bp.route('/add_airline', methods=['GET', 'POST'])
def add_airline():
    if request.method == 'POST':
        name = request.form.get('name')
        if not name:
            flash('Airline name is required.', 'error')
        else:
            existing_airline = Airline.query.filter_by(name=name).first()
            if existing_airline:
                flash(f'Airline "{name}" already exists.', 'info')
            else:
                new_airline = Airline(name=name)
                db.session.add(new_airline)
                db.session.commit()
                flash(f'Airline "{name}" added successfully.', 'success')
                return redirect(url_for('admin.add_airline'))
    return render_template('admin/add_airline.html')

@admin_bp.route('/add_aircraft', methods=['GET', 'POST'])
def add_aircraft():
    if request.method == 'POST':
        name = request.form.get('name')
        airline_id = request.form.get('airline_id')

        if not name or not airline_id:
            flash('Aircraft name and airline are required.', 'error')
        else:
            airline = Airline.query.get(airline_id)
            if not airline:
                flash('Selected airline is invalid.', 'error')
            else:
                new_aircraft = Aircraft(name=name, airline_id=airline_id)
                db.session.add(new_aircraft)
                db.session.commit()
                flash(f'Aircraft "{name}" added successfully for {airline.name}.', 'success')
                return redirect(url_for('admin.add_aircraft'))
    
    airlines = Airline.query.all()
    return render_template('admin/add_aircraft.html', airlines=airlines)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@admin_bp.route('/add_registration', methods=['GET', 'POST'])
def add_registration():
    if request.method == 'POST':
        registration_code = request.form.get('registration_code')
        aircraft_id = request.form.get('aircraft_id')
        notes = request.form.get('notes')
        photo = request.files.get('photo')

        if not registration_code or not aircraft_id:
            flash('Registration code and aircraft are required.', 'error')
        else:
            aircraft = Aircraft.query.get(aircraft_id)
            if not aircraft:
                flash('Selected aircraft is invalid.', 'error')
            else:
                filename = None
                if photo and allowed_file(photo.filename):
                    filename = secure_filename(photo.filename)
                    # Construct the full path using the 'uploads' directory at the root of the project
                    # current_app.root_path is the 'app' directory, so we go up one level
                    upload_folder = os.path.join(current_app.root_path, '..', current_app.config['UPLOAD_FOLDER'])
                    if not os.path.exists(upload_folder):
                        os.makedirs(upload_folder) # Ensure the upload folder exists
                    photo.save(os.path.join(upload_folder, filename))
                
                new_registration = Registration(
                    registration_code=registration_code,
                    aircraft_id=aircraft_id,
                    notes=notes,
                    photo_filename=filename
                )
                db.session.add(new_registration)
                db.session.commit()
                flash(f'Registration "{registration_code}" added successfully for {aircraft.name}.', 'success')
                return redirect(url_for('admin.add_registration'))

    aircraft_list = Aircraft.query.all() # Renamed to avoid conflict with aircraft variable in POST
    return render_template('admin/add_registration.html', aircraft_list=aircraft_list)

# Blueprint for public/archive routes
archive_bp = Blueprint('archive', __name__, url_prefix='/archive')

@archive_bp.route('/')
@archive_bp.route('/airlines')
def list_airlines():
    airlines = Airline.query.order_by(Airline.name).all()
    return render_template('archive/list_airlines.html', airlines=airlines)

@archive_bp.route('/airline/<int:airline_id>/aircraft')
def list_aircraft_for_airline(airline_id):
    airline = Airline.query.get_or_404(airline_id)
    # Aircraft are ordered by name by default (as defined in relationship, or can be specified here)
    # aircraft_list = Aircraft.query.filter_by(airline_id=airline_id).order_by(Aircraft.name).all()
    # Simpler way if relationship is well-defined and backref is 'aircraft'
    aircraft_list = airline.aircraft 
    return render_template('archive/list_aircraft.html', airline=airline, aircraft_list=aircraft_list)

@archive_bp.route('/aircraft/<int:aircraft_id>/registrations')
def list_registrations_for_aircraft(aircraft_id):
    aircraft = Aircraft.query.get_or_404(aircraft_id)
    # Registrations can be accessed via backref, e.g., aircraft.registrations
    # Order them if necessary, e.g., by registration_code
    registrations = sorted(aircraft.registrations, key=lambda r: r.registration_code)
    return render_template('archive/list_registrations.html', aircraft=aircraft, registrations=registrations)

@archive_bp.route('/uploads/<filename>')
def uploaded_file(filename):
    # Correctly construct the path to the UPLOAD_FOLDER
    # current_app.root_path is the 'app' directory. UPLOAD_FOLDER is relative to the project root.
    upload_folder_abs = os.path.join(current_app.root_path, '..', current_app.config['UPLOAD_FOLDER'])
    return send_from_directory(upload_folder_abs, filename)

@archive_bp.route('/imprint')
def imprint():
    return render_template('static_pages/imprint.html')
