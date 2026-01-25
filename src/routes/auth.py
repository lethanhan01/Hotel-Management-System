from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from forms.auth_form import LoginForm, RegisterForm
from models.customer import Customer
from extensions import supabase

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    form = LoginForm()
    if form.validate_on_submit():
        response = supabase.table('customer').select('*').eq('username', form.username.data).limit(1).execute()
        user_data = response.data[0] if response.data else None
        user = Customer.from_dict(user_data)
        if user is None or user.password != form.password.data:
            flash('Invalid username or password.', 'danger')
            return redirect(url_for('auth.login'))

        login_user(user, remember=form.remember_me.data)
        flash('Logged in successfully!', 'success')

        next_page = request.args.get('next')
        return redirect(next_page or url_for('main.index'))

    return render_template('auth/login.html', form=form)

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('auth.login'))

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.confirm_password.data:
            flash('Password confirmation does not match.', 'danger')
            return render_template('auth/register.html', form=form)

        existing = supabase.table('customer') \
            .select('customer_id') \
            .or_(f"username.eq.{form.username.data},email.eq.{form.email.data}") \
            .limit(1) \
            .execute()

        if existing.data:
            flash('Username or email already exists.', 'danger')
            return render_template('auth/register.html', form=form)

        insert_response = supabase.table('customer').insert({
            'username': form.username.data,
            'email': form.email.data,
            'password': form.password.data,
            'account_status': 1,
            'membership_level': 0
        }).execute()

        insert_error = getattr(insert_response, 'error', None)
        if insert_error:
            message = getattr(insert_error, 'message', None) or str(insert_error)
            flash(f'Registration failed: {message}', 'danger')
            return render_template('auth/register.html', form=form)

        flash('Registration successful! You can log in now.', 'success')
        return redirect(url_for('auth.login'))

    return render_template('auth/register.html', form=form)