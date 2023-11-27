from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from models import db, Location

# Cloud SQL接続情報
INSTANCE_CONNECTION_NAME = "rare-chiller-406009:us-west1:flask"
DB_USER = "root"
DB_PASSWORD = "test"
DB_NAME = "project-c"
socket_dir = "/cloudsql"

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+pymysql://{DB_USER}:{DB_PASSWORD}@localhost:3306/{DB_NAME}?unix_socket={socket_dir}/{INSTANCE_CONNECTION_NAME}'
db.init_app(app)

# データベースの初期化
with app.app_context():
    db.create_all()

# ページ表示用のエンドポイント
@app.route('/')
def show_pages():
    # データベースからロケーション情報を取得
    locations = Location.query.all()

    # テンプレートにデータを渡してHTMLを生成
    return render_template('pages.html', locations=locations)

if __name__ == '__main__':
    app.run(debug=True)
