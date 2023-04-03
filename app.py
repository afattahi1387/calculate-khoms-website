from flask import Flask, flash, render_template, request, redirect, url_for
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

    if request.args.get('edit-have'):
        show_form = 'edit_have'
    else:
        show_form = 'add_have'

    return render_template('index.html', haves = haves, show_form = show_form, user_id = current_user.get_id())

@app.route('/add-have-for-user', methods = ['POST'])
@login_required
def add_have_for_user():
    if not request.form['name'] or request.form['type'] == 'is_null' or not request.form['total_price']:
        return redirect('/')
    
    if request.form['type'] == 'commodity' and not request.form['remaining_amount']:
        return redirect('/')

    have_information = {}
    have_information['name'] = request.form['name']
    have_information['type'] = request.form['type']
    have_information['user_id'] = request.form['user_id']
    have_information['total_price'] = request.form['total_price']
    if not request.form['remaining_amount']:
        have_information['remaining_amount'] = None
    else:
        have_information['remaining_amount'] = request.form['remaining_amount']

    functions.insert_have(have_information)
    flash('داشته شما با موفقیت افزوده شد.', 'success')
    return redirect('/')

@app.route('/delete-have/<int:have_id>')
@login_required
def delete_have_page(have_id):
    functions.delete_have(have_id)
    flash('داشته شما با موفقیت حذف شد.', 'success')
    return redirect('/')

@app.route('/login', methods = ['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect('/')

    if request.method == 'POST':
        email_or_username = request.form['email_or_username']
        password = request.form['password']
        if not email_or_username or not password:
            flash('لطفا ایمیل یا نام کاربری یا رمز عبور خود را به درستی وارد کنید', 'danger')
            return redirect(url_for('login'))
        user_information = functions.user_login_settings(email_or_username, password)
        if user_information:
            user = functions.User(user_information[0])
            login_user(user)
            flash('شما وارد حساب کاربری خود شدید.', 'success')
            return redirect('/')
        else:
            flash('لطفا مجددا تلاش کنید.', 'danger')
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
    flash('شما از حساب کاربری خود خارج شدید.', 'success')
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
