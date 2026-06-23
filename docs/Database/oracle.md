## Navigation

```sql
-- Lister les bases (PDBs en 12c+)
SELECT name, open_mode FROM v$pdbs;

-- Lister les tables de l'utilisateur courant
SELECT table_name FROM user_tables;

-- Lister toutes les tables accessibles
SELECT owner, table_name FROM all_tables;

-- Décrire une table
DESC <table>;

-- Lire une table
SELECT * FROM <table> WHERE ROWNUM <= 10;
```

## Enumération

```sql
SELECT * FROM v$version;
SELECT username, password FROM dba_users;
SELECT * FROM session_privs;
```