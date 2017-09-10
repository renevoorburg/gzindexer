# gzindexer

Creates an index of the members of concatenated gzip files (cf. [RFC 1952](https://tools.ietf.org/html/rfc1952) ). Use it for quick and easy random file access.

Supply the file to be indexed as parameter:
```
$ python3 gzindexer.py infile.gz
```

This wil generate output like
```
# infile.gz: [start] [bytes]
0 27677
27677 676790
```

The output can be used for quick random files access to specific members:
```
$ dd bs=1 skip={start} count={bytes} if=infile.gz | gzip -dc
```
