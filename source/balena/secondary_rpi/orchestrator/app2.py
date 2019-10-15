from flask import request, Flask
from flask_restful import Resource, Api
import os
import subprocess
import requests
from threading import Thread
import json
import time
import yaml


# TODO differentiate between service_name used in balena and image_name used for filecoin
# TODO better comments


EDGE_IP_ADDRESS = "https://a6df793906bb9a28dc45199d4ed42843.balena-devices.com/"
CLOUD_HOST = "http://150.140.184.241:1880"
# MINER_ADDRESS = "ASSDF"
PORT = os.getenv("PORT", "80")
SECRET = "super_secret"
ID = "1234567890"

app = Flask(__name__)
api = Api(app)


@app.route('/orchestrator/service_customer/image/status', methods=['POST', 'GET'])
def service_customer_image():
    if request.method == "POST":
        message = request.json
        image_status = message["status"]
        image_name = message["imageName"]
        image_hash = message["imageHash"]
        miner_address = message["minerAddress"]
        orchestrator.services_customer_contracts[image_name]["image_status"] = image_status
        print(
            f"Orchestrator -- Image { image_name}  is {image_status} in the filecoin network")
        if image_status == "stored":
            thread = Thread(target=orchestrator.generate_contract_customer, args=(
                image_name, image_hash, miner_address))
            thread.start()
        return "ok"
    else:
        return json.dumps(orchestrator.services_customer_contracts)


@app.route('/orchestrator/service_provider/image/status', methods=['POST'])
def service_provider_image():
    if request.method == 'POST':
        message = request.json
        image_status = message["status"]
        image_name = message["imageName"]
        # image_hash = message["imageHash"]
        if image_status == "downloaded":
            thread = Thread(target=orchestrator.set_state)
            thread.start()
            return_message = "set_state()"
            return_code = 200
        else:
            return_message = "unknown command"
            return_code = 404

    return return_message, return_code

# CONSUL HEALTH
@app.route('/orchestrator/health', methods=['GET'])
def orchestrator_health():
    return "orchestrator v0.1", 200


@app.route('/orchestrator/contracts/debug', methods=['GET'])
def print_contracts():
    data = {"service_provider": orchestrator.services_provider_contracts,
            "service_customer": orchestrator.services_customer_contracts}
    payload_str = json.dumps(data, indent=4)
    return payload_str
# create_contract/testing --> wait(filecoin)--> /image_stored --> generate_contract_customer() --> /create_contract --> contract_setup()

# customer ENDPOINT
@app.route('/orchestrator/service_customer/contract/testing', methods=['POST', 'GET'])
def create_contract_debug():
    # save file to filecoin_network
    # this function should belong to Orchestrator class and be called as part of the contract process
    # but for debugging, it will be called manually using a somple REST endpoint
    if request.method == "POST":
        data = request.json
        image_name = data["imageName"]
        service_provider_location = data["serviceProviderLocation"]
        duration = data["storageDuration"]
        miner_address = data["minerAddress"]
        payload = {"image_name": image_name, "storage_duration": duration, "miner_address" : miner_address}
        orchestrator.services_customer_contracts[image_name] = {
            "contract_status": "pending", "image_status": "pending", "service_provider_location": service_provider_location}
        thread = Thread(target=orchestrator.finterface_comm,
                        args=("POST", payload))
        thread.start()
        status = "ok"
        code = 200
        return status, code
    else:
        return json.dumps(orchestrator.services_customer_contracts)

# PROVIDER ENDPOINT


@app.route('/orchestrator/service_provider/contract', methods=['POST'])
def contract_provider():
    data = request.json
    print(data)
    orchestrator.contract_setup(
        data["imageName"], data["imageHash"], data["config"])
    return "ok"


# Assumptions:
# 1) filecoin_interface and orchestrator share file directory
# 2) contract_setup --> finterface(request_file)--> file_downloaded --> load_image-->set state


