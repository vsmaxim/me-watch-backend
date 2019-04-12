# me_watch

Service for watching video from different sources.

## How to setup

First of all, you need docker and docker-compose cli tools 
to build docker image and run containers.

Create django_config.env file in root directory. (Environment variables are described
in django_config.env part)

The setup steps are pretty easy:
1. Make sure docker.service is up and running
2. Run `docker-compose build`
3. Run  `docker-compose up -d`

Development server must be accessible via `localhost:8000`

## django_config.env

File from which environment variables for docker container 
are pulled.

```env
# Secret key used by django to generate passwords
SECRET_KEY=
# Client ID of VK application
VK_CLIENT_ID=
# Client secret of VK application
VK_CLIENT_SECRET=
# Auth url used for VK OAuth2
VK_AUTH_URL=
# Token url used for VK OAuth2
VK_TOKEN_URL=
```