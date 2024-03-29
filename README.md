## NameDaddy
Manage GoDaddy, Namecheap and Route53 DNS records for previously purchased domains.

### Install
```
git clone https://github.com/Tw1sm/namedaddy.git
cd namedaddy
pip3 install -r requirements.txt
./namedaddy.py
```
You must already have API keys for at least 1 of Namecheap, GoDaddy, or Route53 and set API key values in `config.py`.

### Main Menu

```
Command    Syntax <Required> (Optional)      About
=======    ===========================       ====
exit                                         Close NameDaddy
help                                         Displays help menu
show                                         Display all domains or active domains to the screen
switch     <registrar>                       Swtich between GoDaddy, Namecheap and Route53 API clients
use        <domain name>                     Select a domain to edit
```

### Domain Menu

```
Command     Syntax <Required> (Optional)                  About
=======     ============================                  =====
add         <type> (priority> <name> <value>              Add a DNS record. Priority is only for MX
back                                                      Return to main menu
delete      GoDaddy/Route53: <record name> (record type)  Deletes GoDaddy DNS records by name or name/type combos. All records matching criteria will be deleted
delete      Namecheap <record id>                         Deletes Namecheap DNS records by record ID
exit                                                      Close ConfigDaddy
help                                                      Displays help menu
records                                                   Display DNS records
stockconfig <config name>                                 Configure a new domain with preset records
updateip    <ip addr>                                     Updates the IP the address domain points to
```

### Known Issues
* Deleting some records with the GoDaddy API client can be a little buggy - only way to delete is by providing the name of the record and optionally the record type. This works sometimes, but not always in my experience.
* Adding a MX record with the Namecheap API client usually fails unless the `MAIL SETTINGS` value has been changed to `Custom MX` using the web interface
* The `route53` library requires that DNS records have a TTL value otherwise it will fail to get a list of records. So far, I've encounterd this on `A` records that have the `Value/route traffic to` set to an alias (on/off slider in the Route53 web interface)