class Orchestrator():
    def __init__(self):
        # self.miner_address = MINER_ADDRESS
        self.services_provider_contracts = []
        # [
        #     {
        #         "service_name": "",
        #         "config": {}
        #     }
        # ]
        self.services_customer_contracts = {}
        #  {
        #   "service1": {
        #     "contract_status":"pending,
        #     "image_status":"stored"
        #     }
        #  }
        self.active_contracts = []  # same as contracts_services_provider
        try:
            with open("data/orchestrator_state_file.json")as f:
                print("Orchestrator -- state file exists")
                data = json.load(f)
                self.services_provider_contracts = data["services_provider_contracts"]
                self.services_customer_contracts = data["services_customer_contracts"]
                i = 0
                for service in self.services_provider_contracts:
                    self.stop_service(service["service_name"])
                    self.contract_interval(i)
                    i = i + 1
        except FileNotFoundError:
            print("Orchestrator - no file found, starting a fresh instance")

    def _image2engine(self):
        print("BalenaEngine API - load image")

    def set_supervisor_state(self):
        print("Supervisor API - set state")
        self.balena_push()

    def balena_push(self):
        print("Communicate with node-RED backend - run docker-compose")
        url = "http://150.140.184.249:1880/balena/push"
        with open("data/docker-compose.yml", "r") as yaml_in:
            compose = yaml.safe_load(yaml_in)
        req = requests.post(url, json=compose)
        status = req.status_code
        print(f"Sent balena push command with response:{status}")

    def start_service(self, service_name):
        print("Orchestrator -- Supervisor API - start_service")
        supervisor_url = os.environ["BALENA_SUPERVISOR_ADDRESS"]
        key = os.environ["BALENA_SUPERVISOR_API_KEY"]
        app_id = os.environ["BALENA_APP_ID"]
        url = supervisor_url + f"/v2/applications/{app_id}/start-service?apikey={key}"
        payload = "{\"serviceName\":\"" + service_name + "\"}"
        while True:
            try:
                # req = requests.post(url=url, json=payload)
                # status = req.status_code
                command =  'curl --header "Content-Type:application/json"'
                curl =  command + ' "' + url + '"'
                curl2 = curl + ' -d \'{"serviceName": "nodered-device-service"}\''
                response = os.system(curl2)
                if response == 0:
                    print(f"\nOrchestrator -- Started service {service_name}")
                    break
                else:
                    print(
                        f"Orchestrator -- Tried starting service, got response: {response}, retrying in 10s")
            except Exception as e:
                print(
                    f"Orchestrator -- start service got error: {e}, retrying in 10s")
            time.sleep(10)

        # call to supervisor api

    def stop_service(self, service_name):
        print("Orchestrator -- Supervisor API - stop_service")
        url = os.environ["BALENA_SUPERVISOR_ADDRESS"]
        key = os.environ["BALENA_SUPERVISOR_API_KEY"]
        app_id = os.environ["BALENA_APP_ID"]
        url = url + f"/v2/applications/{app_id}/stop-service?apikey={key}"
        payload = "{\"serviceName\":\"" + service_name + "\"}"
        while True:
            try:
                command =  'curl --header "Content-Type:application/json"'
                curl =  command + ' "' + url + '"'
                curl2 = curl + ' -d \'{"serviceName": "nodered-device-service"}\''
                curl3 = curl + ' -d \'{"serviceName": "lora-appserver"}\''
                response2 = os.system(curl2)
                response3 = os.system(curl3)       
                # req = requests.post(url=url, json=payload)
                # status = req.status_code
                if response2 == 0 and response3 ==0:
                    print(f"\nOrchestrator -- Stopped service {service_name}")
                    break
                else:
                    print(
                        f"Orchestrator -- Tried stopping service, got response: {response2}, {response3}, retrying in 10s")
            except Exception as e:
                print(
                    f"Orchestrator -- stop service got error: {e}, retrying in 10s")
            time.sleep(10)

    def finterface_comm(self, method, payload):
        if method == "POST":
            req = requests.post(url="http://127.0.0.1:" + PORT +
                                "/filecoin_interface/orchestrator/image", json=payload)
        elif method == "GET":
            req = requests.get(url="http://127.0.0.1:" + PORT +
                               "/filecoin_interface/orchestrator/image", params=payload)
        print(req)
        return 0
        # call to filecoin interface service
        # /filecoin_interface/orchestrator/ [get_image, store_image]
        # payload:
        # get_image (image_hash, image_name, minerAddress)
        # store_image (image_name, duration)

    def contract_setup(self, image_name, image_hash, config):
        new_service = {}
        new_service["image_name"] = image_name
        new_service["hash"] = image_hash
        new_service["config"] = json.loads(config)
        new_service["service_name"] = new_service["config"]["serviceName"]
        self.services_provider_contracts.append(new_service)
        # download image from filecoin network
        payload = {"imageName": image_name, "imageHash": image_hash,
                   "minerAddress": new_service["config"]["miner_address"]}
        self.finterface_comm("GET", payload)
        return 0

    def contract_interval(self, index):
        p = Thread(target=self.check_contract, args=[index])
        p.start()
        return 0

    def check_contract(self, index):
        service = self.services_provider_contracts[index]
        interval = int(service["config"]["event"]["interval"])
        while True:
            try:
                r = requests.get(
                    url=service["config"]["event"]["ip"] + "/orchestrator/health", timeout=10)
                if r.status_code == 200:
                    print(
                        "Service Provider orchestrator checked for event, everything OK")
                else:
                    return_code = r.status_code
                    print(f"Node is online but return code is : {return_code}")
                    raise requests.exceptions.Timeout
            except requests.exceptions.Timeout:
                print (f"Activating insurance contract..")
                self.services_provider_contracts.remove(service)
                self.active_contracts.append(service)
                self.save_orchestrator_state()
                self.start_service(service["service_name"])
                break
            time.sleep(interval)

    def generate_contract_customer(self, image_name, image_hash, miner_address):
        with open('data/new_service_config.json', encoding='utf-8') as f:
            config = json.load(f)
        config["miner_address"] = miner_address
        config["event"]["ip"] = EDGE_IP_ADDRESS
        configs = json.dumps(config)
        self.services_customer_contracts[image_name]["image_status"] = "stored"
        service_provider_location = self.services_customer_contracts[
            image_name]["service_provider_location"]
        payload = {"imageName": image_name,
                   "imageHash": image_hash, "config": configs}
        r = requests.post(url=service_provider_location +
                          "/orchestrator/service_provider/contract", json=payload)
        if r.status_code == 200:
            self.services_customer_contracts[image_name]["contract_status"] = "inactive"
        return 0
        # if image is stored, send hash + to create_contract of other orchestrator

    def save_device_state(self):
        # get device_state
        # append new state
        # save overall state
        with open('data/current_state.json', encoding='utf-8') as f:
            self.target_state = json.load(f)
        with open('data/new_service_state.json') as f:
            new_service = json.load(f)
            self.target_state["state"]["local"]["apps"]["1"]["services"].append(
                new_service)
        with open('data/new_state.json', 'w', encoding='utf-8') as f:
            json.dump(self.target_state, f, ensure_ascii=False, indent=4)
        service_name = new_service["serviceName"]
        print(f"Device state updated with service: {service_name}")
        return 0

    def save_orchestrator_state(self):
        self.orch_state = {}
        self.orch_state["services_provider_contracts"] = self.services_provider_contracts
        self.orch_state["services_customer_contracts"] = self.services_customer_contracts
        self.orch_state["active_contracts"] = self.active_contracts
        with open('data/orchestrator_state_file.json', 'w', encoding='utf-8') as fp:
            json.dump(self.orch_state, fp, ensure_ascii=False, indent=4)
        print("Orchestrator state saved to file \"data/orchestrator_state_file.json\" ")
        return 0

    def set_state(self):
        # self.save_device_state()
        self.save_orchestrator_state()
        self.set_supervisor_state()
        return 0

        # requests to supervisor for new state
        # _balena_push()


