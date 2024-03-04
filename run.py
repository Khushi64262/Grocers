from MAD1 import app
from MAD1.database import db

if __name__ == '__main__':
    with app.app_context():
        db.create_all() 
        print("hello")
        app.run(debug=True)
