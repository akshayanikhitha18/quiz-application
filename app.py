import os, random
from functools import wraps
from flask import Flask, request, jsonify, session
import mysql.connector
from werkzeug.security import generate_password_hash, check_password_hash
from config import DB

app = Flask(__name__, static_folder="static", static_url_path="")
app.secret_key = os.environ.get("SECRET_KEY", "quizsphere-dev-secret")


def db(sql, args=(), mode="all"):
    con = mysql.connector.connect(**DB)
    cur = con.cursor(dictionary=True)
    try:
        cur.execute(sql, args)
        if mode == "all":
            return cur.fetchall()
        if mode == "one":
            return cur.fetchone()
        con.commit()
        return cur.lastrowid
    finally:
        cur.close()
        con.close()


def need(role=None):
    def deco(f):
        @wraps(f)
        def w(*a, **k):
            if "uid" not in session:
                return jsonify(error="Please log in first"), 401
            if role and session.get("role") != role:
                return jsonify(error="Admins only"), 403
            return f(*a, **k)
        return w
    return deco


def err(msg, code=400):
    return jsonify(error=msg), code


@app.errorhandler(mysql.connector.Error)
def db_error(e):
    return err("Database error. Check config.py and that MySQL is running.", 500)


@app.get("/")
def index():
    return app.send_static_file("index.html")


def login_user(u):
    session["uid"], session["role"] = u["id"], u["role"]
    return jsonify(id=u["id"], name=u["name"], role=u["role"])


@app.post("/api/register")
def register():
    d = request.get_json() or {}
    name, email, pw = (d.get("name") or "").strip(), (d.get("email") or "").strip().lower(), d.get("password") or ""
    if not name or "@" not in email or len(pw) < 6:
        return err("Enter a name, a valid email and a password of 6+ characters")
    if db("SELECT id FROM users WHERE email=%s", (email,), "one"):
        return err("That email is already registered")
    uid = db("INSERT INTO users (name,email,password_hash) VALUES (%s,%s,%s)",
             (name, email, generate_password_hash(pw)), "w")
    return login_user({"id": uid, "name": name, "role": "student"})


@app.post("/api/login")
def login():
    d = request.get_json() or {}
    u = db("SELECT * FROM users WHERE email=%s", ((d.get("email") or "").strip().lower(),), "one")
    if not u or not check_password_hash(u["password_hash"], d.get("password") or ""):
        return err("Wrong email or password", 401)
    return login_user(u)


@app.post("/api/logout")
def logout():
    session.clear()
    return jsonify(ok=True)


@app.get("/api/me")
def me():
    if "uid" not in session:
        return jsonify(None)
    u = db("SELECT id,name,role FROM users WHERE id=%s", (session["uid"],), "one")
    return jsonify(u)


@app.get("/api/subjects")
@need()
def subjects():
    return jsonify(db("SELECT s.id, s.name, COUNT(q.id) AS questions FROM subjects s "
                      "LEFT JOIN questions q ON q.subject_id=s.id GROUP BY s.id ORDER BY s.id"))


def options_of(q):
    return {k: q["option_" + k.lower()] for k in "ABCD" if q["option_" + k.lower()]}


@app.get("/api/quiz/<int:sid>")
@need()
def quiz(sid):
    s = db("SELECT name FROM subjects WHERE id=%s", (sid,), "one")
    qs = db("SELECT * FROM questions WHERE subject_id=%s", (sid,))
    if not s or not qs:
        return err("No questions in this subject yet")
    random.shuffle(qs)
    return jsonify(subject_id=sid, subject=s["name"], questions=[
        {"id": q["id"], "qtype": q["qtype"], "question": q["question"], "options": options_of(q)} for q in qs[:10]])


