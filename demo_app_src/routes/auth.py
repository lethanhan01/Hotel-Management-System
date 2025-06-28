from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from forms.auth_form import LoginForm, RegisterForm
from models.customer import Customer
from extensions import db

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    form = LoginForm()
    if form.validate_on_submit():
        user = Customer.query.filter_by(username=form.username.data).first()
        if user is None or user.password != form.password.data:
            flash('Tên đăng nhập hoặc mật khẩu không hợp lệ.', 'danger')
            return redirect(url_for('auth.login'))

        login_user(user, remember=form.remember_me.data)
        flash('Đăng nhập thành công!', 'success')

        next_page = request.args.get('next')
        return redirect(next_page or url_for('main.index'))

    return render_template('auth/login.html', form=form)

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Bạn đã đăng xuất.', 'info')
    return redirect(url_for('auth.login'))

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.confirm_password.data:
            flash('Mật khẩu xác nhận không khớp.', 'danger')
            return render_template('auth/register.html', form=form)

        existing_user = Customer.query.filter_by(username=form.username.data).first()
        if existing_user:
            flash('Tên đăng nhập đã tồn tại.', 'danger')
            return render_template('auth/register.html', form=form)

        new_customer = Customer(
            username=form.username.data,
            email=form.email.data,
            password=form.password.data
        )
        db.session.add(new_customer)
        db.session.commit()

        flash('Đăng ký thành công! Bạn có thể đăng nhập ngay bây giờ.', 'success')
        return redirect(url_for('auth.login'))

    return render_template('auth/register.html', form=form)