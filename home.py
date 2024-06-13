import streamlit as st
import requests

KEYCLOAK_URL = "http://keycloak:8080/realms/news_realm/protocol/openid-connect/token"
CLIENT_ID = "news_app_client"

NEWS_API_URL = "http://news-api:8081/api/articles/all/2"


# JWTを取得する関数
def get_jwt_token(username, passsword):
    payload = {
        'grant_type': 'password',
        'client_id': CLIENT_ID,
        'username': username,
        'password': passsword,
    }
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    response = requests.post(KEYCLOAK_URL, data=payload, headers=headers)
    if response.status_code != 200:
        st.error(f"Error: {response.status_code} {response.text}")
    response.raise_for_status()
    return response.json().get("access_token")


# Premiumニュースを取得する関数
def get_premium_news(token):
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(NEWS_API_URL, headers=headers)
    response.raise_for_status()
    return response.json()


# Streamlitアプリケーション
st.title("News Viewer")
st.write("Login to view premium news articles.")

# ユーザ名とパスワードの入力
username = st.text_input("Username")
password = st.text_input("Password", type="password")

if st.button("Get Premium News"):
    if username and password:
        try:
            token = get_jwt_token(username, password)
            news = get_premium_news(token)
            st.success("Successsfully retrieved premium news!")
            st.write(news)
        except requests.exceptions.RequestException as e:
            st.error(f"An error occurred: {e}")
    else:
        st.error("Please enter both username and password.")
