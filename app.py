from flask import Flask, flash, render_template, \
                                request, redirect, url_for, session
from flask_login import LoginManager, login_required, \
                                login_user, logout_user, current_user
from flask_mail import Mail, Message
import config
import functions

import socket
socket.getaddrinfo('localhost', config.MAIL_PORT)

app = Flask(__name__)

app.config['MAIL_SERVER'] = 'sandbox.smtp.mailtrap.io'
app.config['MAIL_PORT'] = config.MAIL_PORT
app.config['MAIL_USERNAME'] = '5db6253802bb7d'
app.config['MAIL_PASSWORD'] = '586933c026e705'
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False

mail = Mail(app)

app.config.update(SECRET_KEY = config.SECRET_KEY)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

users = [functions.User(userRow[0]) for userRow in functions.get_all_users()]

@app.route('/')
def home():
    if not current_user.is_authenticated:
        flash('ابتدا باید وارد شوید.', 'primary')
        return redirect(url_for('login'))

    haves = {}
    haveId = 0
    havesRow = functions.get_user_haves(current_user.get_id())
    for have in havesRow:
        haveId += 1
        have = list(have)
        have.append(functions.add_cama_in_number(functions.calculate_have_khoms(have[0])))
        if have[2] == 'commodity':
            have.append(functions.add_cama_in_number(have[4] * have[5]))
        else:
            have.append(functions.add_cama_in_number(have[4]))

        have[4] = functions.add_cama_in_number(have[4])

        if have[5]:
            have[5] = functions.add_cama_in_number(have[5])
        haves[str(haveId)] = have

    if request.args.get('edit-have'):
        show_form = 'edit_have'
        have_row_for_edit = functions.get_one_have(request.args.get('edit-have'))
    else:
        show_form = 'add_have'
        have_row_for_edit = None

    return render_template('index.html',
    haves = haves,
    show_form = show_form,
    user_id = current_user.get_id(),
    user_name = functions.get_one_user(current_user.get_id())[1],
    have_row_for_edit = have_row_for_edit,
    total_prices = functions.add_cama_in_number(functions.calculate_total_prices(current_user.get_id())),
    total_khoms = functions.add_cama_in_number(functions.calculate_khoms_of_user_haves(current_user.get_id())),
    number_of_haves = functions.add_cama_in_number(functions.count_user_haves(current_user.get_id())),
    number_of_commodities = functions.add_cama_in_number(functions.count_user_haves(current_user.get_id(), 'commodity')),
    number_of_moneys = functions.add_cama_in_number(functions.count_user_haves(current_user.get_id(), 'money')))

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

@app.route('/update-have/<int:have_id>', methods = ['POST'])
@login_required
def update_have_page(have_id):
    if not request.form['name'] or not request.form['total_price']:
        flash('لطفا اطلاعات خود را به صورت کامل وارد کنید.', 'danger')
        return redirect('/')

    if request.form['type'] == 'commodity' and not request.form['remaining_amount']:
        flash('لطفا اطلاعات خود را به صورت کامل وارد کنید.', 'danger')
        return redirect('/')

    new_have_row = {}
    new_have_row['name'] = request.form['name']
    new_have_row['type'] = request.form['type']
    new_have_row['user_id'] = request.form['user_id']
    new_have_row['total_price'] = request.form['total_price']
    if new_have_row['type'] == 'commodity' and request.form['remaining_amount']:
        new_have_row['remaining_amount'] = request.form['remaining_amount']
    else:
        new_have_row['remaining_amount'] = None

    functions.update_have(have_id, new_have_row)
    flash('ویرایش داشته شما با موفقیت انجام شد.', 'success')
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
            if email_or_username:
                session['login_page_email_or_username'] = email_or_username
            
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
        if 'login_page_email_or_username' in session:
            email_or_username = session['login_page_email_or_username']
            session.pop('login_page_email_or_username')
        else:
            email_or_username = ''
        return render_template('login.html', old_email_or_username = email_or_username)

