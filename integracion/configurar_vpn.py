#!/usr/bin/env python3
"""Configurar strongSwan en extremos ya administrados; PSK privada e idempotente."""
from datetime import datetime, timezone
import json
import time
from pathlib import Path
import operaciones as op


def configuration(local_ip, peer_ip, local_network, remote_network):
    return f'''config setup
    uniqueids=yes

conn nexoandes
    keyexchange=ikev2
    type=tunnel
    authby=psk
    left=%defaultroute
    leftid={local_ip}
    leftsubnet={local_network}
    right={peer_ip}
    rightid={peer_ip}
    rightsubnet={remote_network}
    ike=aes256-sha256-modp2048!
    esp=aes256-sha256!
    forceencaps=yes
    dpddelay=30s
    dpdaction=restart
    keyingtries=%forever
    auto=start
'''


def commands(local_ip,peer_ip,local_net,remote_net,psk,gateway):
    script='set -euo pipefail\ncommand -v ipsec >/dev/null\n'
    script+=op.write_remote('/etc/ipsec.conf',configuration(local_ip,peer_ip,local_net,remote_net))
    script+=op.write_remote('/etc/ipsec.secrets',f'{local_ip} {peer_ip} : PSK "{psk}"\n')
    script+='sysctl -w net.ipv4.conf.all.rp_filter=0 >/dev/null\n'
    if gateway: script+='sysctl -w net.ipv4.ip_forward=1 >/dev/null\n'
    chains=['FORWARD'] if gateway else ['OUTPUT']
    for chain in chains:
        rule=f'-p tcp -s {local_net} -d {remote_net} --tcp-flags SYN,RST SYN -j TCPMSS --set-mss 1360'
        script+=f'iptables -t mangle -C {chain} {rule} 2>/dev/null || iptables -t mangle -A {chain} {rule}\n'
        rule=f'-s {local_net} -d {remote_net} -m policy --dir out --pol none -j REJECT'
        script+=f'iptables -C {chain} {rule} 2>/dev/null || iptables -A {chain} {rule}\n'
    script+='systemctl enable strongswan-starter >/dev/null 2>&1\nsystemctl restart strongswan-starter\nsleep 3\nipsec statusall\n'
    return script


def main():
    op.assert_aws_identity()
    aws=op.state('aws');gcp=op.state('gcp');secrets=op.private_settings()
    gateway=op.ssm(aws['vpn_instance'],commands(aws['vpn_ip'],gcp['vm_ip'],'10.10.0.0/16','10.30.1.0/24',secrets['ipsec_psk'],True),timeout=90)
    replica=op.ssh(commands(gcp['vm_ip'],aws['vpn_ip'],'10.30.1.0/24','10.10.0.0/16',secrets['ipsec_psk'],False),timeout=50)
    for _ in range(12):
        if 'INSTALLED' in replica:
            break
        time.sleep(3)
        replica=op.ssh('ipsec statusall',timeout=30)
    else:
        raise RuntimeError('IPsec no instaló CHILD_SA; no continuar con la réplica')
    result={'utc':datetime.now(timezone.utc).isoformat(),'aws':gateway,'gcp':replica,
            'nota':'Estado de negociacion; la conectividad se demuestra adicionalmente con consulta PostgreSQL.'}
    path=op.ROOT/'integracion/evidencias/20261104/vpn-configuracion.json'
    path.parent.mkdir(parents=True,exist_ok=True);path.write_text(json.dumps(result,indent=2)+'\n')
    print('Configuración aplicada; se conservó la PSK fuera de Terraform y evidencias.')
    print('GCP CHILD_SA instalada:', 'INSTALLED' in replica)


if __name__=='__main__':main()
