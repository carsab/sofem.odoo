FROM ubuntu:jammy
LABEL MAINTAINER="Sofem Ltda <contacto@sofem.co>"
ARG UID=999
SHELL ["/bin/bash", "-xo", "pipefail", "-c"]

# Generate locale C.UTF-8 for postgres and general locale data
ENV LANG=en_US.UTF-8

# Retrieve the target architecture to install the correct wkhtmltopdf package
ARG TARGETARCH

# Install some deps, lessc and less-plugin-clean-css, and wkhtmltopdf
RUN apt-get update && \
    DEBIAN_FRONTEND=noninteractive \
    apt-get install -y --no-install-recommends \
        ca-certificates \
        curl \
        dirmngr \
        fonts-noto-cjk \
        gnupg \
        libssl-dev \
        node-less \
        npm \
        vim \
        git \
        wget \
        xz-utils && \
    apt install -y --no-install-recommends build-essential zlib1g-dev libncurses5-dev libgdbm-dev libnss3-dev libsqlite3-dev libreadline-dev libffi-dev curl libbz2-dev  python3-pip libldap2-dev libpq-dev libsasl2-dev && \
    apt-get install -y --no-install-recommends libmagic-mgc libmagic1 gettext libpq5 python3-dev libsasl2-dev libssl-dev checkinstall && \
    if [ -z "${TARGETARCH}" ]; then \
        TARGETARCH="$(dpkg --print-architecture)"; \
    fi; \
    WKHTMLTOPDF_ARCH=${TARGETARCH} && \
    case ${TARGETARCH} in \
    "amd64") WKHTMLTOPDF_ARCH=amd64 && WKHTMLTOPDF_SHA=967390a759707337b46d1c02452e2bb6b2dc6d59  ;; \
    "arm64")  WKHTMLTOPDF_SHA=90f6e69896d51ef77339d3f3a20f8582bdf496cc  ;; \
    "ppc64le" | "ppc64el") WKHTMLTOPDF_ARCH=ppc64el && WKHTMLTOPDF_SHA=5312d7d34a25b321282929df82e3574319aed25c  ;; \
    esac \
    && curl -o wkhtmltox.deb -sSL https://github.com/wkhtmltopdf/packaging/releases/download/0.12.6.1-3/wkhtmltox_0.12.6.1-3.jammy_${WKHTMLTOPDF_ARCH}.deb \
    && echo ${WKHTMLTOPDF_SHA} wkhtmltox.deb | sha1sum -c - \
    && apt-get install -y --no-install-recommends ./wkhtmltox.deb \
    && rm -rf /var/lib/apt/lists/* wkhtmltox.deb

# Install python
ENV PYTHON_VERSION=3.11.10
RUN apt-get update \
    && wget https://www.python.org/ftp/python/$PYTHON_VERSION/Python-$PYTHON_VERSION.tar.xz \
        && tar -xf Python-$PYTHON_VERSION.tar.xz \
        && mv Python-$PYTHON_VERSION /opt/ \
        && cd /opt/Python-$PYTHON_VERSION/ \
        && ./configure --enable-optimizations --enable-shared \
        && make \
        && make -j 4 \
        && make altinstall \
        && ldconfig /opt/Python-$PYTHON_VERSION \
        && python3 --version \
        && pip3 --version \
        &&  rm -rf Python-$PYTHON_VERSION.tar.xz

# RUN apt-get install -y --no-install-recommends libmagic-mgc libmagic1 gettext libpq5 python3-dev libsasl2-dev libssl-dev checkinstall
# RUN update-alternatives --install /usr/bin/python python3 /usr/bin/python3 20
# RUN update-alternatives --install /usr/bin/python python3 /opt/Python-$PYTHON_VERSION/python 10
# RUN update-alternatives --set python3 /opt/Python-$PYTHON_VERSION/python

RUN unlink /usr/bin/python3 && \
    ln -s /opt/Python-$PYTHON_VERSION/python /usr/bin/python3  && \
    python3 --version

# install latest postgresql-client
RUN echo 'deb http://apt.postgresql.org/pub/repos/apt/ jammy-pgdg main' > /etc/apt/sources.list.d/pgdg.list \
    && GNUPGHOME="$(mktemp -d)" \
    && export GNUPGHOME \
    && repokey='B97B0AFCAA1A47F044F244A07FCC7D46ACCC4CF8' \
    && gpg --batch --keyserver keyserver.ubuntu.com --recv-keys "${repokey}" \
    && gpg --batch --armor --export "${repokey}" > /etc/apt/trusted.gpg.d/pgdg.gpg.asc \
    && gpgconf --kill all \
    && rm -rf "$GNUPGHOME" \
    && apt-get update  \
    && apt-get install --no-install-recommends -y postgresql-client \
    && rm -f /etc/apt/sources.list.d/pgdg.list \
    && rm -rf /var/lib/apt/lists/*

# Install another libraries
RUN apt-get update\
  && mkdir -p /odoo /var/log/odoo /odoo/data /odoo/addons /odoo/custom-addons /etc/odoo \
  && npm install -g rtlcss

# create odoo user
RUN adduser --disabled-password -uid $UID --gecos 'odoo ERP' odoo \
  && usermod odoo --home /odoo \
  && chown -R odoo:odoo /odoo /var/log/odoo /odoo/data /odoo/addons /odoo/custom-addons

# Install Odoo from source
#COPY .  /odoo
COPY  --chown=odoo:odoo .  /odoo

# Install dependencies
RUN  pip3 install -r /odoo/requirements.txt

# Copy entrypoint script and Odoo configuration file
COPY --chmod=777 ./entrypoint.sh /
COPY --chmod=777 ./sofem.conf /etc/odoo/

#chown -R odoo:odoo
#find /odoo -type d -exec chown odoo:odoo {} + \ &&

# Set permissions and Mount /var/lib/odoo to allow restoring filestore and /mnt/extra-addons for users addons
# RUN find /odoo/custom-addons -type d -exec chown odoo:odoo {} +

#VOLUME ["/odoo/data","/odoo/addons","/odoo/custom-addons"]

# Expose Odoo services
EXPOSE 8069 8071 8072

# Set the default config file
ENV ODOO_RC=/etc/odoo/sofem.conf

COPY --chmod=777 wait-for-psql.py /usr/local/bin/wait-for-psql.py

# Set default user when running the container
USER odoo

ENTRYPOINT ["/entrypoint.sh"]
CMD ["/odoo/odoo-bin"]
