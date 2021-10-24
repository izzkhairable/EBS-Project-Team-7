# set base image (host OS)
FROM python:3.8

# set the working directory in the container
WORKDIR /code

# copy the dependencies file to the working directory
COPY requirements.txt .

# install dependencies
RUN pip install -r requirements.txt
RUN apt-get update
RUN apt install -y libgl1-mesa-glx

# copy the content of the local src directory to the working directory
COPY beach_human_counter_controller.py .

# command to run on container start
CMD [ "python", "./beach_human_counter_controller.py" ]