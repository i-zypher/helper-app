# Use a base Ubuntu image compatible with GitHub runners
FROM ubuntu:22.04

# Avoid interactive prompts during package installation
ENV DEBIAN_FRONTEND=noninteractive

# Install essential system packages, Python, Java 17, and other build dependencies
# Added common libraries often needed by Python packages
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    git \
    zip \
    unzip \
    openjdk-17-jdk \
    python3.11 \
    python3.11-venv \
    python3-pip \
    libffi-dev \
    libssl-dev \
    build-essential \
    libsqlite3-dev \
    zlib1g-dev \
    libncursesw5-dev \
    libgdbm-dev \
    libnss3-dev \
    libreadline-dev \
    libbz2-dev \
    liblzma-dev \
    && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Set Java 17 as default
ENV JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64
RUN update-alternatives --install /usr/bin/java java ${JAVA_HOME}/bin/java 1 && \
    update-alternatives --set java ${JAVA_HOME}/bin/java

# Set up Android SDK variables
ENV SDK_ROOT=/opt/android-sdk
ENV ANDROID_HOME=${SDK_ROOT}
ENV ANDROID_SDK_ROOT=${SDK_ROOT}
ENV NDK_VERSION=25b
ENV ANDROID_NDK_HOME=${SDK_ROOT}/ndk/${NDK_VERSION}
ENV ANDROID_NDK_ROOT=${ANDROID_NDK_HOME}
ENV BUILD_TOOLS_VERSION=33.0.2

# Download and set up Android SDK command-line tools
# Using a specific version URL for stability
RUN mkdir -p ${SDK_ROOT}/cmdline-tools && \
    wget https://dl.google.com/android/repository/commandlinetools-linux-11076708_latest.zip -O cmdline-tools.zip && \
    unzip cmdline-tools.zip -d ${SDK_ROOT}/cmdline-tools && \
    mv ${SDK_ROOT}/cmdline-tools/cmdline-tools ${SDK_ROOT}/cmdline-tools/latest && \
    rm cmdline-tools.zip

# Define absolute path to sdkmanager and add tools to PATH
ENV SDKMANAGER_CMD=${SDK_ROOT}/cmdline-tools/latest/bin/sdkmanager
ENV PATH=${PATH}:${SDK_ROOT}/cmdline-tools/latest/bin:${SDK_ROOT}/platform-tools:${SDK_ROOT}/build-tools/${BUILD_TOOLS_VERSION}:${ANDROID_NDK_HOME}

# Install required SDK packages and accept licenses
# Use || true for license acceptance as it can return non-zero exit codes
RUN yes | ${SDKMANAGER_CMD} --licenses --sdk_root=${SDK_ROOT} || true && \
    ${SDKMANAGER_CMD} --install "platform-tools" "build-tools;${BUILD_TOOLS_VERSION}" "ndk;${NDK_VERSION}" --sdk_root=${SDK_ROOT}

# Verify installation (optional but good practice)
RUN ${SDKMANAGER_CMD} --list_installed --sdk_root=${SDK_ROOT}

# Install Python build tools
RUN pip3 install --no-cache-dir --upgrade pip && \
    pip3 install --no-cache-dir buildozer cython

# Set working directory for the application code
WORKDIR /app

# (Optional) Define a default command if you were running the container directly
# CMD ["buildozer", "android", "debug"]

