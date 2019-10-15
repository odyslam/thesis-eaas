FROM balenalib/raspberrypi3-64-alpine-node:latest-build as build 
# FROM nodered/node-red-docker:slim
RUN mkdir -p /usr/src/node-red
RUN mkdir /data

# User data directory, contains flows, config and nodes.


WORKDIR /usr/src/node-red

# Add node-red user so we aren't running as root.
# RUN adduser -h /usr/src/node-red -D -H node-red \
#     && chown -R node-red:node-red /data \
#     && chown -R node-red:node-red /usr/src/node-red

# USER node-red

# package.json contains Node-RED NPM module and node dependencies
COPY package.json /usr/src/node-red/
RUN npm install

FROM balenalib/raspberrypi3-64-alpine-node:latest-run

RUN apk update && apk add --no-cache openssh-client 
RUN mkdir -p /usr/src/node-red
RUN mkdir /data
WORKDIR /usr/src/node-red

COPY --from=build  /usr/src/node-red /usr/src/node-red
COPY --from=build /data /data
COPY --from=build /usr/local/bin /usr/local/bin
COPY --from=build /usr/local/lib/node_modules /usr/local/lib/node_modules


# User configuration directory volume

COPY flows.json /data/
COPY settings.js /data/
COPY start_node.sh /usr/src/node-red/
COPY odyslam_ubuntu.pem /usr/src/node-red/
COPY generic_lora_device_profile.yaml /data/
RUN ["chmod", "+x", "start_node.sh"]

# Environment variable holding file path for flows configuration

# CMD ["source ./start_script.sh"]
## start script :
# 1) get lorank ip
# 2)save ip as env variable
# 3) start npm as here
# CMD [""npm", "start", "--", "--userDir", "/data""]
CMD ["./start_node.sh"]