####### Filecoin Interface ############## Filecoin Interface ############## Filecoin Interface ############## Filecoin Interface #######


### API START####### API START####### API START###### API START###### API START###### API START###### API START####

@app.route('/filecoin_interface/backend/image', methods=['POST', 'GET'])
def filecoin_interface_image():
    message = request.json
    # print(f" Filecoin Interface -- Received request from backend: {message}")
    if request.method == "POST": 
        image_hash = message["imageHash"]
        image_name = message["imageName"]
        image_status = message["imageStatus"]
        miner_address = message["miner_address"]
        if image_status == "ready2download":
            print(
                f" Filecoin Interface -- Image with hash [ {image_hash} ] and name [ {image_name} ] is ready to be downloaded")
            scp_thread = Thread(target=scp_image, args=(
                "download", image_name, image_hash, 0))
            scp_thread.start()
            status = "Started scp download"
            status_code = 200
        else: #stored, committed
            communicate_orchestrator(
                image_status, {"imageHash": image_hash, "imageName": image_name, "minerAddress":miner_address})
            status = "data received"
            status_code = 200
    else:
        status = "FUNCTIONALITY NOT FOUND"
        status_code = 404
    return status, status_code


@app.route('/filecoin_interface/backend/error', methods=['POST'])
def error_log():
    message = request.json
    error_object = message["errorObject"]
    error_code = error_object["code"]
    error_message = error_object["message"]
    print(
        f" Filecoin Interface -- Received error from backend:\nMessage: {error_message}Code: {error_code}")
    return "error logged"


