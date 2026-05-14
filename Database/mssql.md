# MSSQL

```bash
# Installation clients
sudo apt install sqsh freetds-bin        # sqsh + tsql
```

```bash
# Connexion depuis Kali
sqsh -S <ip> -U <user> -P <password>
```

**Navigation**

```sql
SELECT name FROM sys.databases;
USE <database>;
SELECT table_name FROM information_schema.tables WHERE table_type = 'BASE TABLE';
SELECT column_name, data_type FROM information_schema.columns WHERE table_name = '<table>';
SELECT TOP 10 * FROM <table>;
```

**Enumération**

```sql
SELECT @@version;
SELECT name, type_desc FROM sys.server_principals;
```

**xp_cmdshell -  exécution de commandes système**

```sql
-- Activer
EXEC sp_configure 'show advanced options', 1; RECONFIGURE;
EXEC sp_configure 'xp_cmdshell', 1; RECONFIGURE;

-- Utiliser
EXEC xp_cmdshell 'whoami';
```
