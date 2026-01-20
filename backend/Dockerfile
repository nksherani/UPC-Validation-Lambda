FROM public.ecr.aws/lambda/python:3.12

# Build zbar from source (EPEL packages are not compatible with the AL2023 base).
RUN set -eux; \
    microdnf update -y; \
    microdnf install -y findutils tar gzip curl-minimal glibc-langpack-en \
        gcc gcc-c++ make automake autoconf libtool pkgconfig gettext gettext-devel cmake \
        libjpeg-turbo libjpeg-turbo-devel zlib zlib-devel \
        libpng libpng-devel libtiff libtiff-devel libwebp libwebp-devel \
        giflib giflib-devel; \
    cd /tmp; \
    curl -L -o zbar.tar.gz https://github.com/mchehab/zbar/archive/refs/tags/0.23.92.tar.gz; \
    tar -xzf zbar.tar.gz; \
    cd zbar-0.23.92; \
    if [ -x ./configure ]; then :; else autoreconf -vfi; fi; \
    ./configure --without-imagemagick --without-gtk --without-qt --disable-video --without-x --without-python --without-java; \
    make -j"$(nproc)"; \
    make install; \
    ln -sf /usr/local/lib/libzbar.so /usr/lib64/libzbar.so || true; \
    ln -sf /usr/local/lib/libzbar.so.0 /usr/lib64/libzbar.so.0 || true; \
    cd /tmp; \
    curl -L -o leptonica.tar.gz https://github.com/DanBloomberg/leptonica/archive/refs/tags/1.84.1.tar.gz; \
    tar -xzf leptonica.tar.gz; \
    cd leptonica-1.84.1; \
    ./autogen.sh; \
    ./configure; \
    make -j"$(nproc)"; \
    make install; \
    /sbin/ldconfig || true; \
    cd /tmp; \
    curl -L -o tesseract.tar.gz https://github.com/tesseract-ocr/tesseract/archive/refs/tags/5.4.1.tar.gz; \
    tar -xzf tesseract.tar.gz; \
    cd tesseract-5.4.1; \
    ./autogen.sh; \
    export PKG_CONFIG_PATH="/usr/local/lib/pkgconfig${PKG_CONFIG_PATH:+:${PKG_CONFIG_PATH}}"; \
    export LDFLAGS="-L/usr/local/lib"; \
    export CPPFLAGS="-I/usr/local/include"; \
    ./configure; \
    make -j"$(nproc)"; \
    make install; \
    /sbin/ldconfig || true; \
    cd /; \
    mkdir -p /usr/local/share/tessdata; \
    curl -L -o /usr/local/share/tessdata/eng.traineddata \
        https://github.com/tesseract-ocr/tessdata_fast/raw/main/eng.traineddata; \
    rm -rf /tmp/zbar-0.23.92 /tmp/zbar.tar.gz /tmp/leptonica-1.84.1 /tmp/leptonica.tar.gz /tmp/tesseract-5.4.1 /tmp/tesseract.tar.gz; \
    microdnf remove -y gcc make automake autoconf libtool pkgconfig gettext cmake \
        libjpeg-turbo-devel zlib-devel libpng-devel libtiff-devel libwebp-devel \
        giflib-devel || true; \
    microdnf clean all; \
    rm -rf /var/cache/dnf /var/cache/yum

# Ensure runtime can find libzbar
ENV LD_LIBRARY_PATH="/usr/local/lib:/usr/lib64:${LD_LIBRARY_PATH}"
ENV TESSDATA_PREFIX="/usr/local/share/tessdata"

# Install Python dependencies
WORKDIR ${LAMBDA_TASK_ROOT}
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY app ./app

# Set the Lambda handler
CMD ["app.main.lambda_handler"]

