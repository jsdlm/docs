```bash
# https://github.com/dirkjanm/adidnsdump
pipx install adidnsdump
adidnsdump -u 'north.sevenkingdoms.local\jon.snow' -p 'iknownothing' winterfell.north.sevenkingdoms.local

# Zone transfer DNS
dig @$rhost axfr
dig -x $rhost
```
