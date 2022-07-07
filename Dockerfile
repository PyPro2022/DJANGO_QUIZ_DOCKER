FROM python:3.10.5-slim

RUN apt update  \
    && apt install mc vim -y

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

#ENV SECRET_KEY=django-insecure-!e#ul1lx(g9nsaf^*hm9geqc1@7vuvx@sanp+zp*=q#nn#$dbq
ENV SECRET_KEY=django-insecure-t@y-u@+vwo1y9-osnt94k17-_6mng05u5z^(pyk%c*p#$ys7!6
ENV DEBUG=True
ENV ALLOWED_HOSTS=''

RUN mkdir /opt/src
WORKDIR /opt/src

COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install -r requirements.txt
RUN rm -f requirements.txt

COPY src .

EXPOSE 8090

CMD python manage.py runserver 0.0.0.0:8090
