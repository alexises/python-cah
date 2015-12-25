# python-cah : IRC bot for the game cards against humanity

This program provides an IRC bot for the game cards against humanity,

[![Build Status](https://travis-ci.org/alexises/python-cah.svg?branch=master)](https://travis-ci.org/alexises/python-cah)
## Installation
For a simple use of the bot it's realy simple, edit the `config.json` file, and launch `pythonCah` executable,

all the debugging info will be print on the console (at this time, it's not possible to configure easely the
logging settings)

## Configuration
All the configuration is written on JSon, all the parameter available will be describted

### Root parameter

| name | default value | description |
| ---- | ------------- | ----------- |
| ctcp | "python-cah" | string send when CTCP VERSION is issued |
| nick | | nick of the bot |
| ident | nick value | ident send to IDENT command |
| realname | ctcp value | real name show on WHO command |
| token | '!' | prefix that bot check for detecting a command |
| startTimeout | 60 | Timeout before the party begin when player can join |
| pickTimeout | 60 | Timeout for the non czar player to pick a set of cards |
| servers | 1 required | list of serveurs, describted below |
| acl | | list of role attributed fonction of certen irc param, describted below |
| roleMapping | | map command and role to know which role can execute which commande, descrited below |
| autoVoice | False | auto voice people who start a party |

### servers
servers is a list of server where the bot should go

| name | default value | description |
| ---- | ------------- | ----------- |
| server | | address of the server |
| port | 6667 | port which the irc deamon listen |
| token | inherited |  |
| startTimeout | inherited |  |
| pickTimeout | inherited | |
| nick | inherited | |
| ident | inheried | |
| ctcp | inherited | |
| realname | inherited | |
| ssl | False | try to connect using SSL |
| sslCheck | True | check ssl certificate if `ssl` is true |
| withSasl | False | try to initiate an sasl authentication, should provide `password field` |
| password | '' | if withSasl is True, used in sasl authentication, else provided to nickserv to authenticate the bot with service |
| channels | 1 required | describted below |
| autoVoice | inherited | |

### channels 
channels parameter, take a list of channel, describted below

| name | default value | description |
| ---- | ------------- | ----------- |
| channel | | name of irc channel |
| token | inherited |  |
| startTimeout | inherited |  |
| pickTimeout | inherited | |
| autoVoice | inherited | |

### authentication
each command are securted with a separation between anthentication
and authorizzation.

Authentication manage the mapping between irc specific parameters and role

Authorization manage the mapping between rola and command.

### acl (aka authentication parameters)
acl provides a list of parameters describted bellow

| name | default value | description |
| ---- | ------------- | ----------- |
| server | '' (all server) | server filter for this ACE |
| channel | '' (all channel) | channel filter for this ACE |
| nick | '' (all nick) | nick filter for this ACE |
| ircRole | '' (no role | irc role filter, shouild be one of '', '+', '%', '&', '~' |
| role | | role provided when ACE is matched |

### roleMapping (aka authorization parameters)
roleMapping parameter provides a list of role that be allowed to run
a specific command.

To add multiple role that can execute a command, just add multiple line with
different role.

| name | default value | description |
| ---- | ------------- | ----------- |
| command | | command to authorize |
| role | | role that be allowed to use this command |


