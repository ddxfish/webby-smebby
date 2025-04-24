import sqlite3
import os
import random

def corrupt_database(db_path='uptime.db'):
    """Corrupts a SQLite database for testing recovery mechanisms."""
    
    if not os.path.exists(db_path):
        print(f"Database file {db_path} not found.")
        return
    
    confirm = input(f"This will corrupt your database at {db_path}. Type 'yes' to continue: ")
    if confirm.lower() != 'yes':
        print("Operation cancelled.")
        return
    
    corruption_type = input("Choose corruption type (1=drop table, 2=random bytes): ")
    
    try:
        if corruption_type == '1':
            # Drop a table
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.execute("DROP TABLE websites")
            conn.commit()
            conn.close()
            print("Dropped websites table. Database corrupted.")
            
        elif corruption_type == '2':
            # Write random bytes in the middle of the file
            with open(db_path, 'r+b') as f:
                filesize = os.path.getsize(db_path)
                if filesize > 1000:
                    position = random.randint(1000, filesize - 100)
                    f.seek(position)
                    random_bytes = bytes([random.randint(0, 255) for _ in range(50)])
                    f.write(random_bytes)
                    print(f"Wrote random bytes at position {position}. Database corrupted.")
                else:
                    print("File too small to safely corrupt.")
        else:
            print("Invalid option selected.")
            
    except Exception as e:
        print(f"Error corrupting database: {str(e)}")

if __name__ == "__main__":
    corrupt_database()