from flask import Flask, render_template, redirect, url_for, request, flash, jsonify, abort, g
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, FileField, BooleanField, TextAreaField, DateField, TimeField, SelectField
from wtforms.validators import DataRequired, Email
from werkzeug.security import generate_password_hash, check_password_hash
import os
from models import Location, Reservation  # モデルのインポート
from forms import AdminForm, ReservationForm 
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import relationship
import logging
from datetime import datetime, date, time
from itertools import groupby
from operator import attrgetter
from wtforms.validators import DataRequired, ValidationError, Optional


# Cloud SQL接続情報
INSTANCE_CONNECTION_NAME = "rare-chiller-406009:us-west1:flask"
DB_USER = "root"
DB_PASSWORD = "test"
DB_NAME = "project-c"
socket_dir = "/cloudsql"


logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///your_database.db'
# app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+pymysql://{DB_USER}:{DB_PASSWORD}@127.0.0.1:3306/{DB_NAME}'
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # 不要な警告を抑制
db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# Location model definition
class Location(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    location_name = db.Column(db.String(255), nullable=False)
    domain = db.Column(db.String(255), nullable=False)
    floor = db.Column(db.Integer, nullable=False)

# User model definition
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False)
    username = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)

class Reservation(db.Model):
    __tablename__ = 'reservation'
    id = db.Column(db.Integer, primary_key=True)
    location_id = db.Column(db.Integer, db.ForeignKey('location.id'), nullable=False)
    title = db.Column(db.String(255), nullable=True)
    start = db.Column(db.DateTime, nullable=False)
    end = db.Column(db.DateTime, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    responsible_user = db.Column(db.String(255), nullable=False)
    domain = db.Column(db.String(255), nullable=False)

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class ReservationForm(FlaskForm):
    start_date = DateField('開始日', format='%Y-%m-%d', validators=[DataRequired()])
    start_time = TimeField('開始時間', format='%H:%M', validators=[Optional()])
    end_date = DateField('終了日', format='%Y-%m-%d', validators=[Optional()])
    end_time = TimeField('終了時間', format='%H:%M', validators=[Optional()])
    is_all_day = BooleanField('終日予約')
    title = StringField('予約タイトル', validators=[DataRequired()])
    submit = SubmitField('予約する')

    # バリデーションの追加
    def validate_end_date(form, field):
        if form.is_all_day.data and field.data:
            raise ValidationError('終日予約の場合、終了日は指定不要です。')

    def validate_end_time(form, field):
        if form.is_all_day.data and field.data:
            raise ValidationError('終日予約の場合、終了時間は指定不要です。')


# ログアウトフォームのクラス
class LogoutForm(FlaskForm):
    submit = SubmitField('ログアウト')

class SettingsForm(FlaskForm):
    username = StringField('New Username')
    new_password = PasswordField('New Password')
    current_password = PasswordField('Current Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password')
    icon = FileField('Upload Icon')
    dark_mode = BooleanField('Dark Mode')
    submit = SubmitField('Save Changes')

# ロケーション登録フォーム
class LocationForm(FlaskForm):
    location_name = StringField('Location Name', validators=[DataRequired()])
    floor = SelectField('Floor', choices=[(str(i), str(i)) for i in range(1, 11)])
    submit = SubmitField('Submit')

class AdminForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    username = StringField('Username', validators=[DataRequired()])
    submit = SubmitField('Add Submit')

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# ログインしていない場合はログインページにリダイレクト
@app.before_request
def before_request():
    if not current_user.is_authenticated and request.endpoint not in ['login', 'register', 'static']:
        flash('ログインが必要です。', 'danger')
        return redirect(url_for('login'))

# ログインページ
@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()

    if request.method == 'POST' and form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        user = User.query.filter_by(username=username).first()

        logging.debug(f'Attempting to log in user: {username}')

        if user and check_password_hash(user.password, password):
            login_user(user)
            flash('ログインに成功しました。', 'success')
            logging.debug('Login successful')
            return redirect(url_for('index'))
        else:
            flash('ユーザー名またはパスワードが正しくありません。', 'danger')
            logging.warning('Login failed: Invalid username or password')
    return render_template('login.html', form=form)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        username = request.form['username']
        password = request.form['password']

        # ユーザー名またはメールアドレスが既に使用されていないか確認
        existing_user = User.query.filter((User.email == email) | (User.username == username)).first()
        if existing_user:
            return "ユーザー名またはメールアドレスはすでに存在します。別のものを選択してください。"

        # 'pbkdf2_sha256' をハッシュメソッドとして使用して新しいユーザーを作成
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
        new_user = User(email=email, username=username, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()

        login_user(new_user)
        return redirect('/')

    return render_template('register.html')

# ログアウト
@app.route('/logout', methods=['POST'])
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

# サンプルデータ
buttons_data = [
    {"label": "予約画面", "url": "/reservation"},
    {"label": "連絡画面", "url": "/contact"},
    {"label": "位置情報画面", "url": "/map"},
    {"label": "設定画面", "url": "/settings"},
    {"label": "Admin", "url": "/add_admin"},
    {"label": "AddLocation", "url": "/add_location"}
]

# ホームページ
@app.route('/')
@login_required
def index():
    login_status = None
    logout_form = LogoutForm()  # LogoutForm をインスタンス化

    # ログインに成功した場合、メッセージを設定
    if current_user.is_authenticated:
        login_status = 'ログインに成功しました。'

    # ログアウトボタンがクリックされた場合
    if logout_form.validate_on_submit():
        logout_user()
        return redirect(url_for('index'))

    return render_template('index.html', buttons=buttons_data, login_status=login_status, logout_form=logout_form)

# ロケーション登録ページ
@app.route('/add_location', methods=['GET', 'POST'])
@login_required
def add_location():
    # アクセス権限の確認
    if not current_user.is_admin:
        flash('このページにアクセスする権限がありません。', 'danger')
        return redirect(url_for('index'))

    form = LocationForm()

    if form.validate_on_submit():
        # フォームからデータを取得してデータベースに追加
        location_name = form.location_name.data
        floor = form.floor.data

        # ユーザーのメールアドレスからドメインを抽出
        user_domain = current_user.email.split('@')[-1] if '@' in current_user.email else None

        # ドメインごとに既存のロケーションを確認
        existing_location = Location.query.filter_by(domain=user_domain, location_name=location_name, floor=floor).first()

        if existing_location:
            flash('同じドメイン、同じ階に既に存在するロケーション名です。別の名前または階を使用してください。', 'danger')
        else:
            new_location = Location(location_name=location_name, domain=user_domain, floor=floor)
            db.session.add(new_location)

            try:
                db.session.commit()
                flash('ロケーションが正常に追加されました。', 'success')
                
                # データベースの変更をコミットした後、show_locations ページにリダイレクト
                return redirect(url_for('show_locations'))
            except SQLAlchemyError as e:
                db.session.rollback()
                flash(f'データベースのエラーが発生しました: {str(e)}', 'danger')
            finally:
                db.session.close()

    return render_template('add_location.html', form=form)

# ロケーション表示ページ
@app.route('/locations')
@login_required
def show_locations():
    # ユーザーのメールアドレスからドメインを取得
    user_domain = current_user.email.split('@')[-1] if '@' in current_user.email else None

    # データベースから対応するドメインのロケーション情報を取得
    if user_domain:
        locations = Location.query.filter_by(domain=user_domain).order_by(Location.floor, Location.location_name).all()
    else:
        locations = []

    # グループ化された辞書を作成（キーは階層）
    grouped_locations = {floor: list(group) for floor, group in groupby(locations, key=attrgetter('floor'))}

    return render_template('pages.html', grouped_locations=grouped_locations)

@app.route('/reservation')
@login_required
def show_pages():
    # ユーザーのメールアドレスからドメインを取得
    user_domain = current_user.email.split('@')[-1] if '@' in current_user.email else None

    # データベースから対応するドメインのロケーション情報を取得
    if user_domain:
        locations = Location.query.filter_by(domain=user_domain).order_by(Location.floor, Location.location_name).all()
    else:
        locations = []

    # グループ化された辞書を作成（キーは階層）
    grouped_locations = {floor: list(group) for floor, group in groupby(locations, key=attrgetter('floor'))}

    return render_template('pages.html', grouped_locations=grouped_locations)

@app.route('/map')
@login_required
def map():
    return render_template('map.html')


# 設定ページ
@app.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    form = SettingsForm()

    if request.method == 'POST' and form.validate_on_submit():
        current_password = form.current_password.data
        new_password = form.new_password.data
        confirm_password = form.confirm_password.data
        username = form.username.data

        # 現在のパスワードの確認
        if not check_password_hash(current_user.password, current_password):
            # 現在のパスワードが間違っている場合の処理
            error_message = 'パスワードが間違っています'
            flash(error_message, 'danger') 
            return render_template('settings.html', form=form, error=error_message)

        # 新しいパスワードと確認が一致するかチェックする
        if new_password != confirm_password:
            # パスワードが不一致の場合
            error_message = '新しいパスワードと確認パスワードが一致しません'
            flash(error_message, 'danger') 
            return render_template('settings.html', form=form, error=error_message)

        # ユーザー名の更新
        if username:  # 新しいユーザー名が提供された場合のみ更新
            current_user.username = username

        # 新しいパスワードが提供された場合、パスワードを更新する
        if new_password:
            current_user.password = generate_password_hash(new_password, method='pbkdf2:sha256')

        db.session.commit()

        flash('設定が正常に更新されました', 'success')
        return redirect(url_for('settings'))

    return render_template('settings.html', form=form)

# /add_admin エンドポイントの追加
@app.route('/add_admin', methods=['GET', 'POST'])
def add_admin():
    if not current_user.is_admin:
        flash('このページにアクセスする権限がありません。', 'danger')
        return redirect(url_for('index'))

    form = AdminForm()

    if form.validate_on_submit():
        username = form.username.data
        email = form.email.data

        existing_admin = User.query.filter_by(username=username, email=email).first()

        if existing_admin:
            if not existing_admin.is_admin:
                existing_admin.is_admin = True
                try:
                    # データベースの更新処理
                    db.session.commit()
                    flash('ユーザーが正常に管理者に昇格しました！', 'success')
                    print('リダイレクト前')
                    return redirect(url_for('index'))
                except SQLAlchemyError as e:
                    db.session.rollback()
                    flash(f'データベースのエラーが発生しました: {str(e)}', 'danger')
                finally:
                    db.session.close()
            else:
                flash('ユーザーは既に管理者権限を持っています。', 'warning')
        else:
            flash('ユーザー名とメールアドレスが一致しません。', 'danger')

    return render_template('add_admin.html', form=form)

@app.route('/api/location_reservations/<int:location_id>')
def get_location_reservations(location_id):
    try:
        # location_idに基づいてロケーションを取得
        location = Location.query.get(location_id)

        if not location:
            app.logger.error(f'ロケーションが見つかりません: {location_id}')
            return jsonify({'error': 'ロケーションが見つかりません'}), 404

        # ロケーションに関連する予約データを取得し、ユーザードメインで絞り込む
        reservations = Reservation.query.filter_by(location_id=location_id, domain=current_user.email.split('@')[-1]).all()

        # 予約データをJSON形式に変換
        reservations_data = []
        for reservation in reservations:
            reservation_data = {
                'title': reservation.title,
                'start': reservation.start.isoformat(),
                'end': reservation.end.isoformat(),
            }
            reservations_data.append(reservation_data)

        return jsonify(reservations_data)
    except Exception as e:
        # エラーが発生した場合はログにエラーメッセージを出力
        app.logger.error(f'get_location_reservationsでエラーが発生しました: {str(e)}')
        return jsonify([]), 500
    
def can_access_reservation(reservation, user):
    # 予約したユーザーまたは管理者であるかを確認
    return user.is_admin or (reservation and reservation.user_id == user.id)

# Location 属性を取得するヘルパー関数
def get_location_attributes(location_name):
    location = Location.query.filter_by(location_name=location_name, domain=current_user.email.split('@')[-1]).first()
    return {'id': location.id, 'location_name': location.location_name} if location else None

# /location/<location_name> エンドポイントの修正と追加
@app.route('/location/<location_name>', methods=['GET', 'POST'])
@login_required
def location_page(location_name):
    # 指定された location_name の Location 属性を取得し、"g" に保存
    g.location_attributes = get_location_attributes(location_name)
    
    # Location が見つからない場合は、404 エラーを表示
    if not g.location_attributes:
        abort(404)

    # Location インスタンスを取得
    location = Location.query.filter_by(location_name=location_name, domain=current_user.email.split('@')[-1]).first()

    # reservation_id の Reservation インスタンスを取得
    reservation_id = request.args.get('desired_reservation_id', type=int)
    g.reservation = Reservation.query.get(reservation_id)

    # ロケーションに関連する予約を取得
    reservations = Reservation.query.filter_by(location_id=g.location_attributes['id'], domain=current_user.email.split('@')[-1]).all()

    # ReservationForm をインスタンス化
    form = ReservationForm()

    # ユーザーが予約を編集する権限があるか確認
    can_access = can_access_reservation(g.reservation, current_user)

    # 新しい予約を追加
    if form.validate_on_submit():
        start_date = form.start_date.data
        start_time = form.start_time.data
        
        # 終日予約の場合、終了日時を開始日時の23:59に設定
        if form.is_all_day.data:
            end_date = form.start_date.data
            end_time = time(23, 59)
        else:
            end_date = form.end_date.data
            end_time = form.end_time.data

        # 時間が選択されている場合のみdatetime.combine()を使用
        if start_time is not None:
            start_datetime = datetime.combine(start_date, start_time)
        else:
            start_datetime = datetime.combine(start_date, time.min)

        if end_time is not None:
            end_datetime = datetime.combine(end_date, end_time)
        else:
            end_datetime = datetime.combine(end_date, time.min)

        # 予約が有効かどうかを確認
        if start_date < date.today() or (not form.is_all_day.data and (start_datetime.hour < 7 or end_datetime.hour > 20)):
            flash('予約の詳細が無効です。', 'danger')
        else:
            # 既存の予約との重複を確認
            overlapping_reservations = Reservation.query.filter(
                (Reservation.location_id == g.location_attributes['id']) &
                (Reservation.id != reservation_id) &
                (
                    (Reservation.start <= start_datetime) & (Reservation.end > start_datetime) |
                    (Reservation.start < end_datetime) & (Reservation.end >= end_datetime) |
                    (Reservation.start >= start_datetime) & (Reservation.end <= end_datetime)
                )
            ).all()

            if overlapping_reservations:
                flash('指定された時間帯には既に予約があります。', 'danger')
            else:
                try:
                    # 新しい Reservation オブジェクトを作成
                    new_reservation = Reservation(
                        location_id=g.location_attributes['id'],
                        title=form.title.data,
                        start=start_datetime,
                        end=end_datetime,
                        user_id=current_user.id,
                        responsible_user=current_user.username,
                        domain=current_user.email.split('@')[-1]
                    )

                    # 新しい予約データをデータベースセッションに追加
                    db.session.add(new_reservation)
                    db.session.commit()

                    flash('予約が追加されました。', 'success')
                    return redirect(url_for('location_page', location_name=location_name))
                except SQLAlchemyError as e:
                    # エラーの処理
                    db.session.rollback()
                    flash(f'予約の追加中にエラーが発生しました: {str(e)}', 'danger')
                finally:
                    # セッションを閉じる
                    db.session.close()

    # テンプレートをレンダリングし、"g" に保存されたデータを使用
    return render_template('location_page.html', location=g.location_attributes, form=form, desired_reservation_id=reservation_id, reservations=reservations, can_access=can_access)


# 予約変更ページ
@app.route('/location/<location_name>/edit_reservation/<int:reservation_id>', methods=['GET', 'POST'])
@login_required
def edit_reservation(location_name, reservation_id):
    # データベースから指定された location_name の Location を取得
    location = Location.query.filter_by(location_name=location_name, domain=current_user.email.split('@')[-1]).first()

    # Location が存在しない場合は 404 エラーを表示
    if not location:
        abort(404)

    # データベースから指定された reservation_id の Reservation を取得
    reservation = Reservation.query.get(reservation_id)

    # リクエストからdesired_reservation_idを取得
    desired_reservation_id = request.args.get('desired_reservation_id', type=int)

    # Reservation が存在しない場合は 404 エラーを表示
    if not reservation or reservation.location_id != location.id:
        abort(404)

    # 予約が編集可能な権限があるか確認
    if not can_access_reservation(reservation, current_user):
        abort(403)

    # ReservationForm をインスタンス化
    form = ReservationForm(obj=reservation)

    if form.validate_on_submit():
        start_datetime = datetime.combine(form.start_date.data, form.start_time.data)
        
        # 終日予約の場合、終了日時を開始日時の23:59に設定
        if form.is_all_day.data:
            end_datetime = datetime.combine(form.start_date.data, datetime.max.time())
        else:
            end_datetime = datetime.combine(form.end_date.data, form.end_time.data)

        # 予約が有効かどうかを確認
        if form.start_date.data < date.today() or (not form.is_all_day.data and (start_datetime.hour < 7 or end_datetime.hour > 20)):
            flash('予約の詳細が無効です。', 'danger')
        else:
            try:
                # 既存の予約データを更新
                reservation.title = form.title.data
                reservation.start = start_datetime
                
                # 終日予約の場合、終了日時を開始日時の23:59に設定
                if form.is_all_day.data:
                    reservation.end = datetime.combine(form.start_date.data, datetime.max.time())
                else:
                    reservation.end = end_datetime

                # データベースをコミット
                db.session.commit()

                flash('予約が更新されました。', 'success')
                return redirect(url_for('location_page', location_name=location_name))
            except SQLAlchemyError as e:
                # エラーの処理
                db.session.rollback()
                flash(f'予約の更新中にエラーが発生しました: {str(e)}', 'danger')
            finally:
                # セッションを閉じる
                db.session.close()

    return render_template('location_page.html', location=location, form=form, reservation=reservation, desired_reservation_id=desired_reservation_id)

# 予約の削除エンドポイント
@app.route('/location/<location_name>/delete_reservation/<int:reservation_id>', methods=['POST'])
@login_required
def delete_reservation(location_name, reservation_id):
    # データベースから指定された location_name の Location を取得
    location = Location.query.filter_by(location_name=location_name, domain=current_user.email.split('@')[-1]).first()

    # Location が存在しない場合は 404 エラーを表示
    if not location:
        abort(404)

    # データベースから指定された reservation_id の Reservation を取得
    reservation = Reservation.query.get(reservation_id)

    # Reservation が存在しない場合は 404 エラーを表示
    if not reservation or reservation.location_id != location.id:
        abort(404)

    # 予約が削除可能な権限があるか確認
    if not can_access_reservation(reservation, current_user):
        abort(403)

    try:
        # 予約を削除
        db.session.delete(reservation)

        # データベースの変更をコミット
        db.session.commit()

        flash('予約が削除されました。', 'success')
    except SQLAlchemyError as e:
        # エラーの処理
        db.session.rollback()
        flash(f'予約の削除中にエラーが発生しました: {str(e)}', 'danger')
    finally:
        # セッションを閉じる
        db.session.close()

    return redirect(url_for('location_page', location_name=location_name))

@app.route('/update_reservation_time', methods=['POST'])
def update_reservation_time():
    event_id = request.form.get('eventId')
    new_start = request.form.get('newStart')
    new_end = request.form.get('newEnd')

    # データベースで対応する予約を取得
    reservation = Reservation.query.get(event_id)

    if reservation:
        # 予約が見つかった場合、日時を更新
        reservation.start_datetime = new_start
        reservation.end_datetime = new_end

        # 予約を保存
        db.session.commit()

        return jsonify({'message': '予約が更新されました。'})
    else:
        return jsonify({'message': '対応する予約が見つかりませんでした。'}), 404


# データベースの初期化
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
