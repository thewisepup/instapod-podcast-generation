FROM public.ecr.aws/lambda/python:3.11
RUN yum update -y && \
    yum install -y wget tar xz && \
    wget https://johnvansickle.com/ffmpeg/releases/ffmpeg-release-amd64-static.tar.xz && \
    tar xvf ffmpeg-release-amd64-static.tar.xz && \
    mv ffmpeg-*-amd64-static/ffmpeg /usr/local/bin/ && \
    mv ffmpeg-*-amd64-static/ffprobe /usr/local/bin/ && \
    rm -rf ffmpeg-*-amd64-static* && \
    yum clean all
COPY lambda_handler.py ${LAMBDA_TASK_ROOT}
COPY requirements.txt ${LAMBDA_TASK_ROOT}
COPY utils ${LAMBDA_TASK_ROOT}/utils
COPY podcastfy ${LAMBDA_TASK_ROOT}/podcastfy
RUN pip3 install -r requirements.txt
CMD [ "lambda_handler.lambda_handler" ]
