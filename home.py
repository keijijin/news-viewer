import streamlit as st
import requests
import time

# セッション状態を初期化
if "token" not in st.session_state:
    st.session_state.token = None
if "token_expires" not in st.session_state:
    st.session_state.token_expires = 0
if "username" not in st.session_state:
    st.session_state.username = ""
if "password" not in st.session_state:
    st.session_state.password = ""

# APIのエンドポイント
BASE_URL = "http://news-api:8081/api/articles"

def get_token(username, password):
    # Keycloakのトークンを取得
    token_url = "http://keycloak:8080/realms/news_realm/protocol/openid-connect/token"
    client_id = "news_app_client"
    data = {
        'grant_type': 'password',
        'client_id': client_id,
        'username': username,
        'password': password
    }
    response = requests.post(token_url, data=data)
    if response.status_code == 200:
        data = response.json();
        st.session_state.token = data["access_token"]
        st.session_state.token_expires = time.time() + data["expires_in"]
        return True
    else:
        return None

def ensure_token():
    if time.time() >= st.session_state.token_expires:
        if not get_token(st.session_state.username, st.session_state.password):
            st.error("トークンの有効期限が切れました。再ログインしてください。")
            return False
    return True

def fetch_article_titles():
    if not ensure_token():
        return []
    headers = {'Authorization': f'Bearer {st.session_state.token}'}
    response = requests.get(f"{BASE_URL}/titles", headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        st.sidebar.error("記事のタイトルリストを取得できませんでした。")
        return []

def fetch_article_content(article_id):
    if not ensure_token():
        return {}
    headers = {'Authorization': f'Bearer {st.session_state.token}'}
    response = requests.get(f"{BASE_URL}/{article_id}", headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        st.error("記事の内容を取得できませんでした。")
        return {}

def main():
    st.sidebar.title("ニュース記事閲覧アプリ")

    if st.session_state.token is None:
        username = st.sidebar.text_input("ユーザー名")
        password = st.sidebar.text_input("パスワード", type="password")
        if st.sidebar.button("ログイン"):
            if get_token(username, password):
                st.session_state.username = username
                st.session_state.password = password
                st.rerun()  # トークンが取得されたらページを再読み込みして状態を更新
            else:
                st.sidebar.error("ログインに失敗しました。ユーザー名またはパスワードが間違っています。")
    else:
        st.sidebar.success("ログイン成功")
        if st.sidebar.button("ログアウト"):
            st.session_state.token = None
            st.session_state.username = ""
            st.session_state.password = ""
            st.rerun()
        
        articles = fetch_article_titles()
        if articles:
            article_titles = [article['title'] for article in articles]

            selected_title = st.sidebar.selectbox("記事を選択", article_titles)
            if selected_title:
                selected_article = next(article for article in articles if article['title'] == selected_title)
                article_content = fetch_article_content(selected_article['id'])
                if article_content:
                    st.write(f"### {article_content['title']}")
                    st.write(article_content['content'])

if __name__ == "__main__":
    main()