@app.post("/api/submit")
@need()
def submit():
    d = request.get_json() or {}
    try:
        sid, ids = int(d["subject_id"]), [int(i) for i in d["question_ids"]]
    except (KeyError, ValueError, TypeError):
        return err("Bad quiz data")
    if not ids:
        return err("Bad quiz data")
    answers = d.get("answers") or {}
    qs = db("SELECT * FROM questions WHERE subject_id=%s AND id IN (" + ",".join(["%s"] * len(ids)) + ")", [sid] + ids)
    by_id = {q["id"]: q for q in qs}
    results, score = [], 0
    for i in ids:
        q = by_id.get(i)
        if not q:
            continue
        chosen = answers.get(str(i))
        ok = chosen == q["correct"]
        score += ok
        results.append({"id": i, "question": q["question"], "options": options_of(q), "chosen": chosen,
                        "correct": q["correct"], "is_correct": ok, "explanation": q["explanation"]})
    aid = db("INSERT INTO attempts (user_id,subject_id,score,total) VALUES (%s,%s,%s,%s)",
             (session["uid"], sid, score, len(results)), "w")
    for r in results:
        db("INSERT INTO attempt_answers (attempt_id,question_id,chosen,is_correct) VALUES (%s,%s,%s,%s)",
           (aid, r["id"], r["chosen"], r["is_correct"]), "w")
    return jsonify(score=score, total=len(results), results=results)


@app.get("/api/history")
@need()
def history():
    return jsonify(db("SELECT a.id, s.name AS subject, a.score, a.total, LEFT(CAST(a.taken_at AS CHAR),16) AS taken "
                      "FROM attempts a JOIN subjects s ON s.id=a.subject_id WHERE a.user_id=%s "
                      "ORDER BY a.taken_at DESC, a.id DESC LIMIT 50", (session["uid"],)))


@app.get("/api/stats")
@need()
def stats():
    return jsonify(db("SELECT s.name, COUNT(a.id) AS attempts, "
                      "CAST(COALESCE(ROUND(AVG(a.score/a.total*100)),0) AS UNSIGNED) AS avg, "
                      "CAST(COALESCE(ROUND(MAX(a.score/a.total*100)),0) AS UNSIGNED) AS best "
                      "FROM subjects s LEFT JOIN attempts a ON a.subject_id=s.id AND a.user_id=%s "
                      "GROUP BY s.id ORDER BY s.id", (session["uid"],)))


@app.get("/api/admin/questions")
@need("admin")
def admin_list():
    return jsonify(db("SELECT q.*, s.name AS subject FROM questions q JOIN subjects s ON s.id=q.subject_id "
                      "ORDER BY q.id DESC"))


@app.post("/api/admin/questions")
@need("admin")
def admin_add():
    d = request.get_json() or {}
    qtype, text = d.get("qtype"), (d.get("question") or "").strip()
    correct = (d.get("correct") or "").upper()
    if qtype == "tf":
        opts = ["True", "False", None, None]
    else:
        opts = [(d.get("option_" + k) or "").strip() or None for k in "abcd"]
    valid = "AB" if qtype == "tf" else "ABCD"
    if qtype not in ("mcq", "tf") or not text or correct not in list(valid) or not opts[0] or not opts[1]:
        return err("Fill in the question, the options and the correct answer")
    if qtype == "mcq" and not (opts[2] and opts[3]):
        return err("Multiple-choice questions need four options")
    if not db("SELECT id FROM subjects WHERE id=%s", (d.get("subject_id"),), "one"):
        return err("Pick a subject")
    qid = db("INSERT INTO questions (subject_id,qtype,question,option_a,option_b,option_c,option_d,correct,explanation) "
             "VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)",
             (d["subject_id"], qtype, text, *opts, correct, (d.get("explanation") or "").strip()), "w")
    return jsonify(id=qid)


@app.delete("/api/admin/questions/<int:qid>")
@need("admin")
def admin_delete(qid):
    db("DELETE FROM questions WHERE id=%s", (qid,), "w")
    return jsonify(ok=True)


if __name__ == "__main__":
    app.run(debug=True)
