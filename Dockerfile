FROM python:3.8

# First install requirements
WORKDIR /app
ADD ./src/requirements.txt /app/requirements.txt
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Then copy stuff
ADD ./src /app

# Run bot
CMD python main.py


