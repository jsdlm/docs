# MySQL / MariaDB

```bash
# Installation client
sudo apt install default-mysql-client
```

```bash
# Connexion
mysql -h <ip> -P 3306 -u <user> -p
```

**Navigation**

```sql
SHOW DATABASES;
USE <database>;
SHOW TABLES;
DESCRIBE <table>;
EXIT
```

**Enumération**

```sql
SELECT version();
SELECT user, authentication_string FROM mysql.user;
SELECT * FROM <table> LIMIT 10;
```
