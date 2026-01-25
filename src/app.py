import os
from flask import Flask, send_from_directory
from config import config
from extensions import login_manager, supabase

from routes.auth import auth_bp
from routes.main import main_bp 

config_name = os.environ.get('FLASK_CONFIG') or 'default'

app = Flask(__name__)
app.config.from_object(config[config_name])

login_manager.init_app(app)

app.register_blueprint(auth_bp)
app.register_blueprint(main_bp)

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(
        os.path.join(app.root_path, 'static'),
        'favicon.svg',
        mimetype='image/svg+xml'
    )

@app.route('/supabase-todos')
def supabase_todos():
    response = supabase.table('todos').select("*").execute()
    todos = response.data

    html = '<h1>Todos</h1><ul>'
    for todo in todos:
        html += f'<li>{todo["name"]}</li>'
    html += '</ul>'

    return html

if __name__ == "__main__":
    app.run(debug=True)
