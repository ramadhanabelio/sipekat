from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
import mysql.connector
from mysql.connector import Error
import logging
import sys
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/uploads/'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')

app.config['MYSQL_HOST'] = os.getenv('MYSQL_HOST')
app.config['MYSQL_USER'] = os.getenv('MYSQL_USER')
app.config['MYSQL_PASSWORD'] = os.getenv('MYSQL_PASSWORD')
app.config['MYSQL_DB'] = os.getenv('MYSQL_DB')

logging.basicConfig(level=logging.DEBUG)

def create_db_connection():
    try:
        connection = mysql.connector.connect(
            host=app.config['MYSQL_HOST'],
            database=app.config['MYSQL_DB'],
            user=app.config['MYSQL_USER'],
            password=app.config['MYSQL_PASSWORD']
        )
        if connection.is_connected():
            logging.info("Database connection successful")
            return connection
        else:
            raise Exception("Connection is None")
    except Error as e:
        logging.error(f"Database connection failed: {str(e)}")
        sys.exit("Database connection failed")

@app.route('/', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        try:
            connection = create_db_connection()
            cursor = connection.cursor(dictionary=True)
            cursor.execute('SELECT * FROM admin WHERE username = %s AND password = %s', (username, password))
            admin = cursor.fetchone()
            
            if admin:
                session['logged_in'] = True
                session['username'] = username
                return redirect(url_for('dashboard'))
            else:
                error = 'Invalid username or password'
        except Exception as e:
            error = f"Error connecting to the database: {str(e)}"
            logging.error(error)
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()
        
    return render_template('login.html', error=error)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/dashboard')
def dashboard():
    if 'logged_in' not in session:
        return redirect(url_for('login'))
    certificate_count = total_certificates()
    return render_template('dashboard.html', certificate_count=certificate_count)

def total_certificates():
    try:
        connection = create_db_connection()
        cursor = connection.cursor()
        cursor.execute('SELECT COUNT(*) FROM sertifikat')
        count = cursor.fetchone()[0]
        return count
    except Exception as e:
        logging.error(f"Error fetching sertifikat count: {str(e)}")
        return 0
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

@app.route('/sertifikat')
def sertifikat():
    if 'logged_in' not in session:
        return redirect(url_for('login'))
    try:
        connection = create_db_connection()
        cursor = connection.cursor(dictionary=True)
        cursor.execute('SELECT id, judul, nomor_sertifikat, nama_pemegang FROM sertifikat')
        sertifikat_list = cursor.fetchall()
        return render_template('sertifikat.html', sertifikat_list=sertifikat_list)
    except Exception as e:
        error = f"Error fetching sertifikat data: {str(e)}"
        logging.error(error)
        return render_template('sertifikat.html', error=error)
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

@app.route('/sertifikat/<int:id>')
def detail_sertifikat(id):
    if 'logged_in' not in session:
        return redirect(url_for('login'))
    try:
        connection = create_db_connection()
        cursor = connection.cursor(dictionary=True)
        cursor.execute('SELECT * FROM sertifikat WHERE id = %s', (id,))
        sertifikat = cursor.fetchone()
        
        if sertifikat:
            return jsonify(sertifikat)
        else:
            return jsonify({'error': 'Sertifikat tidak ditemukan'}), 404
    except Exception as e:
        logging.error(f"Error fetching sertifikat details: {str(e)}")
        return jsonify({'error': 'Sertifikat tidak ditemukan'}), 404
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

@app.route('/add_sertifikat', methods=['POST'])
def add_sertifikat():
    if 'logged_in' not in session:
        return redirect(url_for('login'))
    
    judul = request.form['judul']
    nomor_sertifikat = request.form['nomor_sertifikat']
    nama_pemegang = request.form['nama_pemegang']
    tanggal_terbit = request.form['tanggal_terbit']
    tanggal_berakhir = request.form['tanggal_berakhir']
    file = request.files['file']
    
    file_path = None
    if file and file.filename:
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(file_path)
    
    try:
        connection = create_db_connection()
        cursor = connection.cursor()
        cursor.execute(
            'INSERT INTO sertifikat (judul, nomor_sertifikat, nama_pemegang, tanggal_terbit, tanggal_berakhir, dokumen) VALUES (%s, %s, %s, %s, %s, %s)',
            (judul, nomor_sertifikat, nama_pemegang, tanggal_terbit, tanggal_berakhir, file_path)
        )
        connection.commit()
        flash('Sertifikat berhasil ditambahkan', 'success')
    except Exception as e:
        flash(f"Error adding sertifikat: {str(e)}", 'danger')
        logging.error(f"Error adding sertifikat: {str(e)}")
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
    
    return redirect(url_for('sertifikat'))

@app.route('/delete_sertifikat/<int:id>', methods=['POST'])
def delete_sertifikat(id):
    if 'logged_in' not in session:
        return redirect(url_for('login'))

    try:
        connection = create_db_connection()
        cursor = connection.cursor()
        cursor.execute('DELETE FROM sertifikat WHERE id = %s', (id,))
        connection.commit()
        flash('Sertifikat berhasil dihapus', 'success')
    except Exception as e:
        flash(f"Error deleting sertifikat: {str(e)}", 'danger')
        logging.error(f"Error deleting sertifikat: {str(e)}")
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
    
    return redirect(url_for('sertifikat'))

@app.route('/edit_sertifikat/<int:id>', methods=['GET', 'POST'])
def edit_sertifikat(id):
    if 'logged_in' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        judul = request.form['judul']
        nomor_sertifikat = request.form['nomor_sertifikat']
        nama_pemegang = request.form['nama_pemegang']
        tanggal_terbit = request.form['tanggal_terbit']
        tanggal_berakhir = request.form['tanggal_berakhir']
        file = request.files['file']
        
        file_path = None
        if file and file.filename:
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            file.save(file_path)

        try:
            connection = create_db_connection()
            cursor = connection.cursor()
            cursor.execute(
                'UPDATE sertifikat SET judul = %s, nomor_sertifikat = %s, nama_pemegang = %s, tanggal_terbit = %s, tanggal_berakhir = %s, dokumen = %s WHERE id = %s',
                (judul, nomor_sertifikat, nama_pemegang, tanggal_terbit, tanggal_berakhir, file_path if file_path else request.form['existing_file'], id)
            )
            connection.commit()
            flash('Sertifikat berhasil diperbarui', 'success')
        except Exception as e:
            flash(f"Error updating sertifikat: {str(e)}", 'danger')
            logging.error(f"Error updating sertifikat: {str(e)}")
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()
        
        return redirect(url_for('sertifikat'))

    try:
        connection = create_db_connection()
        cursor = connection.cursor(dictionary=True)
        cursor.execute('SELECT * FROM sertifikat WHERE id = %s', (id,))
        sertifikat = cursor.fetchone()
        if sertifikat:
            return render_template('edit_sertifikat.html', sertifikat=sertifikat)
        else:
            return 'Sertifikat tidak ditemukan', 404
    except Exception as e:
        logging.error(f"Error fetching sertifikat details: {str(e)}")
        return 'Sertifikat tidak ditemukan', 404
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

if __name__ == '__main__':
    app.run(debug=True)
