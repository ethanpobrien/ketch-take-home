FROM python:3.12-slim

RUN apt-get update && apt-get install gcc postgresql curl -y
WORKDIR /app
COPY . /app
RUN pip install -r requirements.txt

CMD ["/bin/bash"]
