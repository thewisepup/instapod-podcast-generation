FROM public.ecr.aws/lambda/python:3.11
RUN yum update -y && \
    yum install -y wget tar xz && \
    wget https://johnvansickle.com/ffmpeg/releases/ffmpeg-release-arm64-static.tar.xz && \
    tar xvf ffmpeg-release-arm64-static.tar.xz && \
    mv ffmpeg-*-arm64-static/ffmpeg /usr/local/bin/ && \
    mv ffmpeg-*-arm64-static/ffprobe /usr/local/bin/ && \
    chmod +x /usr/local/bin/ffmpeg && \
    chmod +x /usr/local/bin/ffprobe && \
    rm -rf ffmpeg-*-arm64-static* && \
    yum clean all


COPY requirements.txt ${LAMBDA_TASK_ROOT}
RUN pip3 install -r requirements.txt

COPY lambda_handler.py ${LAMBDA_TASK_ROOT}
COPY utils ${LAMBDA_TASK_ROOT}/utils
COPY podcastfy ${LAMBDA_TASK_ROOT}/podcastfy

CMD [ "lambda_handler.lambda_handler" ]
 