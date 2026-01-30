# use the latest Alpine Linux image as the base
FROM alpine:latest

# setup the container
RUN apk update && apk add --no-cache \
    python3 \
    python3-dev \
    git \
    clang \
    pkgconfig \
    freetype \
    make \
    g++

RUN mkdir wikip_test
WORKDIR "/wikip_test"

RUN git clone https://github.com/ghaerr/agg-2.6.git
WORKDIR "/wikip_test/agg-2.6/agg-src"
RUN make
RUN cp ./src/libagg.a /usr/lib/libagg.a
RUN rm -rf /wikip_test/agg-2.6/

WORKDIR "/wikip_test"
RUN git clone https://github.com/elektrobohemian/CulturalAnalytics.git
WORKDIR "/wikip_test/CulturalAnalytics"
RUN python3 -m venv ./venv
RUN source ./venv/bin/activate && pip install --upgrade pip &&pip3 install -r requirements.txt

RUN apk del python3-dev clang pkgconfig make g++

EXPOSE 8888
EXPOSE 8000

WORKDIR "/wikip_test/CulturalAnalytics"
ADD start_jupyter_in_container.sh /wikip_test/CulturalAnalytics/start_jupyter_in_container.sh
CMD ["/bin/sh", "/wikip_test/CulturalAnalytics/start_jupyter_in_container.sh"]

# after activationg the virtual environment, the jupyter notebook can be started with:
# source ./venv/bin/activate
# jupyter notebook --ip=0.0.0.0 --port=8888 --no-browser --allow-root --NotebookApp.token='' --NotebookApp.password=''

