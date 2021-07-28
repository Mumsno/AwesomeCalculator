Awesome Calculator is a ranking program that searches for sub-repos of awesome repos and ranks them according to various criteria.

**How To Use**
```
usage: AwesomeCalculator.py [-h] [--debug] [--limit LIMIT]
                            owner_name repo_name token

This script is used to determine how awesome are awesome pages!

positional arguments:
  owner_name     The awesome page's owner name
  repo_name      The awesome repository's name
  token          Github's authentication token

optional arguments:
  -h, --help     show this help message and exit
  --debug
  --limit LIMIT  Limit sub-repos queries for debug or validation purposes
```

For Example
```
python AwesomeCalculator.py avelino awesome-go <your_token> --limit 20
```

**Compatability**

Supports every Windows x64/x86 with **python 2.7**

**Developers**

Amit Tal
