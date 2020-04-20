from namecheap import Api
from contextlib import contextmanager
import io
from contextlib import redirect_stdout


class NamecheapApiClient():
    # used to prevent PyNamecheap form printing every request and response
    trap = io.StringIO()
    
    name = 'Namecheap'
    client = ''
    domains = []

    def __init__(self, NamecheapConfig):
        self.client = self.get_client(NamecheapConfig)
        self.domains = self.get_domains()


    def get_client(self, NamecheapConfig):
        if NamecheapConfig.api_key == '' or NamecheapConfig.username == '':
            print(f'{color.red}[!] Add Namecheap configs to config file{color.end}')
            exit()
        return Api(NamecheapConfig.username, NamecheapConfig.api_key, NamecheapConfig.username, NamecheapConfig.ip_address, sandbox=False)


    def get_domains(self):
        try:
            print(f'\n[*] Attemtping to gather list of {color.blue}{self.name}{color.end} domains...\n')
            domain_list = self.client.domains_getList()
            with redirect_stdout(self.trap):
                domain_list.__next__()
            domains = [d['Name'] for d in domain_list.results]
            return domains
        except:
            print(f'{color.red}[!] Authentication failure{color.end}')
            exit()

    def print_records(self, domain):
        try:
            print('')
            with redirect_stdout(self.trap):
                recs = self.client.domains_dns_getHosts(domain)
            print('%-4s%-7s%-25s%-60s%-15s' % ('+----', '+-------', '+-------------------------','+------------------------------------------------------------', '+---------------+'))
            print('|%-4s|%-7s|%-25s|%-60s|%-15s|' % ('ID', 'Type', 'Name', 'Address', 'TTL (Seconds)'))
            for idx, rec in enumerate(recs):
                value = rec['Address'] if len(rec['Address']) <= 60 else '%s...' % rec['Address'][:57]
                name = rec['Name'] if len(rec['Name']) <= 25 else '%s...' % rec['Name'][:22]
                print('%-4s%-7s%-25s%-60s%-15s' % ('+----', '+-------', '+-------------------------','+------------------------------------------------------------', '+---------------+'))
                print('|%-4s|%-7s|%-25s|%-60s|%-15s|' % (idx, rec['Type'], name, value, rec['TTL']))
            print('%-4s%-7s%-25s%-60s%-15s' % ('+----', '+-------', '+-------------------------','+------------------------------------------------------------', '+---------------+'))
            print('')
        except:
            print('[!] Error retrieving DNS records for %s' % domain)


    def update_ip(self, domain, ip):
        recs = []
        
        try:
            # get all records
            with redirect_stdout(self.trap):
                recs = self.client.domains_dns_getHosts(domain)
            
            # find and delte all 'A' records
            for idx, rec in enumerate(recs):
                if rec['Type'] == 'A':
                    self.delete_record(domain, idx, record=rec)
                    print(f'[*] Deleted A record with address {rec["Address"]}')

            # add 'A' record with new IP
            self.add_record(domain, 'A', '@', ip)
            #print('\n[+] IP address updated\n')
        except:
            print(f'\n[!] Error updating DNS records for {domain}\n')

    
    def add_record(self, domain, rec_type, name, data, priority=None):
        new_rec = {
            'RecordType': rec_type,
            'HostName': name,
            'Address': data
        }

        if rec_type.upper() == 'MX':
            new_rec['MXPref'] = int(priority)
            new_rec['EmailType'] = 'MX'

        try:
            with redirect_stdout(self.trap):
                self.client.domains_dns_addHost(domain, new_rec)
            print('\n[+] Record added\n')
        except Exception as e:
            print(e)
            print(f'{color.red}[!] Error adding DNS record{color.end}\n{e}\n')


    def delete_record(self, domain, record_id, record=None):
        # delete record if provided
        if record:
            with redirect_stdout(self.trap):
                self.client.domains_dns_delHost(domain, record)
                
        # else delete record by ID
        else:
            if record_id.isdigit():
                with redirect_stdout(self.trap):
                    recs = self.client.domains_dns_getHosts(domain)
                    self.client.domains_dns_delHost(domain, recs[int(record_id)])
                print('\n[-] DNS records deleted\n')
            else:
                print('\n[!] Namecheap records must be deleted by supplying the ID number of a record\n')


    def config_from_stock(self, domain, records):
        # first need to convert each record dict into Namecheap format
        for rec in records:
            rec['RecordType'] = rec.pop('type')
            rec['HostName'] = rec.pop('name')
            rec['Address'] = rec.pop('data')
            if 'priority' in rec:
                rec['MXPref'] = rec.pop('priority')
                rec['EmaiType'] = 'MX'

        try:
            print('')
            for rec in records:
                
                with redirect_stdout(self.trap):
                    self.client.domains_dns_addHost(domain, rec)
                print(f'[+] Added {rec["RecordType"]} record')
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
