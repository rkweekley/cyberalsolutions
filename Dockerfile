FROM joseluisq/static-web-server:2-alpine 

COPY . /home/sws/public

EXPOSE 80
