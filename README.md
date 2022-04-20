# fEVR-flask
fEVR rebuilt for flask
This version of fEVR is EXPERIMENTAL and under VERY HEAVY development.

Please assume that each new commit has breaking changes and start from scratch.

## Docker Compose:
Example docker-compose.yml:
```
version: '2.4'
services:
  tailscale:
    image: tailscale/tailscale
    container_name: fevr_tailscale
    restart: unless-stopped
    privileged: true
    volumes:
      - ./tailscale/varlib:/var/lib
      - /dev/net/tun:/dev/net/tun
      - ./run_tailscale.sh:/run.sh
    cap_add:
      - net_admin
      - sys_module
    environment:
      AUTH_KEY: ${AUTH_KEY}
    command: /run.sh
    networks:
      fevrnet:
        ipv4_address: ${TAILSCALE_IP:-192.168.101.253}
    
  fevr_flask:
    build:
      context: ./
      dockerfile: Dockerfile
    image: beardedtek-com/fevr-flask:main
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
#    build:
#      context: ./
#      dockerfile: Dockerfile
    image: ghcr.io/beardedtek-com/fevr-flask:main
    container_name: fevr_mqtt
    restart: unless-stopped
    privileged: true
    networks:
      fevrnet:
        ipv4_address: ${MQTT_CLIENT_IP:-192.168.101.2}
    volumes:
      - ./:/fevr
    command: /fevr/app/mqtt_client -f "${FEVR_IP:-192.168.101.1}:${FEVR_PORT:-5090}" -p ${MQTT_BROKER_PORT:-1883} -t "${MQTT_TOPICS:-frigate/+}" -u "${MQTT_BROKER_USER:-}" -P "${MQTT_BROKER_PASS:-}" "${MQTT_BROKER_IP:-192.168.2.87}" "${API_KEY}"
     #usage: mqtt_client [-h] [-p PORT] [-t TOPICS] [-u USER] [-P PASSWORD] [-f FEVR] [-s] mqtt
     #
     #positional arguments:
     #  mqtt                  MQTT Broker IP/FQDN **Required** (default: None)
     #  key                   fEVR API Key        **Required** (default: None)
     #
     #optional arguments:
     #  -h, --help            show this help message and exit
     #  -p PORT, --port PORT  MQTT Port (default: 1883)
     #  -t TOPICS, --topics TOPICS
     #                        MQTT Topics (default: 'frigate/+')
     #  -u USER, --user USER  MQTT Username (default: '')
     #  -P PASSWORD, --password PASSWORD
     #                        MQTT Password (default: '')
     #  -f FEVR, --fevr FEVR  fEVR IP Address/FQDN (default: '192.168.101.1:5090)
     #  -s, --https           If set uses https:// (default: http://)

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
#fEVR Setup
#####################################################################
# Changes the port fEVR runs on DEFAULT: 5090
FEVR_PORT=5090
# Uncomment FLASK_ENV=development to put fEVR into Debug Mode
FLASK_ENV=development
#####################################################################

#MQTT Client Setup **REQUIRED **
#####################################################################
MQTT_BROKER_IP=192.168.101.3
MQTT_BROKER_PORT=1883

# If there is no user/password, leave unset
MQTT_BROKER_USER=
MQTT_BROKER_PASS=

# Comma seperated string of MQTT topics to subscribe to.  LIMIT 5!!!
MQTT_TOPICS="frigate/+"

# API Auth Key **REQUIRED**
# 128 character randomly generated key used for api authentication
# To generate a key manually, login with an admin account and go to
# the following address:
# http(s)://<your_fevr_url>/api/auth/add/key/<name>/<ip>/<limit>
#   - <name>: Name of your token (limit 50 characters)
#   - <ip>  : IP address (for future use) should be set to all for now
#   - <limt>: Limit the number of times this key can be used.
#             This will be used in the future for one-time passwords.
#             Set this to 0 for unlimited.
# Example: https://fevr.local/api/auth/add/key/mqtt/all/0
API_KEY=""
#####################################################################

#Tailscale
#####################################################################
# Obtain Auth Key from https://login.tailscale.com/admin/authkeys
AUTH_KEY=tskey-ksMEvS5CNTRL-81zx6mrGvVgpwQDf5xDTF
TAILSCALE_IP=192.168.101.253
#####################################################################

#####################################################################
#                                                                   #
#      DEFAULTS BELOW THIS LINE SHOULD NOT HAVE TO BE CHANGED       #
#                                                                   #
#####################################################################

# Bridge Network Variables
BRIDGE_SUBNET=192.168.101.0/24
BRIDGE_GATEWAY=192.168.101.254

# fEVR container Network Address
FEVR_IP=192.168.101.1

# mqtt_client container Network Address
MQTT_CLIENT_IP=192.168.101.2
```

Once it is up and running run the following command:
```
wget http://<fevr-flask-ip>:<port>/api/frigate/add/<name>/<http>/<ip>/<port>
```
example:
```
wget http://192.168.101.1:5090/api/frigate/add/frigate/http/192.168.101.10/5000
```

You can also open it as a link in your web browser of choice.