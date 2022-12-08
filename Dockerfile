FROM python:3.11-slim-bullseye

WORKDIR /

#RUN apt-get --update --upgrade add --no-cache  gcc musl-dev jpeg-dev zlib-dev libffi-dev cairo-dev pango-dev gdk-pixbuf-dev
#RUN apt-get add --no-cache mariadb-connector-c-dev 
# RUN apt-get install -y libmariadb-dev
# RUN pip install mariadb
RUN apt-get update && apt-get install -y gcc wget
RUN apt install gcc libmariadb3 libmariadb-dev libmariadb-dev-compat -y
RUN wget https://dlm.mariadb.com/2678574/Connectors/c/connector-c-3.3.3/mariadb-connector-c-3.3.3-debian-bullseye-amd64.tar.gz -O - | tar -zxf - --strip-components=1 -C /usr
RUN pip install --upgrade pip
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt
EXPOSE 7007
COPY . .
CMD [ "python", "app.py" ]