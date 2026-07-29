# Service

```
sc_create dbgsvc "Debug Service" "C:\Program Files\http_x64.exe" "Windows Debug Service" 0 2 3

sc_qc dbgsvc
sc_start dbgsvc
sc_stop dbgsvc

sc_config dbgsvc "C:\Program Files\http_x64.exe" 0 2 3
```