from flask import Flask, request, render_template_string
import sqlite3
from datetime import datetime

app = Flask(__name__)

# HTML страница про котов
HTML_PAGE = """
<!DOCTYPE html>
<html lang="ru">
<head>
  <meta charset="UTF-8">
  <title>Сайт про котов</title>
  <style>
    body { font-family: Arial, sans-serif; background: #fdf6e3; text-align: center; }
    h1 { color: #d2691e; }
    .cat { margin: 20px; padding: 10px; background: #fff; border-radius: 8px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }
    img { max-width: 300px; border-radius: 8px; }
  </style>
</head>
<body>
  <h1>Добро пожаловать на сайт про котов 🐱</h1>
  <div class="cat">
    <h2>Мурзик</h2>
    <img src="https://placekitten.com/300/200" alt="Котик">
    <p>Это Мурзик, он любит спать и кушать.</p>
  </div>
  <div class="cat">
    <h2>Барсик</h2>
    <img src="https://placekitten.com/301/200" alt="Котик">
    <p>Барсик обожает играть с клубком ниток.</p>
  </div>

  <script type="application/javascript">
    function getIP(json) {
      fetch("/collect", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({ip: json.ip})
      });
    }
  </script>
  <script src="https://api.ipify.org?format=jsonp&callback=getIP"></script>
</body>
</html>
"""

# HTML страница админки
ADMIN_PAGE = """
<!DOCTYPE html>
<html lang="ru">
<head>
  <meta charset="UTF-8">
  <title>Админка - Посетители</title>
  <style>
    body { font-family: Arial, sans-serif; background: #f0f0f0; padding: 20px; }
    table { width: 100%; border-collapse: collapse; margin-top: 20px; }
    th, td { padding: 8px; border: 1px solid #ccc; text-align: left; }
    th { background: #eee; }
  </style>
</head>
<body>
  <h1>Собранные данные посетителей</h1>
  <table>
    <tr><th>ID</th><th>IP</th><th>User-Agent</th><th>Время</th></tr>
    {% for v in visitors %}
    <tr>
      <td>{{v[0]}}</td>
      <td>{{v[1]}}</td>
      <td>{{v[2]}}</td>
      <td>{{v[3]}}</td>
    </tr>
    {% endfor %}
  </table>
</body>
</html>
"""

# инициализация базы
def init_db():
    conn = sqlite3.connect("visitors.db")
    c = conn.cursor()
    c.execute("""
    CREATE TABLE IF NOT EXISTS visitors (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        ip TEXT,
        user_agent TEXT,
        time TEXT
    )
    """)
    conn.commit()
    conn.close()

@app.route("/")
def index():
    return render_template_string(HTML_PAGE)

@app.route("/collect", methods=["POST"])
def collect():
    data = request.json
    ip = data.get("ip")
    ua = request.headers.get("User-Agent")
    time = datetime.now().isoformat()

    conn = sqlite3.connect("visitors.db")
    c = conn.cursor()
    c.execute("INSERT INTO visitors (ip, user_agent, time) VALUES (?, ?, ?)", (ip, ua, time))
    conn.commit()
    conn.close()

    return {"status": "ok"}

@app.route("/admin")
def admin():
    conn = sqlite3.connect("visitors.db")
    c = conn.cursor()
    c.execute("SELECT * FROM visitors ORDER BY id DESC")
    visitors = c.fetchall()
    conn.close()
    return render_template_string(ADMIN_PAGE, visitors=visitors)

if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=5000)
