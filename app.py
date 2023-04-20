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
        return render_template('register.html')

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
