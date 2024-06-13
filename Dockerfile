# Define custom function directory
ARG FUNCTION_DIR="/function"

FROM python:3.10-slim as build-image

# Include global arg in this stage of the build
ARG FUNCTION_DIR
ARG TARGETPLATFORM
ARG BUILD_NODE_ENV production

RUN echo "Target architecture: $TARGETPLATFORM" > /log

# Copy function code
RUN mkdir -p ${FUNCTION_DIR}
COPY . ${FUNCTION_DIR}

RUN apt-get update -y
RUN apt-get install curl python3-dev libglu1-mesa libxi-dev libxmu-dev libglu1-mesa-dev \
    libxrender1 libxcursor1 libxft2 libxinerama1 libgomp1 ca-certificates openssl -y
RUN curl -fsSL https://deb.nodesource.com/setup_20.x | bash -
RUN apt-get install nodejs -y
RUN npm i -g pnpm

# Install the function's dependencies
RUN pip install \
    --target ${FUNCTION_DIR} \
    awslambdaric

# required libs for parser
RUN pip install --upgrade gmsh==4.13.1
RUN pip install "trimesh[easy]"==3.16.0



# Use a slim version of the base Python image to reduce the final image size
FROM python:3.10-slim

ARG TARGETPLATFORM
ARG BUILD_NODE_ENV production

RUN echo "Target architecture: $TARGETPLATFORM" > /log

RUN apt-get update -y
RUN apt-get install curl python3-dev libglu1-mesa libxi-dev libxmu-dev libglu1-mesa-dev \
    libxrender1 libxcursor1 libxft2 libxinerama1 libgomp1 ca-certificates openssl -y
RUN curl -fsSL https://deb.nodesource.com/setup_20.x | bash -
RUN apt-get install nodejs -y
RUN npm i -g pnpm

# required libs for parser
RUN pip install --upgrade gmsh==4.11.1
RUN pip install "trimesh[easy]"==3.16.0
RUN pip install boto3

# Include global arg in this stage of the build
ARG FUNCTION_DIR
# Set working directory to function root directory
WORKDIR ${FUNCTION_DIR}

# Copy in the built dependencies
COPY --from=build-image ${FUNCTION_DIR} ${FUNCTION_DIR}

# Set runtime interface client as default command for the container runtime
ENTRYPOINT [ "/usr/local/bin/python", "-m", "awslambdaric" ]
# Pass the name of the function handler as an argument to the runtime
CMD [ "lambda_function.lambda_handler" ]
