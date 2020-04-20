#!/usr/bin/env python3

from godaddypy import Client, Account
from registrars.Namecheap import NamecheapApiClient
from registrars.GoDaddy import GoDaddyApiClient
from configs import GoDaddyConfig, NamecheapConfig, StockDomainConfigs
from requests.exceptions import HTTPError
from time import sleep
import cmd
import argparse
from contextlib import contextmanager
import io
from contextlib import redirect_stdout


# called to move from the ModuleMenu back to the Main Menu
class NavMain(Exception):
    """
    Custom exception class used to navigate to the 'main' menu.
    """
    pass


# Main menu class
class MainMenu(cmd.Cmd):
    client = ''
    registrar = ''

    def __init__(self, registrar):

        cmd.Cmd.__init__(self)

        self.registrar = registrar
        self.init_client()
        
        self.setprompt()

        # for 'help' command
        self.do_help.__func__.__doc__ = '''Displays the help menu'''
        self.doc_header = 'Commands'

    
    # initalize the API client and get domains
    def init_client(self):
        self.client = NamecheapApiClient(NamecheapConfig) if self.registrar == 'Namecheap' else GoDaddyApiClient(GoDaddyConfig)

    
    # set how the prompt will appear
    def setprompt(self):
        self.prompt = f'{color.yellow}NameDaddy{color.blue}#>{color.end} '


    # do nothing if provided empty line
    def emptyline(self):
        pass


    # Main cmd loop
    def cmdloop(self):
        while True:
            try:
                # initialize loop (uses prompt automatically)
                cmd.Cmd.cmdloop(self)
            except KeyboardInterrupt:
                self.exitdaddy()
            except NavMain as e:
                self.setprompt()
  

    # called if unrecognized command is issued
    def default(self, line):
        print('\n{}[!] Unknown syntax. Use \'help\' for list of commands{}\n'.format(color.red, color.end))


    # print all domains in table
    def do_show(self, line):
        '''Display domains'''
        print('')
        print('%-31s' % ('+------------------------------+'))
        print('|%-30s|' % ('Domain Name'))

        for domain in self.client.domains:
            try:
                print('%-31s' % ('+------------------------------+'))
                print('|%-30s|' % (domain))
            except KeyboardInterrupt:
                print('\n[!] Cancelling...\n')
                return
            #sleep(0.1)
        print('%-31s' % ('+------------------------------+'))
        print('')
        


    # if 'exit' issued, prompt the user if they want to exit
    def do_exit(self, line):
        '''Close NameDaddy'''
        raise KeyboardInterrupt


    # exit
    def exitdaddy(self):
        print('')
        print('{}[!] Exiting...{}'.format(color.red, color.end))
        exit()


    # select a domain to use
    def do_use(self, line):
        '''Use <domain>. Select a domain to edit'''
        if line in self.client.domains:
            domain_menu = DomainMenu(self, line)
            domain_menu.cmdloop()
        else:
            print('\n{}[!] Unknown domain: {}{}\n'.format(color.red, line, color.end))


    # tab-complete use with a list of available domains
    def complete_use(self, text, line, begidx, endidx):
        mline = line.partition(' ')[2]
        offs = len(mline) - len(text)
        return [s[offs:] for s in self.client.domains if s.startswith(mline)]


    def do_switch(self, line):
        '''Swtich between GoDaddy and Namecheap API clients'''
        if self.registrar == 'Namecheap':
            self.registrar = 'GoDaddy'
            self.client = GoDaddyApiClient(GoDaddyConfig)
        else:
            self.registrar = 'Namecheap'
            self.client = NamecheapApiClient(NamecheapConfig)


    # format for the menu shown by the 'help' command
    def print_topics(self, header, commands, cmdlen, maxcol):
        if commands:
            self.stdout.write("%s\n" % str(header))
            if self.ruler:
                self.stdout.write("%s\n" % str(self.ruler * len(header)))
            for command in commands:
                self.stdout.write("%s %s\n" % (command.ljust(17), getattr(self, 'do_' + command).__doc__))
            self.stdout.write("\n")


