# Keycloakサンプルアプリ：ニュースビューアの起動について

# Dockerネットワークの作成

```sh
docker network create my_network
```

# Keycloakの起動と設定

## Keycloakの起動

```sh
docker run -d --name keycloak --network my_network -p 8080:8080 -e KEYCLOAK_USER=admin -e KEYCLOAK_PASSWORD=admin quay.io/keycloak/keycloak:latest
```

## Keycloakの設定

1. ブラウザで `http://localhost:8080` にアクセスし、`admin/admin` でログインします。
2. 新しいRealmを作成します（例: `news_realm`）。
3. 新しいClientを作成します（例: `news_app_client`）。
4. 新しいUserを作成します（例：`basic_user`, `premium_user`）。
5. 新しいRolesを設定します（例：`basic_access`, `premium_access`）。

# `keycloak-quarkus` のビルド

## プロジェクトのクローン

```sh
git clone https://github.com/keijijin/keycloak-quarkus.git
cd keycloak-quarkus
```

## ビルド

```sh
./mvnw clean package
```

# JVMによるDockerイメージの生成

```sh
docker build -f src/main/docker/Dockerfile.jvm -t news-api .
```

# Keycloakと同一ネットワークによるDockerの起動

```sh
docker run --name news-api --network my_network -p 8081:8081 -e QUARKUS_OIDC_AUTH_SERVER_URL=http://keycloak:8080/realms/news_realm/protocol/openid-connect -e QUARKUS_OIDC_CLIENT_ID=news_app_client --rm news-api
```

# Dev ContainerによるDockerネットワークの設定

## `.devcontainer` フォルダの作成

```sh
mkdir .devcontainer
```

## `devcontainer.json` ファイルの作成

```json
{
  "name": "Dev Container",
  "dockerComposeFile": "docker-compose.yml",
  "service": "news-api",
  "workspaceFolder": "/workspace",
  "extensions": [
    "redhat.java",
    "vscjava.vscode-java-pack",
    "vscjava.vscode-spring-initializr",
    "vscjava.vscode-spring-boot-dashboard",
    "vscjava.vscode-spring-boot-microservices",
    "pivotal.vscode-boot-dev-pack"
  ],
  "settings": {
    "terminal.integrated.shell.linux": "/bin/bash"
  },
  "remoteUser": "vscode"
}
```

## `docker-compose.yml` ファイルの作成

```yaml
version: '3.7'
services:
  keycloak:
    image: quay.io/keycloak/keycloak:latest
    environment:
      - KEYCLOAK_USER=admin
      - KEYCLOAK_PASSWORD=admin
    networks:
      - my_network
    ports:
      - "8080:8080"

  news-api:
    build:
      context: .
      dockerfile: src/main/docker/Dockerfile.jvm
    environment:
      - QUARKUS_OIDC_AUTH_SERVER_URL=http://keycloak:8080/realms/news_realm
      - QUARKUS_OIDC_CLIENT_ID=news_app_client
    networks:
      - my_network
    ports:
      - "8081:8081"
    depends_on:
      - keycloak

networks:
  my_network:
    external: true
```

## Dev Containerの起動

1. VSCodeを開き、プロジェクトフォルダを開きます。
2. コマンドパレット（Ctrl+Shift+P）を開き、「Dev Containers: Reopen in Container」を選択します。

# Dev Container で作成した `news-viewer` アプリケーションを Docker イメージにするためには、以下の手順に従って Dockerfile を作成し、ビルドする必要があります。

### 1. Dockerfile の作成

まず、プロジェクトのルートディレクトリに `Dockerfile` を作成します。このファイルには、`news-viewer` アプリケーションの環境を設定するための指示が含まれます。

```Dockerfile
# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Make port 8501 available to the world outside this container
EXPOSE 8501

# Run streamlit when the container launches
CMD ["streamlit", "run", "home.py"]
```

### 2. `requirements.txt` の作成

次に、アプリケーションが依存する Python パッケージを指定する `requirements.txt` ファイルを作成します。例：

```txt
streamlit
requests
# 他の依存パッケージもここに追加
```

### 3. Docker イメージのビルド

ターミナルを開き、プロジェクトのルートディレクトリに移動して、次のコマンドを実行します。

```sh
docker build -t news-viewer .
```

これにより、`news-viewer` という名前の Docker イメージが作成されます。

### 4. Docker イメージの実行

次に、作成した Docker イメージを実行して、アプリケーションをテストします。

```sh
docker run -d --rm -p 8501:8501 --network my_network --name news-viewer news-viewer
```

このコマンドは、アプリケーションをコンテナ内で起動し、ローカルマシンのポート `8501` を使用してアクセスできるようにします。ブラウザで `http://localhost:8501` にアクセスして、アプリケーションが正しく動作することを確認してください。

### 5. Docker Compose で他のサービスと統合

他のサービス（例：Keycloak）と一緒に `news-viewer` を実行するには、`docker-compose.yml` ファイルを作成または更新します。

```yaml
version: '3.7'
services:
  keycloak:
    image: quay.io/keycloak/keycloak:latest
    environment:
      - KEYCLOAK_USER=admin
      - KEYCLOAK_PASSWORD=admin
    networks:
      - my_network
    ports:
      - "8080:8080"

  news-api:
    build:
      context: .
      dockerfile: src/main/docker/Dockerfile.jvm
    environment:
      - QUARKUS_OIDC_AUTH_SERVER_URL=http://keycloak:8080/realms/news_realm/protocol/openid-connect
      - QUARKUS_OIDC_CLIENT_ID=news-app
      - QUARKUS_OIDC_CREDENTIALS_SECRET=mysecret
    networks:
      - my_network
    ports:
      - "8081:8081"
    depends_on:
      - keycloak

  news-viewer:
    build:
      context: .
      dockerfile: Dockerfile
    networks:
      - my_network
    ports:
      - "8501:8501"
    depends_on:
      - news-api

networks:
  my_network:
    external: true
```

### 6. Docker Compose でサービスの起動

次のコマンドを実行して、すべてのサービスを一緒に起動します。

```sh
docker-compose up --build
```

これにより、Keycloak、ニュース API、および `news-viewer` アプリケーションが同じネットワーク内で起動し、相互に通信できるようになります。ブラウザで `http://localhost:8501` にアクセスして、アプリケーションが正しく動作することを確認してください。