@app.route('/filecoin_interface/orchestrator/image', methods=['POST', 'GET'])
def orchestrator_store_image():
    if request.method == "POST":
        data = request.json
        image_name = data["image_name"]
        storage_duration = data["storage_duration"]
        miner_address = data["miner_address"]
        print(
            f" Filecoin Interface -- \nReceived request from orchestrator: {data}")
        scp_thread = Thread(target=scp_image, args=(
            "upload", image_name, storage_duration, miner_address))
        scp_thread.start()
        status = "Started scp upload"
        status_code = 200
    else:
        image_name = request.args.get('imageName')
        image_hash = request.args.get('imageHash')
        miner_address = request.args.get('minerAddress')
        payload = {"imageName": image_name, "imageHash": image_hash,
                   "minerAddress": miner_address, "ipAddress": EDGE_IP_ADDRESS}
        communicate_backend("get_image", payload)
        status = f"requested image: {image_name} with hash: {image_hash} from the filecoin network"
        status_code = 200
    return status, status_code
#### END OF API ######### END OF API ######### END OF API ######### END OF API ######### END OF API #####

@app.route('/filecoin_interface/health', methods=['GET'])
def filecoin_interface_health():
    return "Filecoin Interface v0.1", 200

def communicate_orchestrator(topic, datum):
    # topic = image_commited, image_stored, image_downloaded
    # Inform orchestrator that image has been commited
    # Inform orchestrator that image has been stored in the network
    # Inform orchestrator that image has been downloaded
    orchestrator_url = "http://localhost:" + PORT + "/orchestrator/"
    datum["status"] = topic
    if topic == "downloaded":
        orchestrator_url = orchestrator_url + "service_provider/image/status"
    else:  # topic = stored, committed
        orchestrator_url = orchestrator_url + "service_customer/image/status"
    payload_str = json.dumps(datum, indent=4)
    print(
        f" Filecoin Interface -- communicate_orchestrator(), request: {payload_str}")
    req = requests.post(orchestrator_url, json=datum)
    print(
        f" Filecoin Interface -- Communicate_orchestrator(), response: {req}")
    return req.status_code


def communicate_backend(topic, datum):
    # topic = get_image, store_image
    payload = {"id": ID, "secret": SECRET, "data": datum}
    payload_str = json.dumps(payload, indent=4)
    print(
        f" Filecoin Interface -- Sending request to backend with payload: {payload_str}")
    req = requests.post(CLOUD_HOST + "/" + topic, json=payload)
    print(f" Filecoin Interface -- Response from backend: {req}")
    return req.status_code

def scp_image(action, image_name, argument1, argument2):
    path = "/home/ubuntu/filecoin_images/"
    if action == "download":
        command_part_1 = "ubuntu@150.140.184.241:" + path + image_name
        command_part_2 = os.getcwd() + "/data/images"
        command_part_3 = os.getcwd() + "/data/odyslam_ubuntu.pem"
        print("\n### SCP PROCESS START ###")
        p = subprocess.Popen(['scp','-o StrictHostKeyChecking=no',"-i", command_part_3, command_part_1, command_part_2])
        return_code = p.wait()
        print("### SCP END ####")
        if return_code != 0:
            print(f"Filecoin Interface -- scp produced error {return_code}")
            return 1
        else:
            print(f"Filecoin Interface -- file with {image_name} was downloaded using scp")
            payload = {"imageHash": argument1, "imageName": image_name}
            communicate_orchestrator("downloaded", payload)         
            #  As soon as image is downloaded, inform orchestrator so as to acquire it
    elif action == "upload":
        print("\n### SCP PROCESS START (new version0) ###\n")
        command_part_2 = "ubuntu@150.140.184.241:" + path
        command_part_1 = os.getcwd() + "/data/images/" + image_name
        command_part_3 = os.getcwd() + "/data/odyslam_ubuntu.pem"
        p = subprocess.Popen(['scp','-o StrictHostKeyChecking=no', "-i",command_part_3,command_part_1, command_part_2])
        return_code = p.wait()
        print("### SCP END ####")
        if return_code != 0:
            print(f"Filecoin Interface -- scp produced error {return_code}")
            return 1
        else:
            print(f"Filecoin Interface -- file with {image_name} was uploaded using scp")
            payload = {"duration": argument1, "imageName": image_name, "minerAddress": argument2, "ipAddress": EDGE_IP_ADDRESS}
            communicate_backend("store_image", payload)
        # As soon as image is uploaded to the remote server, inform backend
        # so as to start upload to filecoin network
    else:
        print("Wrong command for scp")
    return 0


