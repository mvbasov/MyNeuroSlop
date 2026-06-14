# syntax=docker/dockerfile:1
FROM golang:1.25-bookworm

# Prevent interactive prompts during apt installations
ENV DEBIAN_FRONTEND=noninteractive

# Tell apt to keep downloaded packages in the cache rather than cleaning them up
RUN rm -f /etc/apt/apt.conf.d/docker-clean; echo 'Binary::apt::APT::Keep-Downloaded-Packages "true";' > /etc/apt/apt.conf.d/keep-cache

# 1. Install Linux UI Dependencies (BOTH GTK3 and GTK4 for Wails v3 Alpha), Node.js, and Java
# We mount the apt caches so package downloads are saved across rebuilds
RUN --mount=type=cache,target=/var/cache/apt,sharing=locked \
    --mount=type=cache,target=/var/lib/apt,sharing=locked \
    apt-get update && apt-get install -y \
    build-essential \
    libgtk-3-dev \
    libwebkit2gtk-4.1-dev \
    libgtk-4-dev \
    libwebkitgtk-6.0-dev \
    pkg-config \
    curl \
    git \
    unzip \
    openjdk-17-jdk \
    && curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
    && apt-get install -y nodejs

# 2. Setup Android SDK & NDK Environment Variables
ENV ANDROID_HOME=/opt/android-sdk
ENV PATH=${PATH}:${ANDROID_HOME}/cmdline-tools/latest/bin:${ANDROID_HOME}/platform-tools
ENV ANDROID_NDK_HOME=${ANDROID_HOME}/ndk/26.1.10909125

# 3. Download and Install Android Command Line Tools
RUN mkdir -p ${ANDROID_HOME}/cmdline-tools && \
    cd ${ANDROID_HOME}/cmdline-tools && \
    curl -o commandlinetools.zip https://dl.google.com/android/repository/commandlinetools-linux-11076708_latest.zip && \
    unzip commandlinetools.zip && \
    rm commandlinetools.zip && \
    mv cmdline-tools latest

# 4. Accept Android Licenses and Install SDK Components
RUN yes | sdkmanager --licenses && \
    sdkmanager "platform-tools" "platforms;android-34" "build-tools;34.0.0" "ndk;26.1.10909125"

# 5. Install Wails v3 (Experimental)
# We mount the Go module and build caches to massively speed up future toolchain compiles
RUN --mount=type=cache,target=/go/pkg/mod \
    --mount=type=cache,target=/root/.cache/go-build \
    go install github.com/wailsapp/wails/v3/cmd/wails3@master

# Set the working directory for your mapped code
WORKDIR /workspace

# Keep the container alive for development
CMD ["tail", "-f", "/dev/null"]
