# gzindexer

Creates an index of the members of concatenated gzip files (cf. [RFC 1952](https://tools.ietf.org/html/rfc1952) ). Use it for quick and easy random file access.

Supply the file to be indexed as parameter, optionally provide an xpath expression to add keys to the index:
```
$ python3 gzindexer.py [-h] [-x XPATH] filename
```

This wil generate output similar to:
```
# infile.gz: [start] [bytes] [XPATH]
0 27677 id:1234
27677 676790 id:1235
```

The output can be used for quick random files access to specific members:
```
$ dd bs=1 skip={start} count={bytes} if=infile.gz | gzip -dc
```
