import os
import sqlite3

# Delete the old database
if os.path.exists('app.db'):
    os.remove('app.db')
    print("Old database deleted")

# Create a new empty database
conn = sqlite3.connect('app.db')
conn.close()
print("New database created")

print("Database fixed! Now run: python app.py")
