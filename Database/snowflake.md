# Snowflake

```bash
# Connexion via SnowSQL
snowsql -a <account>.snowflakecomputing.com -u <user>

# Connexion via Python (si SnowSQL absent)
pip install snowflake-connector-python
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