@app.route('/register', methods = ['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect('/')
    
    if request.method == 'POST':
        required_fields = {
            'firstname' : 'نام',
            'lastname' : 'نام خانوادگی',
            'email' : 'ایمیل',
            'username' : 'نام کاربری',
            'password' : 'رمز عبور',
            'password_confirm' : 'تکرار رمز عبور'
        }
        redirect_to_register = False
        for k, v in required_fields.items():
            if not request.form[k]:
                flash('فیلد ' + v + ' شما خالی می باشد. لطفا آن را پر کنید.', 'danger')
                redirect_to_register = True

        if request.form['password'] != request.form['password_confirm']:
            flash('رمز عبور و تکرار آن با هم برابر نیستند.', 'danger')
            redirect_to_register = True

        user_information = functions.user_exists(request.form['email'], request.form['username'], request.form['password'])

        if user_information:
            flash_message = 'اطلاعات وارد شده تکراری می باشد. لطفا فیلد های '
            counter = 0
            for fa in user_information:
                if counter == 0:
                    flash_message += fa
                    counter = 1
                else:
                    flash_message += ' - ' + fa

            flash_message += ' را عوض کنید.'
            flash(flash_message, 'danger')
            redirect_to_register = True

        if redirect_to_register:
            if request.form['firstname']:
                session['register_page_firstname'] = request.form['firstname']

            if request.form['lastname']:
                session['register_page_lastname'] = request.form['lastname']

            if request.form['email']:
                session['register_page_email'] = request.form['email']

            if request.form['username']:
                session['register_page_username'] = request.form['username']

            return redirect(url_for('register'))
        
        last_row_id = functions.user_register({
            'first_name' : request.form['firstname'],
            'last_name' : request.form['lastname'],
            'email' : request.form['email'],
            'username' : request.form['username'],
            'password' : request.form['password']
        })

        user = functions.User(last_row_id)
        login_user(user)
        flash('شما ثبت نام شده و وارد حساب کاربری خود شدید.', 'success')
        return redirect('/')
    else:
        fields_value = {}
        for ch in ['firstname', 'lastname', 'email', 'username']:
            if 'register_page_' + ch in session:
                fields_value[ch] = session['register_page_' + ch]
                session.pop('register_page_' + ch)

        return render_template('register.html', fields_value = fields_value)

@app.route('/forget-password', methods = ['GET', 'POST'])
def forget_password_page():
    if current_user.is_authenticated:
        return redirect('/')
    
    if request.method == 'POST':
        email = request.form['email']
        find_user = functions.get_user_with_email(email)
        if not find_user:
            flash('کاربری یافت نشد. لطفا مجددا تلاش کنید.', 'danger')
            return redirect('/forget-password?show-flashed-messages=1')
        else:
            change_password_url = functions.get_change_password_url(find_user[0])
            message_text = f'''با سلام. روی لینک زیر بزنید تا به صفحه تعویض لینک هدایت شوید.
            <br><br><br>
            <a href="{change_password_url}" style="text-decoration: none;">{change_password_url}</a>'''
            msg = Message('لینک عوض کردن رمز عبور', sender = config.FORGET_PASSWORD_MAIL_SENDER, recipients = [email])
            msg.body = message_text
            mail.send(msg)
            flash('ایمیل برای شما با موفقیت ارسال شد. لطفا آن را بخوانید و طبق آن عمل کنید.', 'success')
            return redirect('/forget-password?show-flashed-messages=1')
    else:
        if request.args.get('show-flashed-messages'):
            show_flashed_messages = True
        else:
            show_flashed_messages = False
        return render_template('forget_password_page.html', show_flashed_messages = show_flashed_messages)

@app.route('/change-password/<user_id>', methods = ['GET', 'POST'])
def change_password_page(user_id):
    if current_user.is_authenticated:
        return redirect('/')

    if request.method == 'POST':
        if not request.form['password'] and not request.form['password_confirm']:
            flash('لطفا هر دو کارد زیر را به صورت کامل وارد نمایید.', 'danger')
            return redirect(f'/change-password/{user_id}')
        
        if request.form['password'] != request.form['password_confirm']:
            flash('لطفا تکرار رمز عبور جدید را دقیقا برابر با رمز عبور جدید وارد کنید.', 'danger')
            return redirect(f'/change-password/{user_id}')

        functions.change_password(user_id, request.form['password'])
        user = functions.User(user_id)
        login_user(user)
        flash('شما وارد حساب کاربری خود شدید.', 'success')
        return redirect('/')
    else:
        return render_template('change_password_page.html')

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
    print(functions.get_change_password_url(8))
    app.run(debug=True)
