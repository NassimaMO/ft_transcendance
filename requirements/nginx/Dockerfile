FROM nginx:latest

COPY ./conf/nginx.conf /etc/nginx/conf.d
RUN mkdir -p /etc/nginx/conf.d && rm -f /etc/nginx/conf.d/default.conf

RUN mkdir -p /etc/nginx/ssl

RUN openssl req -x509 -nodes -out /etc/nginx/ssl/cert.crt \
    -keyout /etc/nginx/ssl/cert.key \
    -subj "/C=FR/ST=IDF/L=Paris/O=42/OU=42/CN=mysite.local"

CMD ["nginx", "-g", "daemon off;"]