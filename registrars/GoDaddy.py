from godaddypy import Client, Account
import requests
import json

class GoDaddyApiClient:
    name = 'GoDaddy'
    client = ''
    domains = []


    def __init__(self, GoDaddyConfig):
        self.client = self.get_client(GoDaddyConfig)
        self.domains = []
        try:
            print(f'\n[*] Attemtping to gather list of {color.blue}{self.name}{color.end} domains...\n')
            # get list of domains manually
            # using godaddypy for this grabs domains that are no longer active on the account
            headers = {
                'Authorization': f'sso-key {GoDaddyConfig.api_key}:{GoDaddyConfig.secret_key}'
            }
            # get only active domains, get top 1,000 results (not sure what the default is, but I've gotten results cutoff before)
            r = requests.get('https://api.godaddy.com/v1/domains?statuses=ACTIVE&limit=1000', headers=headers)
            domain_list = json.loads(r.content)

            for domain in domain_list:
                self.domains.append(domain['domain'])

        except:
            print(f'{color.red}[!] Authentication failure{color.end}')
            exit()

    
    def get_client(self, GoDaddyConfig):
        if GoDaddyConfig.api_key == '' or GoDaddyConfig.secret_key == '':
            print(f'{color.red}[!] Add GoDaddy keys to config file{color.end}')
            exit()
        acct = Account(api_key=GoDaddyConfig.api_key, api_secret=GoDaddyConfig.secret_key)
        return Client(acct)

    
    def print_records(self, domain):
        try:
            print('')
            recs = self.client.get_records(domain)
            print('%-7s%-25s%-60s%-15s' % ('+-------', '+-------------------------','+------------------------------------------------------------', '+---------------+'))
            print('|%-7s|%-25s|%-60s|%-15s|' % ('Type', 'Name', 'Value', 'TTL (Seconds)'))
            for rec in recs:
                value = rec['data'] if len(rec['data']) <= 60 else '%s...' % rec['data'][:57]
                name = rec['name'] if len(rec['name']) <= 25 else '%s...' % rec['name'][:22]
                print('%-7s%-25s%-60s%-15s' % ('+-------', '+-------------------------','+------------------------------------------------------------', '+---------------+'))
                print('|%-7s|%-25s|%-60s|%-15s|' % (rec['type'], name, value, rec['ttl']))
            print('%-7s%-25s%-60s%-15s' % ('+-------', '+-------------------------','+------------------------------------------------------------', '+---------------+'))
            print('')
        except:
            print('[!] Error retrieving DNS records for %s' % domain)


    def update_ip(self, domain, ip):
        try:
            self.client.update_ip(ip, domains=[domain])
            print('\n[+] IP address updated\n')
        except:
            print(f'[!] Error updating DNS records for {domain}')


    def add_record(self, domain, rec_type, name, data, priority=None):
   
        rec = {
            'type': rec_type.upper(),
            'name': name,
            'data': data
        }

        if rec_type.upper() == 'MX':
            rec['priority'] = int(priority)

        try:
            self.client.add_record(domain, rec)
            print('\n[+] Record added\n')
        except Exception as e:
            print(e)
            print(f'{color.red}[!] Error adding DNS record{color.end}\n{e}\n')

    
    def delete_record(self, domain, line):
        # sort of messy with godaddypy - only deleted records by name/type pairing and deletes all that match
        args = line.split(' ')
       
        try:
            if len(args) == 1:
                self.client.delete_records(domain, line)
            elif len(args) == 2:
                self.client.delete_records(domain, args[0], args[1])
            #self.client.delete_records(domain, name, record_type=rec_type)
            print('\n[-] DNS records deleted\n')
        except KeyboardInterrupt:
            print('[!] Cancelled')
        except Exception as e:
            print(f'\n{color.red}[!] Error deleting DNS records{color.end}\n{e}\n')


    def config_from_stock(self, domain, records):
        try:
            print('')
            for rec in records:
                self.client.add_record(domain, rec)
                print(f'[+] Added {rec["type"]} record')
            print('')
        except:
            print('[!] Error adding DNS records')


# colors for the console
class color:
    purple = '\033[95m'
    cyan = '\033[96m'
    darkcyan = '\033[36m'
    blue = '\033[94m'
    green = '\033[92m'
    yellow = '\033[93m'
    red = '\033[91m'
    bold = '\033[1m'
    underline = '\033[4m'
    end = '\033[0m'
