from configs import Route53Config
import route53
import requests
import json
from texttable import Texttable

class Route53ApiClient:
    name = ''
    client = ''
    domains = []

    def __init__(self, Route53Config):
        self.client = self.get_client(Route53Config)
        self.domains = []
        self.zones = {}
        try:
            print(f'\n[*] Attemtping to gather list of {color.blue}{self.name}{color.end} domains...\n')
            for zone in self.client.list_hosted_zones():
                self.domains.append(zone.name[:-1])
                self.zones[zone.name[:-1]] = zone.id

        except:
            print(f'{color.red}[!] Authentication failure{color.end}')
            exit()

    
    def get_client(self, GoDaddyConfig):
        if Route53Config.aws_access_key_id == '' or Route53Config.aws_secret_access_key == '':
            print(f'{color.red}[!] Add Route53 keys to config file{color.end}')
            exit()
        return route53.connect(aws_access_key_id=Route53Config.aws_access_key_id, aws_secret_access_key=Route53Config.aws_secret_access_key)

    
    def print_records(self, domain):
        try:
            print('')
            zone = self.client.get_hosted_zone_by_id(self.zones[domain])
            table = Texttable(120)
            table.header(['Type', 'Name', 'Value', 'TTL (Seconds)'])
            for set in zone.record_sets:
                value = ''
                for indx, rec in enumerate(set.records):
                    if indx == 0:
                        value += rec
                    else:
                        value += f'\n{rec}'        
                rec_type = set.__class__.__name__.replace('ResourceRecordSet', '')
                table.add_row([rec_type, set.name[:-1], value, set.ttl])
            print(table.draw())
            print('')
        except:
            print('[!] Error retrieving DNS records for %s' % domain)


    def update_ip(self, domain, ip):
        try:
            zone = self.client.get_hosted_zone_by_id(self.zones[domain])
            for set in zone.record_sets:
                rec_type = set.__class__.__name__.replace('ResourceRecordSet', '')
                if set.name[:-1] == domain and rec_type == 'A':
                    set.records = [ip]
                    set.save()
                    break
            print('\n[+] IP address updated\n')
        except:
            print(f'[!] Error updating DNS records for {domain}')


    def add_record(self, domain, rec_type, name, data, priority=None):
        edited = False
        rec_type = rec_type.upper()
        zone = self.client.get_hosted_zone_by_id(self.zones[domain])

        # route53 records names need to end with '.yourdomain.com'
        suffix = f'.{domain}'
        if not name.endswith(suffix):
            name += suffix

        try:
            for set in zone.record_sets:
                typ = set.__class__.__name__.replace('ResourceRecordSet', '')
                if set.name[:-1] == name and typ == rec_type:
                    set.records = [data]
                    set.save()
                    edited = True
                    print('\n[+] Existing record edited\n')
                    break
            
            if not edited:
                if rec_type == 'A':
                    zone.create_a_record(name=name, values=[data])
                elif rec_type == 'AAAA':
                    zone.create_aaaa_record(name=name, values=[data])
                elif rec_type == 'CNAME':
                    zone.create_cname_record(name=name, values=[data])
                elif rec_type == 'MX':
                    if priority is None:
                        priority = '10'
                    zone.create_mx_record(name=name, values=[f'{priority} {data}'])
                elif rec_type == 'NS':
                    zone.create_ns_record(name=name, values=[data])
                elif rec_type == 'PTR':
                    zone.create_ptr_record(name=name, values=[data])
                elif rec_type == 'SRV':
                    zone.create_srv_record(name=name, values=[data])
                elif rec_type == 'TXT':
                    zone.create_txt_record(name=name, values=[data])
                else:
                    print(f'{color.red}[!] Record type \'{rec_type}\' does not exist{color.end}\n')

                print('\n[+] Record added\n')
        except Exception as e:
            print(f'{color.red}[!] Error adding DNS record{color.end}\n{e}\n')

    
    def delete_record(self, domain, line):
        # combined this method with the GoDaddy method of record deletion, aka it's not the most straightforward
        args = line.split(' ')
        name = args[0]
        del_type = args[1].upper()
        deleted = False

        try:
            zone = self.client.get_hosted_zone_by_id(self.zones[domain])
            for set in zone.record_sets:
                rec_type = set.__class__.__name__.replace('ResourceRecordSet', '')
                if set.name[:-1] == name and rec_type == del_type:
                    set.delete()
                    print('\n[-] DNS records deleted\n')
                    deleted = True
                    break
            if not deleted:
                print('\n[!] No DNS records found matching name and type')
        except KeyboardInterrupt:
            print('[!] Cancelled')
        except Exception as e:
            print(f'\n{color.red}[!] Error deleting DNS records{color.end}\n{e}\n')

    def config_from_stock(self, domain, records):
        try:
            print('')
            for rec in records:
                if rec['type'].upper() == 'MX':
                    self.add_record(domain, rec['type'], rec['name'], rec['data'], rec['priority'])
                else:
                    self.add_record(domain, rec['type'], rec['name'], rec['data'])
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
