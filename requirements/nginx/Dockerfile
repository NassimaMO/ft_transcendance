FROM nginx:1.27.0

RUN mkdir -p /etc/nginx/conf.d && rm -f /etc/nginx/conf.d/default.conf

COPY ./conf/nginx.conf /etc/nginx/conf.d

RUN mkdir -p /etc/nginx/ssl && \
    openssl req -x509 -nodes -out /etc/nginx/ssl/cert.crt \
    -keyout /etc/nginx/ssl/cert.key \
    -subj "/C=FR/ST=IDF/L=Paris/O=42/OU=42/CN=localhost"

CMD ["nginx", "-g", "daemon off;"]