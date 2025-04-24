import sqlite3
from datetime import datetime
import os

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

    def get_current_status(self):
        """Get the current overall status of all websites"""
        conn = sqlite3.connect(self.db_file)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Check if any website is currently failing
        cursor.execute('SELECT id, name, url, status, status_code, last_fail FROM websites WHERE status != "OK"')
        failing_websites = cursor.fetchall()
        
        if failing_websites:
            # Get the most recently failing website
            most_recent = None
            latest_time = None
            
            for website in failing_websites:
                if website['last_fail']:
                    site_time = datetime.strptime(website['last_fail'], '%Y-%m-%d %H:%M:%S')
                    if latest_time is None or site_time > latest_time:
                        latest_time = site_time
                        most_recent = website
            
            conn.close()
            return dict(most_recent) if most_recent else dict(failing_websites[0])
        else:
            conn.close()
            return None

    def prune_old_logs(self, days=30):
        """Delete logs older than specified days"""
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        
        # Calculate the date threshold
        from datetime import datetime, timedelta
        threshold_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d %H:%M:%S')
        
        try:
            cursor.execute('DELETE FROM logs WHERE timestamp < ?', (threshold_date,))
            deleted_count = cursor.rowcount
            conn.commit()
            return deleted_count
        except Exception as e:
            print(f"Error pruning logs: {str(e)}")
            return 0
        finally:
            conn.close()


    def backup_websites(self, backup_file='websites.csv'):
        """Backup all websites to CSV file for disaster recovery"""
        try:
            success = self.export_to_csv(backup_file)
            if success:
                # Create a timestamp file to record last successful backup
                with open(f"{backup_file}.timestamp", "w") as f:
                    f.write(datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
            return success
        except Exception as e:
            print(f"Error backing up websites: {str(e)}")
            return False
        
    def verify_database(self):
        """Verify database integrity. Returns True if database is valid, False otherwise."""
        # Check if file exists and has content
        if not os.path.exists(self.db_file) or os.path.getsize(self.db_file) == 0:
            print(f"Database file missing or empty: {self.db_file}")
            return False
            
        try:
            conn = sqlite3.connect(self.db_file)
            cursor = conn.cursor()
            
            # Check if the websites table exists
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='websites'")
            if not cursor.fetchone():
                print("Table 'websites' does not exist")
                conn.close()
                return False
            
            # Try to read from the websites table
            cursor.execute('SELECT COUNT(*) FROM websites')
            cursor.fetchone()
            
            # Check integrity
            cursor.execute('PRAGMA integrity_check')
            result = cursor.fetchone()[0]
            
            conn.close()
            return result == 'ok'
        except sqlite3.Error as e:
            print(f"Database verification failed: {e}")
            return False

    def generate_status_report(self, output_file='/tmp/webby_status.txt'):
        """Generate a machine-readable status report file"""
        try:
            websites = self.get_websites()
            with open(output_file, 'w') as f:
                # Write header
                f.write("id|name|url|status|code|last_seen|last_fail\n")
                
                # Write each website status
                for site in websites:
                    f.write(f"{site.get('id', '')}|{site.get('name', '')}|{site.get('url', '')}|"
                            f"{site.get('status', '')}|{site.get('status_code', '')}|"
                            f"{site.get('last_seen', '')}|{site.get('last_fail', '')}\n")
            return True
        except Exception as e:
            print(f"Error generating status report: {str(e)}")
            return False