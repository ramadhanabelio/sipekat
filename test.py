import unittest
from app import app
import sqlite3

class FlaskAppTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # Configure app for testing
        app.config['TESTING'] = True
        app.config['DATABASE'] = 'sqlite:///:memory:'
        cls.client = app.test_client()

        # Create an in-memory SQLite database
        cls.connection = sqlite3.connect(':memory:')
        cls.cursor = cls.connection.cursor()

        # Create tables and insert test data
        cls.create_tables()
        cls.insert_test_data()

    @classmethod
    def tearDownClass(cls):
        cls.connection.close()

    @classmethod
    def create_tables(cls):
        cls.cursor.execute('''
            CREATE TABLE admin (
                username TEXT PRIMARY KEY,
                password TEXT
            )
        ''')
        cls.cursor.execute('''
            CREATE TABLE sertifikat (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                judul TEXT,
                nomor_sertifikat TEXT,
                nama_pemegang TEXT,
                tanggal_terbit DATE,
                tanggal_berakhir DATE,
                dokumen TEXT
            )
        ''')
        cls.connection.commit()

    @classmethod
    def insert_test_data(cls):
        cls.cursor.execute('''
            INSERT INTO admin (username, password) VALUES ('admin', 'admin')
        ''')
        cls.connection.commit()

    def test_login_success(self):
        response = self.client.post('/', data=dict(username='admin', password='admin'), follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Dashboard', response.data)

    def test_login_failure(self):
        response = self.client.post('/', data=dict(username='wrong', password='wrong'), follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Invalid username or password', response.data)

    def test_logout(self):
        with self.client:
            with self.client.session_transaction() as sess:
                sess['logged_in'] = True

            response = self.client.get('/logout', follow_redirects=True)
            self.assertEqual(response.status_code, 200)
            self.assertIn(b'Login', response.data)
            self.assertNotIn('logged_in', sess)

    def test_dashboard_access(self):
        with self.client:
            with self.client.session_transaction() as sess:
                sess['logged_in'] = True

            response = self.client.get('/dashboard')
            self.assertEqual(response.status_code, 200)
            self.assertIn(b'Dashboard', response.data)

    def test_dashboard_redirect_if_not_logged_in(self):
        response = self.client.get('/dashboard', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Login', response.data)

    def test_sertifikat_list(self):
        with self.client:
            with self.client.session_transaction() as sess:
                sess['logged_in'] = True

            response = self.client.get('/sertifikat')
            self.assertEqual(response.status_code, 200)
            self.assertIn(b'Sertifikat', response.data)

    def test_detail_sertifikat(self):
        with self.client:
            with self.client.session_transaction() as sess:
                sess['logged_in'] = True

            response = self.client.get('/sertifikat/1')
            self.assertEqual(response.status_code, 200)
            self.assertIn(b'Sertifikat', response.data)

    def test_add_sertifikat(self):
        with self.client:
            with self.client.session_transaction() as sess:
                sess['logged_in'] = True

            data = {
                'judul': 'New Sertifikat',
                'nomor_sertifikat': '67890',
                'nama_pemegang': 'Jane Doe',
                'tanggal_terbit': '2023-01-01',
                'tanggal_berakhir': '2024-01-01'
            }
            response = self.client.post('/add_sertifikat', data=data, follow_redirects=True)
            self.assertEqual(response.status_code, 200)
            self.assertIn(b'Sertifikat berhasil ditambahkan', response.data)

    def test_delete_sertifikat(self):
        with self.client:
            with self.client.session_transaction() as sess:
                sess['logged_in'] = True

            response = self.client.post('/delete_sertifikat/1', follow_redirects=True)
            self.assertEqual(response.status_code, 200)
            self.assertIn(b'Sertifikat berhasil dihapus', response.data)

    def test_edit_sertifikat(self):
        with self.client:
            with self.client.session_transaction() as sess:
                sess['logged_in'] = True

            response = self.client.get('/edit_sertifikat/1')
            self.assertEqual(response.status_code, 200)
            self.assertIn(b'Edit Sertifikat', response.data)

            data = {
                'judul': 'Updated Sertifikat',
                'nomor_sertifikat': '67890',
                'nama_pemegang': 'Jane Doe',
                'tanggal_terbit': '2023-01-01',
                'tanggal_berakhir': '2024-01-01'
            }
            response = self.client.post('/edit_sertifikat/1', data=data, follow_redirects=True)
            self.assertEqual(response.status_code, 200)
            self.assertIn(b'Sertifikat berhasil diperbarui', response.data)

if __name__ == '__main__':
    unittest.main()
