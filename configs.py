class GoDaddyConfig:
    api_key = ''
    secret_key = ''

class NamecheapConfig:
    api_key = ''
    username = '' # your namecheap username
    ip_address = '' # IP whitelisted in namecheap


class StockDomainConfigs:
    configs = [
        {
            'name': 'StockConfig1',
            'DNS_records': [
                {
                    'type': 'MX',
                    'name': '@',
                    'data': 'mx.mydomain.com',
                    'priority': 10
                },
                {
                    'type': 'TXT',
                    'name': '@',
                    'data': 'v=spf1 ip4:ipv4address include:mx.mydomain.com ~all',
                },
                {
                    'type': 'TXT',
                    'name': '_dmarc',
                    'data': 'v=DMARC1; p=reject',
                }
            ]
        },
        {
            'name': 'StockConfig2',
            'DNS_records': [
                {
                    'type': 'MX',
                    'name': '@',
                    'data': 'mx.mydomain2.com',
                    'priority': 10
                },
                {
                    'type': 'TXT',
                    'name': '@',
                    'data': 'v=spf1 ip4:ipv4address include:mx.mydomain2.com ~all',
                },
                {
                    'type': 'TXT',
                    'name': '_dmarc',
                    'data': 'v=DMARC1; p=reject',
                }
            ]
        }
    ]
