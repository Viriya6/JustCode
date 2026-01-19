import os, json, subprocess, tempfile
from datetime import datetime
from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "dev-secret-key-123")

# Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(BASE_DIR, 'database.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

PROBLEMS_DIR = os.path.join(BASE_DIR, "problems")
if not os.path.exists(PROBLEMS_DIR):
    os.makedirs(PROBLEMS_DIR)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)

class Submission(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50))
    problem_id = db.Column(db.String(100))
    verdict = db.Column(db.String(50))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

with app.app_context():
    db.create_all()
    if not User.query.filter_by(username="admin").first():
        pw = os.getenv("ADMIN_PASSWORD", "admin123")
        db.session.add(User(username="admin", password=generate_password_hash(pw), is_admin=True))
        db.session.commit()

def run_judge(p_id, code):
    p_path = os.path.join(PROBLEMS_DIR, p_id)
    tc_path = os.path.join(p_path, "testcases")
    tl = 2.0
    if os.path.exists(os.path.join(p_path, 'info.json')):
        with open(os.path.join(p_path, 'info.json'), 'r') as f:
            tl = float(json.load(f).get('time_limit', 2.0))
    
    if not os.path.exists(tc_path): return {"verdict": "Error: TC Missing", "details": []}

    with tempfile.NamedTemporaryFile(suffix=".py", mode='w', delete=False) as tf:
        tf.write(code)
        py_file = tf.name

    results, final_v = [], "ACCEPTED"
    try:
        in_files = sorted([f for f in os.listdir(tc_path) if f.endswith('.in')])
        for f_in in in_files:
            case_name = f_in.replace('.in', '')
            f_out = case_name + '.out'
            if not os.path.exists(os.path.join(tc_path, f_out)): continue
            with open(os.path.join(tc_path, f_in), 'r') as fin:
                expected = open(os.path.join(tc_path, f_out), 'r').read().strip()
                proc = subprocess.run(['python', py_file], input=fin.read(), capture_output=True, text=True, timeout=tl)
                status = "AC"
                if proc.returncode != 0: status = "RE"
                elif proc.stdout.strip() != expected: status = "WA"
                results.append({"test": case_name, "status": status})
                if status != "AC": final_v = f"{status} on {case_name}"; break
    except subprocess.TimeoutExpired: final_v = "TLE"
    except Exception: final_v = "System Error"
    finally:
        if os.path.exists(py_file): os.remove(py_file)
    return {"verdict": final_v, "details": results}

@app.route('/')
@app.route('/problem/<p_id>')
def index(p_id=None):
    if 'user_id' not in session: return redirect(url_for('login'))
    return render_template('index.html', is_admin=session.get('is_admin', False))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        u = User.query.filter_by(username=request.form['username']).first()
        if u and check_password_hash(u.password, request.form['password']):
            session.update({'user_id': u.id, 'username': u.username, 'is_admin': u.is_admin})
            return redirect(url_for('index'))
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear(); return redirect(url_for('login'))

@app.route('/api/problems-list')
def list_probs():
    probs = []
    if os.path.exists(PROBLEMS_DIR):
        for d in sorted(os.listdir(PROBLEMS_DIR)):
            inf = os.path.join(PROBLEMS_DIR, d, 'info.json')
            if os.path.exists(inf):
                with open(inf, 'r') as f:
                    p = json.load(f)
                    probs.append({"id": d, "title": p['title'], "tags": p.get('tags', [])})
    return jsonify(probs)

@app.route('/api/problem/<p_id>')
def get_prob(p_id):
    path = os.path.join(PROBLEMS_DIR, p_id, 'info.json')
    if not os.path.exists(path): return jsonify({"error": "Not Found"}), 404
    with open(path, 'r') as f: return jsonify(json.load(f))

@app.route('/judge', methods=['POST'])
def judge_api():
    if 'username' not in session: return jsonify({"error": "Unauthorized"}), 403
    d = request.json
    res = run_judge(d['id'], d['code'])
    db.session.add(Submission(username=session['username'], problem_id=d['id'], verdict=res['verdict']))
    db.session.commit()
    return jsonify(res)

@app.route('/api/status', methods=['GET', 'DELETE'])
def api_status():
    if request.method == 'DELETE':
        if not session.get('is_admin'): return "403", 403
        Submission.query.delete(); db.session.commit()
        return jsonify({"status": "success"})
    subs = Submission.query.order_by(Submission.timestamp.desc()).limit(30).all()
    return jsonify([{"u":s.username, "p":s.problem_id, "v":s.verdict, "t":s.timestamp.strftime("%H:%M:%S")} for s in subs])

@app.route('/api/users', methods=['GET', 'POST', 'DELETE'])
def manage_users():
    if not session.get('is_admin'): return "403", 403
    if request.method == 'POST':
        d = request.json
        db.session.add(User(username=d['username'], password=generate_password_hash(d['password']), is_admin=d.get('is_admin', False)))
        db.session.commit()
    elif request.method == 'DELETE':
        User.query.filter_by(id=request.args.get('id')).delete(); db.session.commit()
    return jsonify([{"id": u.id, "username": u.username, "is_admin": u.is_admin} for u in User.query.all()])

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)