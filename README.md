## WhoxySD
Gather all siblings root domains of a domain from Whoxy. First, all domains that meet your search criteria are retrieved from Whoxy and then, they are verified by whoising each one and looking for your search parameter in the records. The utility can be used with two workflows in mind:

* Use with `-d` and a domain as input in order to retrieve information about a domain, and then use the same command, just adding `-c` with your choice to use for retrieval.
* Use with `-cn` / `-co` / `-em` if you already know the information you are looking for.

Notes:
1. If you want to pass the output of this utility to some other tool for further processing, you can use `-q` to suppress all other output and simply print the identified domains to stdout.
2. The utility supports multiprocessing. However default thread count is set to 1 in order to avoid being rate-limited by the whois servers. 
3. To avoid being rate-limited even further, use the `-s` argument to add a sleep (for instance 1 second) to the thread.

Help:

```
usage: WhoxySD.py [-h] [-d DOMAIN] [-c {1,2,3}] [-cn COMPNAME] [-on OWNNAME] [-em EMAIL]
                  [-o OUTPUTFILE] [-t THREADS] [-s SLEEPTIME] [-q]

Gather all root domains of an organization from Whoxy

optional arguments:
  -h, --help            show this help message and exit
  -d DOMAIN, --domain DOMAIN
                        Domain to get details for
  -c {1,2,3}, --choice {1,2,3}
                        Choices, for use with -d: [1=cn, 2=on, 3=em]
  -cn COMPNAME, --company-name COMPNAME
                        Company name to look for
  -on OWNNAME, --owner-name OWNNAME
                        Owner name to look for
  -em EMAIL, --email EMAIL
                        Email to look for
  -o OUTPUTFILE, --output OUTPUTFILE
                        Output file
  -t THREADS, --threads THREADS
                        Number of threads [default is 1]
  -s SLEEPTIME, --sleep SLEEPTIME
                        Sleep in secs between iterations [default is 0]
  -q, --quiet           If enabled, only found domains are printed
```