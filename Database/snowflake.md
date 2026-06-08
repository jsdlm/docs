# Snowflake

https://docs.snowflake.com/fr/user-guide/snowsql-install-config
```bash
snowsql -a <account>.snowflakecomputing.com -u <user>
```

**Navigation**

```sql
-- Lister les bases
SHOW DATABASES;

-- Utiliser une base
USE DATABASE <database>;
USE SCHEMA <schema>;

-- Lister les schémas
SHOW SCHEMAS;

-- Lister les tables
SHOW TABLES;

-- Décrire une table
DESC TABLE <table>;

-- Lire une table
SELECT * FROM <table> LIMIT 10;
```

**Enumération**

```sql
SELECT CURRENT_VERSION();
SELECT CURRENT_USER(), CURRENT_ROLE();
SHOW USERS;
SHOW ROLES;
SHOW GRANTS TO USER <user>;
```
