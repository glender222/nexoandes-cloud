#!/bin/bash
set -euo pipefail
export DEBIAN_FRONTEND=noninteractive
apt-get update -q
apt-get install -y strongswan iptables curl
if ! systemctl is-active --quiet snap.amazon-ssm-agent.amazon-ssm-agent.service && ! systemctl is-active --quiet amazon-ssm-agent; then
  curl -fsSL https://s3.us-east-1.amazonaws.com/amazon-ssm-us-east-1/latest/debian_amd64/amazon-ssm-agent.deb -o /tmp/amazon-ssm-agent.deb
  dpkg -i /tmp/amazon-ssm-agent.deb
  systemctl enable --now amazon-ssm-agent
fi
cat > /etc/sysctl.d/80-nexoandes-vpn.conf <<'SYSCTL'
net.ipv4.ip_forward=1
net.ipv4.conf.all.rp_filter=0
net.ipv4.conf.default.rp_filter=0
net.ipv4.conf.all.accept_redirects=0
net.ipv4.conf.all.send_redirects=0
SYSCTL
sysctl --system
# La PSK se entrega por SSM, nunca en user-data ni en el estado Terraform.
