FROM python:3.6-slim-stretch

RUN apt update -y; apt install -y \
    git \
    cmake \
    libsm6 \
    libxext6 \
    libxrender-dev \
    software-properties-common \
    gcc \
    g++ \
    && apt-get clean && rm -rf /tmp/* /var/tmp/*

#Install dlib 
RUN cd ~ && \
    mkdir -p dlib && \
    git clone https://github.com/davisking/dlib.git dlib/ && \
    cd  dlib/ && \
    python3 setup.py install && \
    cd ..

# Install requirements
ADD requirements.txt .
RUN pip3 install -r requirements.txt

RUN mkdir -p app && \
	git clone https://github.com/pumpkinsuu/api-server.git app/
	cd app/