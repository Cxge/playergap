from flaskfantasy import app
import os

if __name__ == '__main__':
    app.run(debug=(os.environ.get('DEBUG_VALUE') == 'True'))