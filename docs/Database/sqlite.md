## Installation

```bash
# Installation client
sudo apt install sqlite3
```

```bash
# Ouvrir un fichier
sqlite3 <fichier.db>
```

## Navigation

```sql
.tables             -- lister les tables
.schema <table>     -- décrire une table
SELECT * FROM <table> LIMIT 10;
.quit
```