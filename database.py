import sqlite3
from datetime import datetime

class Database:
    def __init__(self, db_file='uptime.db'):
        self.db_file = db_file
        self.init_db()
    
    def init_db(self):
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS websites (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            url TEXT NOT NULL,
            check_string TEXT,
            last_check TIMESTAMP,
            last_seen TIMESTAMP,
            last_fail TIMESTAMP,
            status TEXT,
            status_code TEXT
        )
        ''')
        
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            website_id INTEGER,
            timestamp TIMESTAMP,
            status TEXT,
            status_code TEXT,
            FOREIGN KEY (website_id) REFERENCES websites (id)
        )
        ''')
        
        conn.commit()
        conn.close()
    
    def get_websites(self):
        conn = sqlite3.connect(self.db_file)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM websites')
        websites = [dict(row) for row in cursor.fetchall()]
        
        conn.close()
        return websites
    
    def get_website(self, website_id):
        """Get a single website by ID"""
        conn = sqlite3.connect(self.db_file)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM websites WHERE id = ?', (website_id,))
        website = cursor.fetchone()
        
        conn.close()
        return dict(website) if website else None
    
    def add_website(self, name, url, check_string=''):
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        
        cursor.execute('''
        INSERT INTO websites (name, url, check_string)
        VALUES (?, ?, ?)
        ''', (name, url, check_string))
        
        conn.commit()
        conn.close()
    
    def update_website(self, website_id, name, url, check_string=''):
        """Update a website's information"""
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        
        cursor.execute('''
        UPDATE websites 
        SET name = ?, url = ?, check_string = ?
        WHERE id = ?
        ''', (name, url, check_string, website_id))
        
        conn.commit()
        conn.close()
    
    def remove_website(self, website_id):
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        
        cursor.execute('DELETE FROM websites WHERE id = ?', (website_id,))
        cursor.execute('DELETE FROM logs WHERE website_id = ?', (website_id,))
        
        conn.commit()
        conn.close()
    
    def update_website_status(self, website_id, status, status_code):
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        
        cursor.execute('''
        UPDATE websites 
        SET last_check = ?, status = ?, status_code = ?
        WHERE id = ?
        ''', (now, status, status_code, website_id))
        
        if status == 'OK':
            cursor.execute('UPDATE websites SET last_seen = ? WHERE id = ?', (now, website_id))
        else:
            cursor.execute('UPDATE websites SET last_fail = ? WHERE id = ?', (now, website_id))
        
        cursor.execute('''
        INSERT INTO logs (website_id, timestamp, status, status_code)
        VALUES (?, ?, ?, ?)
        ''', (website_id, now, status, status_code))
        
        conn.commit()
        conn.close()
    
    def get_last_failure(self):
        conn = sqlite3.connect(self.db_file)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('''
        SELECT l.*, w.name, w.url 
        FROM logs l
        JOIN websites w ON l.website_id = w.id
        WHERE l.status != 'OK'
        ORDER BY l.timestamp DESC
        LIMIT 1
        ''')
        
        result = cursor.fetchone()
        conn.close()
        
        return dict(result) if result else None
    
    def import_from_csv(self, csv_file):
        import csv
        
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        
        try:
            with open(csv_file, 'r') as f:
                reader = csv.reader(f)
                for row in reader:
                    if len(row) >= 2:
                        name, url = row[0], row[1]
                        check_string = row[2] if len(row) > 2 else ''
                        
                        cursor.execute('SELECT id FROM websites WHERE url = ?', (url,))
                        if not cursor.fetchone():
                            cursor.execute('''
                            INSERT INTO websites (name, url, check_string)
                            VALUES (?, ?, ?)
                            ''', (name, url, check_string))
            
            conn.commit()
            return True
        except Exception:
            return False
        finally:
            conn.close()
            
    def export_to_csv(self, csv_file):
        import csv
        
        conn = sqlite3.connect(self.db_file)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        try:
            cursor.execute('SELECT name, url, check_string FROM websites')
            websites = cursor.fetchall()
            
            with open(csv_file, 'w', newline='') as f:
                writer = csv.writer(f)
                for website in websites:
                    writer.writerow([website['name'], website['url'], website['check_string']])
            
            return True
        except Exception:
            return False
        finally:
            conn.close()