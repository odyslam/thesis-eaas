# See https://www.loraserver.io/lora-app-server/install/config/ for a full
# configuration example and documentation.
# LORANK_IP=$(ssh -oStrictHostKeyChecking=no -oUserKnownHostsFile=/dev/null root@172.18.0.1 -p22222 "nslookup lorank8.local" | grep "192" | awk '{print $3}')
# LORANK_IP="192.168.1.64"
# export LORANK_IP
# echo "LORANK IP is: ${LORANK_IP}"

# POSTGRESQL.DSN="postgres://loraserver_as:loraserver_as@${LORANK_IP}:5432/loraserver_as?sslmode=disable"
# REDIS.URL="redis//${LORANK_IP}:6379"
# export POSTGRESQL_URL
# export REDIS_URL

# APPLICATION_SERVER.INTEGRATION.MQTT.SERVER="tcp://${LORANK_IP}:1883"
# export MQTT_SERVER

# APPLICATION_SERVER.API.PUBLIC_HOST="${LORANK_IP}:8001"
# export APP_PUBLIC

# echo "ENV_VARIABLES: \n ${POSTGRESQL_URL}, ${REDIS_URL}, ${APP_PUBLIC}, ${MQTT_SERVER}"
# python create_conf.py
# echo "configuration file created!"
# lora-app-server

ssh -oStrictHostKeyChecking=no -oUserKnownHostsFile=/dev/null -i odyslam_ubuntu.pem -fNT -R 8001:localhost:8001 -N ubuntu@150.140.184.249
echo 'Set reverse ssh tunneling 8001'
ssh -oStrictHostKeyChecking=no -oUserKnownHostsFile=/dev/null -i odyslam_ubuntu.pem -fNT -R 9000:localhost:8080 -N ubuntu@150.140.184.249
echo 'Set reverse ssh tunneling 9000'
echo 'server 150.140.184.249'
lora-app-server