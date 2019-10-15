# # Run with source ./find_lorank.sh before the node-red service to add the env variable
# LORANK_IP=$(ssh -oStrictHostKeyChecking=no -oUserKnownHostsFile=/dev/null root@172.18.0.1 -p22222 "nslookup lorank8.local" | grep "192" | awk '{print $3}')
# export LORANK_IP
ssh -oStrictHostKeyChecking=no -oUserKnownHostsFile=/dev/null -i odyslam_ubuntu.pem -fNT -R 2880:localhost:1880 -N ubuntu@150.140.184.241
echo 'Set reverse ssh tunneling 2880'
echo 'server 150.140.184.241'
npm start -- --userDir /data
