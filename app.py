import os
import hmac
import hashlib
import time
from flask import Flask, request, redirect, session, render_template, url_for
from requests_oauthlib import OAuth2Session
from dotenv import load_dotenv
from database import init_db, link_user

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "flask_secret_change_me")

# X (Twitter) OAuth 2.0 設定
CLIENT_ID = os.getenv("X_CLIENT_ID")
CLIENT_SECRET = os.getenv("X_CLIENT_SECRET")
REDIRECT_URI = f"{os.getenv('BASE_URL', 'http://localhost:5000')}/callback"
SIGNING_SECRET = os.getenv("SIGNING_SECRET", "default_secret_key_change_me")

# X OAuth2 スコープ (ユーザー名を取得するために必要)
SCOPES = ["users.read", "tweet.read"]

def verify_signature(user_id, sig_data):
    """
    ボットからの署名を検証する。
    """
    try:
        timestamp, sig = sig_data.split(".")
        # タイムスタンプが古すぎる場合は拒否 (例: 24時間)
        if int(time.time()) - int(timestamp) > 86400:
            return False
            
        message = f"{user_id}:{timestamp}".encode()
        expected_sig = hmac.new(SIGNING_SECRET.encode(), message, hashlib.sha256).hexdigest()
        return hmac.compare_digest(sig, expected_sig)
    except Exception:
        return False

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/start")
def start():
    user_id = request.args.get("user_id")
    sig = request.args.get("sig")
    
    if not user_id or not sig or not verify_signature(user_id, sig):
        return "Invalid or expired link. Please use /link in Discord again.", 403
    
    # セッションに Discord ID を保存
    session["discord_id"] = user_id
    
    oauth = OAuth2Session(CLIENT_ID, redirect_uri=REDIRECT_URI, scope=SCOPES)
    authorization_url, state = oauth.authorization_url("https://twitter.com/i/oauth2/authorize", code_challenge="challenge", code_challenge_method="plain")
    
    session["oauth_state"] = state
    return redirect(authorization_url)

@app.route("/callback")
def callback():
    code = request.args.get("code")
    state = request.args.get("state")
    
    if state != session.get("oauth_state"):
        return "State mismatch error.", 400
        
    oauth = OAuth2Session(CLIENT_ID, redirect_uri=REDIRECT_URI, scope=SCOPES)
    token = oauth.fetch_token(
        "https://api.twitter.com/2/oauth2/token",
        client_secret=CLIENT_SECRET,
        code=code,
        code_verifier="challenge"
    )
    
    # ユーザー情報を取得
    response = oauth.get("https://api.twitter.com/2/users/me")
    user_data = response.json().get("data")
    
    if not user_data:
        return "Failed to fetch X user data.", 500
        
    x_user_id = user_data["id"]
    x_username = user_data["username"]
    discord_id = session.get("discord_id")
    
    if not discord_id:
        return "Discord session expired.", 400
        
    # データベースに保存
    link_user(discord_id, x_user_id, x_username)
    
    return render_template("success.html", username=x_username)

if __name__ == "__main__":
    init_db()
    # 外部からのアクセスを許可するために host='0.0.0.0' を追加
    app.run(host='0.0.0.0', port=80, debug=False)
