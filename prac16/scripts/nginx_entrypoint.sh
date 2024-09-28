#!/usr/bin/env sh

set -eu

export PLUG='$'
envsubst < /etc/nginx/nginx.conf.template > /etc/nginx/nginx.conf

exec "$@"
