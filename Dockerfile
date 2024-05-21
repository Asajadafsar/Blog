FROM python:3.11
WORKDIR /blog
COPY . /blog

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

EXPOSE 8000
#test=http://localhost:8000/



ENV DJANGO_SETTINGS_MODULE=blog.settings
ENV PYTHONUNBUFFERED 1

CMD ["gunicorn", "--bind", "0.0.0.0:8000", "myproject.wsgi:application"]
# CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]



#run 
#docker-compose build
#OFF comment