# Menu system for when a module has been loaded with the 'load' cmd
class DomainMenu(cmd.Cmd):

    def __init__(self, mainMenu, domain):
        cmd.Cmd.__init__(self)

        self.domain = domain

        # object to hold the main menu class
        self.mainMenu = mainMenu
        self.prompt = f'{color.yellow}{self.domain}{color.blue}#>{color.end} '

        # 'help' functions
        self.do_help.__func__.__doc__ = '''Displays the help menu'''
        self.doc_header = 'Commands'


    # command loop
    def cmdloop(self):
        cmd.Cmd.cmdloop(self)


    # do nothing if provided empty line
    def emptyline(self):
        pass


    # for unkown commands
    def default(self, line):
        print('\n{}[!] Unknown syntax. Use \'help\' for list of commands{}\n'.format(color.red, color.end))


    def do_updateip(self, line):
        '''updateip <ip addr>. Updates the IP the address domain points to'''
        self.mainMenu.client.update_ip(self.domain, line)

    
    def do_back(self, line):
        '''Return to main menu'''
        raise NavMain()


    def do_records(self, line):
        '''Display DNS records'''
        self.mainMenu.client.print_records(self.domain)
        #show_domain_rec(self.mainMenu.client, self.domain)


    # if 'exit' issued, prompt the user if they want to exit
    def do_exit(self, line):
        '''Close NameDaddy'''
        raise KeyboardInterrupt


    def do_delete(self, line):
        '''GoDaddy: delete <record name> (record type). Deletes DNS records by name or name/type combos. All records matching criteria will be deleted
                  Namecheap: delete <record id>. Delete a record by suppling an ID from the records command'''
        self.mainMenu.client.delete_record(self.domain, line)

    
    def complete_stockconfig(self, text, line, begidx, endidx):
        options = [config['name'] for config in StockDomainConfigs.configs]
        mline = line.partition(' ')[2]
        offs = len(mline) - len(text)
        return [s[offs:] for s in options if s.startswith(mline)]


    def do_stockconfig(self, line):
        '''stock config <config name>. Configure a new domain with preset records from config file'''
        if line in [config['name'] for config in StockDomainConfigs.configs]:
            config = next((item for item in StockDomainConfigs.configs if item['name'] == line), None)
            self.mainMenu.client.config_from_stock(self.domain, config['DNS_records'])
        else:
            print('\n{}[!] Unknown config: {}{}\n'.format(color.red, line, color.end))


    def do_add(self, line):
        '''add <type> (priority) <name> <value>. Add a DNS record. Priority is only for MX'''
        if line.split(' ', 1)[0].upper() == 'MX':
            args = line.split(' ', 3)
            if len(args) < 4 or not args[1].isdigit():
                print('\n{}[!] Syntax for MX record is <type> <priority> <name> <value>{}\n'.format(color.red, color.end))
                return
            self.mainMenu.client.add_record(self.domain, args[0], args[2], args[3], args[1])
        else:
            args = line.split(' ', 2)
            self.mainMenu.client.add_record(self.domain, args[0], args[1], args[2])
        

    # format for the menu shown by the 'help' command
    def print_topics(self, header, commands, cmdlen, maxcol):
        if commands:
            self.stdout.write("%s\n" % str(header))
            if self.ruler:
                self.stdout.write("%s\n" % str(self.ruler * len(header)))
            for command in commands:
                self.stdout.write("%s %s\n" % (command.ljust(17), getattr(self, 'do_' + command).__doc__))
            self.stdout.write("\n")
    

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


def getArgs():
    parser = argparse.ArgumentParser(description="used to configure DNS for GoDaddy and Namecheap domains", formatter_class=argparse.RawDescriptionHelpFormatter)

    parser.add_argument('--namecheap', action="store_true", dest='namecheap', help='Nessus account username', required=False)

    args = parser.parse_args()
    return args.namecheap


def main():
    namecheap = getArgs()
    print(f'''
_____   __                      ________       _________________        
___  | / /_____ _______ ___________  __ \_____ ______  /_____  /____  __
__   |/ /_  __ `/_  __ `__ \  _ \_  / / /  __ `/  __  /_  __  /__  / / /
_  /|  / / /_/ /_  / / / / /  __/  /_/ // /_/ // /_/ / / /_/ / _  /_/ / 
/_/ |_/  \__,_/ /_/ /_/ /_/\___//_____/ \__,_/ \__,_/  \__,_/  _\__, /  
                                                               /____/   
                           {color.yellow}Who's your daddy?{color.end}
    ''')
    
    main = MainMenu('Namecheap' if namecheap else 'GoDaddy')
  

    main.cmdloop()


if __name__ == '__main__':
    main()