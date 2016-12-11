from flask import Flask, request, flash, redirect, render_template, url_for
from flask.ext.login import LoginManager, login_user, logout_user, current_user, login_required
import common
from common import User, Settings, ZoneInfo, EventLog
import sys
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

app = Flask(__name__)

# Create the database engine.
engine = create_engine(common.SQLITE_URL) #TODO: Might be good to have an actual config file...
DBSession = sessionmaker(bind=engine)
db_session = DBSession()

# Configure LoginManager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(id):
    return db_session.query(User).get(int(id))

@app.route('/')
@login_required
def index():
    zones = db_session.query(ZoneInfo).all()
    return render_template('index.html', zones=zones)

@app.route('/settings')
@login_required
def settings():
    settings = db_session.query(Settings).one()
    return render_template('settings.html', settings=settings)

@app.route('/eventlog')
@login_required
def eventlog():
    events = db_session.query(ZoneInfo).join(EventLog).add_columns(ZoneInfo.name, EventLog.type, EventLog.start_time, EventLog.end_time) 
    return render_template('eventlog.html', events=events)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        if current_user.is_authenticated:
            return redirect(url_for('index'))
        else:
            return render_template('login.html')
    else:
        username = request.form['username']
        password = request.form['password']
        debug_print('Checking username and password: username \'' + username + '\', password \'' + password + '\'')
        registered_user = db_session.query(User).filter_by(name=username,password=password).first()
        if registered_user is None:
            debug_print('Username or password is invalid')
            flash('Username or Password is invalid', 'error')
            return redirect(url_for('login'))
        else:
            debug_print('Username and password accepted')
            login_user(registered_user)
            return redirect(request.args.get('next') or url_for('index'))

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))

def debug_print(strMessage):
    if common.DEBUG:
        print(strMessage, file = sys.stderr)

if __name__ == '__main__':
    # TODO: Change this stuff before deploying
    app.secret_key = 'super secret key'
    app.run(host='0.0.0.0', debug=True)
