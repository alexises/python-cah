from io import MultiIrcClient
import logging
import sys

logger = logging.getLogger(__name__)
def test():
    logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)
    logger.info('start app')
    servers = []
    servers.append({ 'server' : 'irc.iiens.net', 'port' : 7000, 'nick' : 'cahBot', 'ctcp' : 'cahBot', 'ssl' : True, 'sslCheck' : False })
    servers.append({ 'server' : 'irc.freenode.net', 'port' : 7000, 'nick' : 'cahBot', 'ctcp' : 'cahBot', 'ssl' : True })
    logger.debug('{}'.format(servers))
    item = MultiIrcClient(servers)
    item.start()
       
    while 1:
        pass 
if __name__ == '__main__':
   test()
