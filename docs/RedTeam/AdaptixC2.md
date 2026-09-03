https://github.com/Adaptix-Framework/AdaptixC2
https://adaptix-framework.gitbook.io/adaptix-framework

```bash
sudo vim AdaptixServer/server-dist/profile.yaml
```

```yaml
Teamserver:
  interface: "127.0.0.1"
  port: 4321
  endpoint: "/endpoint"
  password: "password"
  only_password: true
  cert: "server.rsa.crt"
  key: "server.rsa.key"
```

```bash
make docker-restart
```
# BOFs

https://github.com/Adaptix-Framework/Extension-Kit

```bash
sudo apt update
sudo apt install build-essential python3 mingw-w64

git clone https://github.com/Adaptix-Framework/Extension-Kit
cd Extension-Kit
make
```

Load all modules in AdaptixC2 client: **Main menu** -> **AxScript** -> **Script manager**.

[![](https://github.com/Adaptix-Framework/Extension-Kit/raw/main/_img/01.png)](https://github.com/Adaptix-Framework/Extension-Kit/blob/main/_img/01.png)

**Context menu** -> **Load new** and select the _extension-kit.axs_ file.


# OPSEC
https://github.com/MaorSabag/Adaptix-StealthPalace

