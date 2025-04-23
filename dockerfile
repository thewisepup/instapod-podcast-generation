FROM public.ecr.aws/lambda/python:3.11
COPY lambda_handler.py ${LAMBDA_TASK_ROOT}
COPY requirements.txt ${LAMBDA_TASK_ROOT}
COPY utils ${LAMBDA_TASK_ROOT}/utils
COPY podcastfy ${LAMBDA_TASK_ROOT}/podcastfy
RUN pip3 install -r requirements.txt
CMD [ "lambda_handler.lambda_handler" ]
