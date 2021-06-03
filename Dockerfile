FROM python:3.8-alpine
ENV PYTHONBUFFERED=0
EXPOSE 5000/tcp
WORKDIR /usr/src/app
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
CMD [ "python3", "app.py" ]
COPY *.py ./

