import streamlit as st
import requests

# APIのエンドポイント
BASE_URL = "http://news-api:8081/api/articles"

def login(username, password):
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
        return response.json()['access_token']
    else:
        st.sidebar.error("ログインに失敗しました。")
        return None

def fetch_article_titles(token):
    headers = {'Authorization': f'Bearer {token}'}
    response = requests.get(f"{BASE_URL}/titles", headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        st.sidebar.error("記事のタイトルリストを取得できませんでした。")
        return []

def fetch_article_content(token, article_id):
    headers = {'Authorization': f'Bearer {token}'}
    response = requests.get(f"{BASE_URL}/{article_id}", headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        st.error("記事の内容を取得できませんでした。")
        return {}

def main():
    st.sidebar.title("ニュース記事閲覧アプリ")

    if 'token' not in st.session_state:
        st.session_state.token = None

    if st.session_state.token is None:
        username = st.sidebar.text_input("ユーザー名")
        password = st.sidebar.text_input("パスワード", type="password")
        if st.sidebar.button("ログイン"):
            token = login(username, password)
            if token:
                st.session_state.token = token
                st.experimental_rerun()  # トークンが取得されたらページを再読み込みして状態を更新
    else:
        st.sidebar.success("ログイン成功")
        if st.sidebar.button("ログアウト"):
            st.session_state.token = None
            st.experimental_rerun()
        
        articles = fetch_article_titles(st.session_state.token)
        article_titles = [article['title'] for article in articles]

        selected_title = st.sidebar.selectbox("記事を選択", article_titles)
        if selected_title:
            selected_article = next(article for article in articles if article['title'] == selected_title)
            article_content = fetch_article_content(st.session_state.token, selected_article['id'])
            if article_content:
                st.write(f"### {article_content['title']}")
                st.write(article_content['content'])

if __name__ == "__main__":
    main()
