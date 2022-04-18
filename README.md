# fEVR-flask
fEVR rebuilt for flask
This version of fEVR is EXPERIMENTAL.  It will be merged with beardedtek-com/fEVR when stable.

## Docker Compose:
Example docker-compose.yml:
```
version: '2.4'
services:
  fevr_flask:
    build:
      context: ./
      dockerfile: Dockerfile
    image: beardedtek-com/fevr:flask
    container_name: fevr_flask
    restart: unless-stopped
    privileged: true
    networks:
      fevrnet:
        ipv4_address: ${FEVR_IP:-192.168.101.1}
    volumes:
      - ./:/fevr
    environment:
      FLASK_ENV: ${FLASK_ENV:-}
      FEVR_PORT: ${FEVR_PORT:-5090}
    command: /fevr/run_fevr.sh
  fevr_mqtt:
    build:
      context: ./
      dockerfile: Dockerfile
    image: beardedtek-com/fevr:flask
    container_name: fevr_mqtt
    restart: unless-stopped
    privileged: true
    networks:
      fevrnet:
        ipv4_address: ${MQTT_CLIENT_IP:-192.168.101.2}
    volumes:
      - ./:/fevr
    command: /fevr/app/mqtt_client -f "${FEVR_IP:-192.168.101.1}:${FEVR_PORT:-5090}" -H "${MQTT_BROKER_IP:-192.168.2.87}" -p ${MQTT_BROKER_PORT:-1883} -t "${MQTT_TOPICS:-frigate/+}" -u "${MQTT_BROKER_USER:-}" -P "${MQTT_BROKER_PASS:-}"

networks:
  fevrnet:
    driver: bridge
    ipam:
      config:
        - subnet: ${BRIDGE_SUBNET:-192.168.101.0/24}
          gateway: ${BRIDGE_GATEWAY:-192.168.101.254}
```

Copy template.env to .env and adjust as necessary:
NOTE: The IP addresses in the .env file are for internal bridge networking and SHOULD NOT be on the same subnet as your home network.
The default values should serve you well.
```
#fEVR
#####################################################################
# Changes the port fEVR runs on
FEVR_PORT=5090
# Uncomment FLASK_ENV=development to put fEVR into Debug Mode
FLASK_ENV=development
#####################################################################

#MQTT Broker
#####################################################################
MQTT_BROKER_IP=192.168.1.101
MQTT_BROKER_PORT=1883

# If there is no user/password, leave unset
MQTT_BROKER_USER=
MQTT_BROKER_PASS=

# Comma seperated string of MQTT topics to subscribe to.  LIMIT 5!!!
MQTT_TOPICS="frigate/+"
#####################################################################


#####################################################################
#                                                                   #
#      DEFAULTS BELOW THIS LINE SHOULD NOT HAVE TO BE CHANGED       #
#                                                                   #
#####################################################################

# Bridge Network Variables
BRIDGE_SUBNET=192.168.101.0/24
BRIDGE_GATEWAY=192.168.101.254

# fEVR variables
FEVR_IP=192.168.101.1

# mqtt_client variables
MQTT_CLIENT_IP=192.168.101.2
```