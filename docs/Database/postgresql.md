# PostgreSQL

```bash
# Installation client
sudo apt install postgresql-client
```

```bash
# Connexion
psql -h <ip> -p 5432 -U <user> -d <database>
```

**Navigation**

```sql
\l                  -- lister les bases
\c <database>       -- se connecter à une base
\dt                 -- lister les tables
\dt *.*             -- lister les tables de tous les schémas
\d <table>          -- décrire une table
\q                  -- quitter
```

**Enumération**

```sql
SELECT version();
SELECT usename, passwd FROM pg_shadow;
SELECT * FROM <table> LIMIT 10;
```