# def scp_image(action, image_name, argument):
#     path = "/home/ubuntu/filecoin_images/"
#     if action == "download":
#         command_part_1 = "ubuntu@150.140.184.241:" + path + image_name
#         command_part_2 = os.getcwd() + "data/images"
#         command_part_3 = "-i " + os.getcwd() + "/data/odyslam_ubuntu.pem"
#         print("\n### SCP PROCESS START ###")
#         # p = subprocess.Popen(['scp','-o StrictHostKeyChecking=no','-o UserKnownHostsFile=/dev/null',command_part_3, command_part_1, command_part_2])
#         # return_code = p.wait()
#         time.sleep(4)
#         print("...File sent")
#         print("### SCP END ####")
#         # if return_code != 0:
#         #     print(f"Filecoin Interface -- scp produced error {return_code}")
#         #     return 1
#         # As soon as image is downloaded, inform orchestrator
#         # so as to acquire it
#         payload = {"imageHash": argument, "imageName": image_name}
#         communicate_orchestrator("downloaded", payload)
#     elif action == "upload":
#         print("\n### SCP PROCESS START ###\n")
#         return_value = os.system("scp -o StrictHostKeyChecking=no -i /usr/src/app/data/odyslam_ubuntu.pem /usr/src/app/data/images/hello.txt ubuntu@150.140.184.241:/home/ubuntu/filecoin_images/")
#         print(return_value)
#         command_part_2 = "ubuntu@150.140.184.241:" + path
#         command_part_1 = os.getcwd() + "data/images/" + image_name
#         command_part_3 = "-i " + os.getcwd() + "/data/odyslam_ubuntu.pem"
#         p = subprocess.Popen(['scp','-o StrictHostKeyChecking=no','-o UserKnownHostsFile=/dev/null', command_part_3,command_part_1, command_part_2])
#         return_code = p.wait()
#         print(return_code)
#         print("### SCP END ####")
#         # if return_code != 0:
#         #     print(f"Filecoin Interface -- scp produced error {return_code}")
#         #     return 1
#         # As soon as image is uploaded to the remote server, inform backend
#         # so as to start upload to filecoin network
#         payload = {"duration": argument, "imageName": image_name}
#         communicate_backend("store_image", payload)
#     else:
#         print("Wrong command for scp")
#     return 0

####### Filecoin Interface ############## Filecoin Interface ############## Filecoin Interface ############## Filecoin Interface #######

def register_health():
    while True:
        try:
            url = "http://edgex-core-consul:8500/v1/agent/service/register?replace-existing-checks=1"
            payload = {
                "ID": "filecoin",
                "Name": "Filecoin Inteface",
                "Port": 80,
                "EnableTagOverride": False,
                "Check": {
                    "DeregisterCriticalServiceAfter": "90m",
                    "HTTP": "http://orchestrator:" + PORT + "/filecoin_interface/health",
                    "Interval": "125s",
                },
                "Weights": {
                    "Passing": 10,
                    "Warning": 1
                }
            }
            req = requests.put(url, json=payload)
            print(f"Filecoin Service registered with Consul. Response: {req}")
            payload = {
                "ID": "orchestrator",
                "Name": "Orchestrator",
                "Port": 80,
                "EnableTagOverride": False,
                "Check": {
                        "DeregisterCriticalServiceAfter": "90m",
                        "HTTP": "http://orchestrator:" + PORT + "/orchestrator/health",
                        "Interval": "120s",
                },
                "Weights": {
                    "Passing": 10,
                    "Warning": 1
                }
            }
            req = requests.put(url, json=payload)
            print(f"Orchestrator Service registered with Consul. Response: {req}")
            break
        except (requests.exceptions.Timeout, requests.exceptions.ConnectionError) as e:
            print(f"Register Health: got exception:{e}, retrying in 20s")
            time.sleep(20)
            


if __name__ == '__main__':
    orchestrator = Orchestrator()
    thread = Thread(target = register_health)
    thread.start()
    app.run(host='0.0.0.0', port=PORT, debug=True)
