## From the Implementation Chapter of the Thesis:

The scenario that was chosen for the implementation of our reference use-case is fairly simple. We assume an edge device that handles a sensor which is connected through LoRa. This edge device has entered into a service contract with another edge device which also supports the LoRa protocol. In our scenario, EdgeA has a failure and EdgeB detects the failure, activates the contract and kickstarts the services in order to control the sensor.
In the implementation, each Edge consists of a Raspberry Pi 3 and a Lorank8 (Beaglebone Black) that are networked over LAN. Although they are two distinct hardware boards, we model our Edge as the combination of those two. Each Edge device has therefore it’s own LoRa gateway, both in terms of software (i.e packet forwarder) and in terms of hardware.

The **Implementation Chapter** can be found [here](https://www.researchgate.net/publication/336564357_An_IoT_Edge-as-a-service_Eaas_Distributed_Architecture_Reference_Implementation), it serves as a detailed walkthrough tutorial of the implementation, it's components and it's purpose.

> The Node-RED device-service that is mentioned in the implementation can be found in a seperate repository [here](https://github.com/OdysLam/edgex-nodered-device-service).

Below you can see an overview of the implementation and how the relevant services have been distributed over 2 physical edge systems which consist a single logical Edge system.

![](https://github.com/OdysLam/thesis-eaas/blob/master/Thesis/images/Distributed%20Implementation%20Architecture%20(1).png?raw=true)
