#!/bin/python

from collections import namedtuple

TabsType = namedtuple("TabsType", ['edit', 'label', 'textread', 'lastlines'])

def ClearText(tabsType):
    return tabsType._replace( textread="", lastlines=-1 )