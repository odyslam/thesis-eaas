import os 
import toml


post = os.environ.get("POSTGRESQL_URL")
redis = os.environ.get("REDIS_URL")
app = os.environ.get("APP_PUBLIC")
mqtt = os.environ.get("MQTT_SERVER")


# create configuration file 
# save configuration file in proper folder to be found by lora-app-server