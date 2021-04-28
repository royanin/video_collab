FROM python:3.9.2
COPY ./app /app
COPY .env .
EXPOSE 5000

ENV STATIC_URL /app/static
ENV STATIC_PATH /var/www/app/static
COPY ./requirements.txt /var/www/requirements.txt
RUN /usr/local/bin/python -m pip install -r /var/www/requirements.txt
CMD ["/usr/local/bin/python", "./app/main.py"]
