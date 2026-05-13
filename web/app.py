import sys
import os
import json
import smtplib
import re
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timezone

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from flask import Flask, render_template, request, jsonify, Response, redirect

from main import build_bot
from src import memory

app = Flask(__name__)
app.secret_key = os.environ.get("CLAWBOT_SECRET_KEY", "clawbot-dev-secret-change-in-prod")

bot = build_bot()

JOBS_FILE        = os.path.join(os.path.dirname(__file__), "data", "jobs.json")
SUBSCRIBERS_FILE = os.path.join(os.path.dirname(__file__), "..", "memory_system", "email_subscribers.json")
SMTP_HOST     = os.environ.get("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT     = int(os.environ.get("SMTP_PORT", "587"))
SMTP_USER     = os.environ.get("SMTP_USER", "")
SMTP_PASSWORD = os.environ.get("SMTP_PASSWORD", "")
FROM_EMAIL    = os.environ.get("FROM_EMAIL", SMTP_USER)
SITE_NAME     = os.environ.get("SITE_NAME", "Calcojobs")
SITE_URL      = os.environ.get("SITE_URL", "https://calcojobs.com")


# ── Data loaders ──────────────────────────────────────────────────────────────

def _load_jobs():
    with open(JOBS_FILE) as f:
        return json.load(f)


# ── Email subscriber store ────────────────────────────────────────────────────

def _load_subscribers():
    if not os.path.exists(SUBSCRIBERS_FILE):
        return []
    with open(SUBSCRIBERS_FILE) as f:
        return json.load(f)

def _save_subscribers(subs):
    os.makedirs(os.path.dirname(SUBSCRIBERS_FILE), exist_ok=True)
    with open(SUBSCRIBERS_FILE, "w") as f:
        json.dump(subs, f, indent=2)

def _valid_email(email):
    return bool(re.match(r"[^@\s]+@[^@\s]+\.[^@\s]+", email))


# ── Routes ────────────────────────────────────────────────────────────────────

@app.route("/")
def index():
    return redirect("/jobs")


@app.route("/dashboard")
def dashboard():
    memories      = memory.all_memories()
    last_analysis = memory.recall("last_analysis")
    last_error    = memory.recall("last_error")
    return render_template(
        "index.html",
        memories=memories,
        last_analysis=last_analysis,
        last_error=last_error,
    )


@app.route("/jobs")
def jobs():
    all_jobs   = _load_jobs()
    regions    = sorted({j["region"]   for j in all_jobs})
    types      = sorted({j["type"]     for j in all_jobs})
    categories = sorted({j.get("category", "Robotics & Automation") for j in all_jobs})
    return render_template(
        "jobs.html",
        jobs=all_jobs,
        regions=regions,
        types=types,
        categories=categories,
        job_count=len(all_jobs),
        site_url=SITE_URL,
    )


@app.route("/privacy")
def privacy():
    return render_template("privacy.html")


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/robots.txt")
def robots_txt():
    body = f"User-agent: *\nAllow: /\nSitemap: {SITE_URL}/sitemap.xml\n"
    return Response(body, mimetype="text/plain")


@app.route("/sitemap.xml")
def sitemap_xml():
    all_jobs = _load_jobs()
    today    = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    urls = [
        {"loc": SITE_URL,              "priority": "1.0", "changefreq": "weekly"},
        {"loc": f"{SITE_URL}/jobs",    "priority": "0.9", "changefreq": "weekly"},
        {"loc": f"{SITE_URL}/about",   "priority": "0.7", "changefreq": "monthly"},
        {"loc": f"{SITE_URL}/privacy", "priority": "0.3", "changefreq": "yearly"},
    ]
    for job in all_jobs:
        urls.append({
            "loc": f"{SITE_URL}/jobs#job-{job['id']}",
            "priority": "0.6",
            "changefreq": "weekly",
            "lastmod": job.get("posted", today),
        })

    lines = ['<?xml version="1.0" encoding="UTF-8"?>',
             '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for u in urls:
        lines.append("  <url>")
        lines.append(f"    <loc>{u['loc']}</loc>")
        if "lastmod" in u:
            lines.append(f"    <lastmod>{u['lastmod']}</lastmod>")
        else:
            lines.append(f"    <lastmod>{today}</lastmod>")
        lines.append(f"    <changefreq>{u['changefreq']}</changefreq>")
        lines.append(f"    <priority>{u['priority']}</priority>")
        lines.append("  </url>")
    lines.append("</urlset>")

    return Response("\n".join(lines), mimetype="application/xml")


@app.route("/command", methods=["POST"])
def run_command():
    data = request.get_json()
    command_text = (data or {}).get("command", "").strip()
    if not command_text:
        return jsonify({"error": "No command provided"}), 400
    result = bot.execute(command_text)
    return jsonify({"result": result})


@app.route("/subscribe", methods=["POST"])
def subscribe():
    data  = request.get_json() or {}
    email = data.get("email", "").strip().lower()

    if not email or not _valid_email(email):
        return jsonify({"error": "Please enter a valid email address."}), 400

    subs = _load_subscribers()
    if any(s["email"] == email for s in subs):
        return jsonify({"ok": True, "message": "You're already subscribed!"})

    subs.append({
        "email": email,
        "subscribed_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    })
    _save_subscribers(subs)
    _send_welcome(email)

    return jsonify({"ok": True, "message": "You're subscribed! We'll be in touch."})


@app.route("/unsubscribe", methods=["POST"])
def unsubscribe():
    data  = request.get_json() or {}
    email = data.get("email", "").strip().lower()
    subs  = _load_subscribers()
    new   = [s for s in subs if s["email"] != email]
    if len(new) < len(subs):
        _save_subscribers(new)
        return jsonify({"ok": True, "message": "You've been unsubscribed."})
    return jsonify({"ok": False, "message": "Email not found."}), 404


@app.route("/status")
def get_status():
    all_mems      = memory.all_memories()
    last_analysis = memory.recall("last_analysis")
    last_error    = memory.recall("last_error")
    return jsonify({
        "memory_count":         len(all_mems),
        "last_analysis_date":   last_analysis["timestamp"][:10] if last_analysis else None,
        "last_analysis_result": last_analysis["value"]["result"] if last_analysis else None,
        "last_error":           last_error["value"]["error"] if last_error else None,
        "subscriber_count":     len(_load_subscribers()),
    })


@app.route("/history")
def get_history():
    entries = memory.recall_all("calibration_history")
    return jsonify([
        {"timestamp": e["timestamp"], "date": e["timestamp"][:10], **e["value"]}
        for e in entries
    ])


@app.route("/memories")
def get_memories():
    context = request.args.get("context")
    entries = memory.recall_by_context(context) if context else memory.all_memories()
    return jsonify(entries)


# ── Email helpers ─────────────────────────────────────────────────────────────

def _send_email(to, subject, body_html):
    if not SMTP_USER or not SMTP_PASSWORD:
        return False
    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"]    = f"{SITE_NAME} <{FROM_EMAIL}>"
        msg["To"]      = to
        msg.attach(MIMEText(body_html, "html"))
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as s:
            s.starttls()
            s.login(SMTP_USER, SMTP_PASSWORD)
            s.sendmail(FROM_EMAIL, to, msg.as_string())
        return True
    except Exception:
        return False


def _send_welcome(email):
    html = f"""
    <div style="font-family:sans-serif;max-width:600px;margin:auto;color:#1e293b">
      <h2 style="color:#7c3aed">Welcome to {SITE_NAME}!</h2>
      <p>You're now subscribed to weekly job alerts and updates.</p>
      <p>We'll send you a digest every week with the latest opportunities.</p>
      <hr style="border:none;border-top:1px solid #e2e8f0;margin:24px 0">
      <p style="font-size:0.8rem;color:#94a3b8">
        Don't want emails? <a href="{SITE_URL}/unsubscribe?email={email}" style="color:#7c3aed">Unsubscribe</a>
      </p>
    </div>"""
    _send_email(email, f"Welcome to {SITE_NAME}!", html)


def send_weekly_digest(custom_message=""):
    """Call this weekly (e.g. via cron) to email all subscribers."""
    subs = _load_subscribers()
    if not subs:
        return 0

    all_jobs = _load_jobs()[:5]
    job_rows = "".join(
        f"""<tr>
          <td style="padding:8px;border-bottom:1px solid #e2e8f0">
            <strong>{j['title']}</strong><br>
            <span style="color:#64748b;font-size:0.85rem">{j['company']} · {j['city']}, CA · {j['salary']}</span>
          </td>
        </tr>"""
        for j in all_jobs
    )

    sent = 0
    for sub in subs:
        html = f"""
        <div style="font-family:sans-serif;max-width:600px;margin:auto;color:#1e293b">
          <h2 style="color:#7c3aed">Your Weekly Update from {SITE_NAME}</h2>
          {f'<p>{custom_message}</p>' if custom_message else ''}
          <h3 style="margin:20px 0 10px;color:#1e293b">This Week's Top Jobs</h3>
          <table style="width:100%;border-collapse:collapse">{job_rows}</table>
          <p style="margin-top:20px">
            <a href="{SITE_URL}/jobs" style="background:#7c3aed;color:#fff;padding:10px 20px;border-radius:6px;text-decoration:none">
              View All Jobs →
            </a>
          </p>
          <hr style="border:none;border-top:1px solid #e2e8f0;margin:24px 0">
          <p style="font-size:0.8rem;color:#94a3b8">
            <a href="{SITE_URL}/unsubscribe?email={sub['email']}" style="color:#7c3aed">Unsubscribe</a>
          </p>
        </div>"""
        if _send_email(sub["email"], f"Your weekly jobs from {SITE_NAME}", html):
            sent += 1
    return sent


if __name__ == "__main__":
    app.run(debug=True, port=5000)
