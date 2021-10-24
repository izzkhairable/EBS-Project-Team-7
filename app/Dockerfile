FROM python:3.7

RUN mkdir /app
WORKDIR /app
ADD . /app/
RUN pip install -r requirements.txt
RUN apt-get update
RUN apt install -y libgl1-mesa-glx

EXPOSE 5000
CMD ["python", "/app/main.py"]
