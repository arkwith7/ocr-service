# Dockerizing Django with Postgres, Gunicorn, and Nginx

## Want to learn how to build this?

Check out the [post](https://testdriven.io/dockerizing-django-with-postgres-gunicorn-and-nginx).

## Want to use this project?

### Development

Uses the default Django development server.

1. Rename *.env.dev-sample* to *.env.dev*.
1. Update the environment variables in the *docker-compose.yml* and *.env.dev* files.
1. Build the images and run the containers:

    ```sh
    $ docker-compose up -d --build
    ```

    Test it out at [http://localhost:8000](http://localhost:8000). The "app" folder is mounted into the container and your code changes apply automatically.

#### Local Development Environment
1. ~/cocoa/Dockerfile 우분투 설치 라이브러리 참조
2. 프로젝트 루트 디렉토리에 파이선 가상환경(~/venv) 설치(python -m venv venv)
3. vscode 익스텐션 설치
   - remote wsl, docker, Python, json, jupyter, SQLite 
### Production

Uses gunicorn + nginx.

1. Rename *.env.prod-sample* to *.env.prod* and *.env.prod.db-sample* to *.env.prod.db*. Update the environment variables.
1. Build the images and run the containers:

    ```sh
    $ docker-compose -f docker-compose.prod.yml up -d --build
    ```

    Test it out at [http://localhost:1337](http://localhost:1337). No mounted folders. To apply changes, the image must be re-built.

### Github 초기화 등록

1. 로컬 저장소의 .git 디렉토리 삭제
2. 잘못된 파일 삭제 or 수정 후 로컬 저장소에서 다시 git init 수행 → 초기화!
3. 초기화에 등록될 파일 추가 
```
git add .
```
4. 초기화에 등록될 파일 커밋
```
git commit -m "커밋 메시지"
```
5. 초기화 시킬 원격 저장소 추가
```
git remote add origin "url"
```
6. 현재 상태를 원격 저장소에 적용
```
git push --force --set-upstream origin master
```
(이를 통해 git pull 없이 강제로 병합)
