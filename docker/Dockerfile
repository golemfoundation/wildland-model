FROM ubuntu:18.04

ARG DEBIAN_FRONTEND=noninteractive

RUN apt-get -qqy update

# disable exclusion of man pages
RUN sed -i '/path-exclude=\/usr\/share\/man\/*/c\#path-exclude=\/usr\/share\/man\/*' /etc/dpkg/dpkg.cfg.d/excludes
RUN apt-get install -qqy man manpages locales-all > /dev/null
RUN apt --reinstall install -qqy man-db coreutils > /dev/null

RUN apt-get install -qqy \
    fish tree vim less mc links lynx \
    iproute2 nmap iputils-ping util-linux \
    sudo > /dev/null

RUN apt-get install -qqy \
  curl wget netcat rsync rclone s3cmd awscli python3-boto3 \
  git make \
  imagemagick \
  pandoc pandoc-citeproc \
  poppler-utils qpdf \
  texlive-latex-recommended texlive-fonts-recommended texlive-latex-extra \
  jp2a figlet > /dev/null

RUN apt-get install -qqy \
  python3-pygraphviz \
  > /dev/null

RUN apt-get install -qqy \
    python3-networkx \
    python3-pygraphviz \
    python3-matplotlib \
    dot2tex \
    > /dev/null

ADD init.sh /

RUN useradd -s /usr/bin/fish -m user

CMD ["/init.sh"]
