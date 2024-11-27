FROM python:3.12

# # Set the timezone environment variable
# ENV TZ=Asia/Yekaterinburg
# ENV DEBIAN_FRONTEND=noninteractive

# # Install tzdata and set the timezone
# RUN apt-get update && \
#     apt-get install -y tzdata && \
#     cp /usr/share/zoneinfo/$TZ /etc/localtime && \
#     echo $TZ > /etc/timezone

WORKDIR /app

COPY . /app/

RUN pip install -r requirements.txt

CMD ["python", "src/bot.py"]