from flask import Flask, render_template, request, redirect, url_for
from flask_login import LoginManager, login_required, \
                                login_user, logout_user, current_user
import config
import functions

app = Flask(__name__)

app.config.update(SECRET_KEY = config.SECRET_KEY)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

users = [functions.User(userRow[0]) for userRow in functions.get_all_users()]

@app.route('/')
def home():
    haves = {}
    haveId = 0
    havesRow = functions.get_user_haves(current_user.get_id())
    for have in havesRow:
        haveId += 1
        haves[str(haveId)] = have
    return render_template('index.html', haves = haves)

@app.route('/login', methods = ['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect('/')

    if request.method == 'POST':
        email_or_username = request.form['email_or_username']
        password = request.form['password']
        if not email_or_username or not password:
            return redirect(url_for('login'))
        user_information = functions.user_login_settings(email_or_username, password)
        if user_information:
            user = functions.User(user_information[0])
            login_user(user)
            return redirect('/')
        else:
            return redirect('/login')
    else:
        return render_template('login.html')

@login_manager.user_loader
def load_user(user_id):
    return functions.User(user_id)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
