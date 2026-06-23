## Installation

```bash
# Installation client
sudo apt install mongodb-clients         # legacy mongo shell
# ou mongosh (shell moderne)
npm install -g mongosh
```

```bash
# Connexion
mongosh <ip>:27017
mongosh "mongodb://<user>:<password>@<ip>:27017/<database>"
```

## Navigation

```js
show dbs
use <database>
show collections
db.<collection>.find().limit(10)
db.<collection>.find({ "key": "value" })
exit
```

## Enumération

```js
db.version()
db.getUsers()
```
