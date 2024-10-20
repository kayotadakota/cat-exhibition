FROM python:3.12-slim
WORKDIR /usr/local/app

COPY requirements.txt /usr/local/app/
RUN python3 -m pip install --no-cache-dir -r requirements.txt

COPY ./ /usr/local/app/

RUN useradd guest
USER guest

CMD ["python3", "manage.py", "runserver", "0.0.0.0:8000"]