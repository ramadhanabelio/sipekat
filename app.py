from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

admins = [
    {'username': 'admin1', 'password': 'password1'},
    {'username': 'admin2', 'password': 'password2'}
]

sertifikat_list = [
    {'id': 1, 'judul': 'Sertifikat 1', 'nomor_sertifikat': '001', 'nama_pemegang': 'John Doe'},
    {'id': 2, 'judul': 'Sertifikat 2', 'nomor_sertifikat': '002', 'nama_pemegang': 'Jane Doe'}
]

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        for admin in admins:
            if admin['username'] == username and admin['password'] == password:
                return redirect(url_for('dashboard'))
        
        return render_template('login.html')
    
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

@app.route('/sertifikat')
def sertifikat():
    return render_template('sertifikat.html', sertifikat_list=sertifikat_list)

@app.route('/sertifikat/<int:id>')
def detail_sertifikat(id):
    sertifikat = next((sert for sert in sertifikat_list if sert['id'] == id), None)
    if sertifikat:
        return render_template('detail_sertifikat.html', sertifikat=sertifikat)
    else:
        return 'Sertifikat tidak ditemukan', 404

if __name__ == '__main__':
    app.run(debug=True)
