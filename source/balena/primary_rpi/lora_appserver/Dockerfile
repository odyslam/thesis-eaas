FROM balenalib/raspberrypi3-64-debian:latest-run



RUN apt-get update && apt-get install -y --no-install-recommends curl 
RUN curl https://artifacts.loraserver.io/packages/3.x/deb/pool/main/l/lora-app-server/lora-app-server_3.2.0_linux_arm64.deb -o lora_app.deb -s \ 
&& dpkg -i lora_app.deb && rm -f lora_app.deb \
&& apt-get -y remove --purge curl \
&& apt-get -y autoclean 
RUN apt-get install -y --no-install-recommends openssh-client
# RUN apt-get install -y --no-install-recommends openssh-client

RUN mkdir -p /usr/home
WORKDIR /usr/home

COPY ./configuration/. /etc/lora-app-server/
COPY init_lora-app-server.sh ./
COPY odyslam_ubuntu.pem ./
RUN ["chmod", "+x", "init_lora-app-server.sh"]
CMD ["./init_lora-app-server.sh"]
# CMD ["lora-app-server"]

# ENV PROJECT_PATH=/lora-app-server
# ENV PATH=$PATH:$PROJECT_PATH/build
# ENV CGO_ENABLED=0
# ENV GO_EXTRA_BUILD_ARGS="-a -installsuffix cgo"

# RUN apk --update add --no-cache ca-certificates make git bash protobuf alpine-sdk
# RUN apk --no-cache add nodejs npm
# RUN apk --no-cache add curl  

# WORKDIR $GOPATH
# RUN go get -u -v github.com/jteeuwen/go-bindata
# RUN go install github.com/jteeuwen/go-bindata


# RUN mkdir -p $PROJECT_PATH
# COPY . $PROJECT_PATH
# WORKDIR $PROJECT_PATH



# RUN make requirements 
# RUN make ui-requirements
# RUN make

# WORKDIR /root/
# COPY --from=development /lora-app-server/build/lora-app-server .
# ENTRYPOINT ["./lora-app-server"]


# ENV container docker
# RUN apt-get update && apt-get install -y --no-install-recommends \
#         systemd \
#     && rm -rf /var/lib/apt/lists/*

# # We never want these to run in a container
# # Feel free to edit the list but this is the one we used
# RUN systemctl mask \
#     dev-hugepages.mount \
#     sys-fs-fuse-connections.mount \
#     sys-kernel-config.mount \

#     display-manager.service \
#     getty@.service \
#     systemd-logind.service \
#     systemd-remount-fs.service \

#     getty.target \
#     graphical.target

# COPY entry.sh /usr/bin/entry.sh
# COPY resin.service /etc/systemd/system/resin.service

# RUN systemctl enable /etc/systemd/system/resin.service

# STOPSIGNAL 37
# VOLUME ["/sys/fs/cgroup"]
# ENTRYPOINT ["/usr/bin/entry.sh"]
