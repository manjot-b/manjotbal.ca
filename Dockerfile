### Builder stage ###
FROM python:3.13 AS builder

WORKDIR /app

COPY . .

RUN python -m pip install Jinja2 PyYAML minify-html rcssmin
RUN python build.py

### Deploy stage ###
FROM nginx:alpine AS deploy

COPY --from=builder /app/output/ /usr/share/nginx/html
COPY config/nginx/nginx.conf /etc/nginx/
COPY config/nginx/default.conf /etc/nginx/conf.d/

EXPOSE 8080
