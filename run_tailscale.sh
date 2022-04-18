#!/bin/sh
tailscaled &
sleep 10
tailscale up --authkey="$AUTH_KEY" --accept-routes --advertise-routes="192.168.101.0/24" --accept-dns --hostname fevrflask --advertise-tags "tag:fevr_flask,tag:docker,tag:homelab,tag:devel"