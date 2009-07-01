#!/usr/bin/env python

import sys, os, os.path, xml.sax.handler
from xml.sax import make_parser 

class Handler(xml.sax.handler.ContentHandler) :
  def __init__(self) :
    pass
    
  def startElementNS(self, name, qname, attrs): 
    if name == ("http://www.xmpp.org/extensions/xep-0227.html#ns", "host") :
      self.server = attrs.getValueByQName("jid")
      for dir in [os.path.join(self.server, d) for d in ["accounts", "roster", "private", "vcard"]] :
        if not os.path.exists(dir) :
          os.makedirs(dir)
    elif name == ("http://www.xmpp.org/extensions/xep-0227.html#ns", "user") :
      self.user = attrs.getValueByQName("name")
      file = open(self.getDataFileName("accounts"), "w")
      file.write("return { password = \"%(pass)s\" }\n" % {"pass" : attrs.getValueByQName("password").replace("\"", "\\\"") })
      file.close()
    elif name == ("jabber:iq:roster", "query") :
      self.rosterItems = []
    elif name == ("jabber:iq:roster", "item") :
      self.rosterItem = (
        self.getAttribute(attrs, "jid"), 
        self.getAttribute(attrs, "name"), 
        self.getAttribute(attrs, "subscription"), 
        self.getAttribute(attrs, "ask"), 
        [])
    elif name == ("jabber:iq:roster", "group") :
      self.text = ""
  
  def endElementNS(self, name, qname) : 
    if name == ("jabber:iq:roster", "query") :
      file = open(self.getDataFileName("roster"), "w")
      file.write("return {")
      for item in self.rosterItems :
        file.write("[\"%(jid)s\"] = {" % { "jid": item[0].encode("utf-8") })
        if item[1] != None :
          file.write("[\"name\"] = \"%(name)s\"," % { "name": item[1].encode("utf-8") })
        if item[2] != None :
          file.write("[\"subscription\"] = \"%(subscription)s\"," % { "subscription": item[2].encode("utf-8") })
        if item[3] != None :
          file.write("[\"ask\"] = \"%(ask)s\"," % { "ask": item[3].encode("utf-8") })
        file.write("[\"groups\"] = { ")
        for group in item[4] :
          file.write("[\"%(group)s\"] = true," % {"group": group})
        file.write("}")
        file.write("},\n")
      file.write("}")
      file.close()
    elif name == ("jabber:iq:roster", "item") :
      self.rosterItems.append(self.rosterItem)
    elif name == ("jabber:iq:roster", "group") :
      self.rosterItem[4].append(self.text)
  
  def characters(self, text) :
    self.text += text

  def getDataFileName(self, data) :
    return os.path.join(self.server, data, self.user + ".dat")

  def getAttribute(self, attributes, attribute) :
    try :
      return attributes.getValueByQName(attribute)
    except KeyError :
      return None

assert(len(sys.argv) == 2)

handler = Handler()
parser = make_parser()    
parser.setFeature(xml.sax.handler.feature_namespaces, 1)
parser.setContentHandler(handler)
parser.parse(open(sys.argv[1]))
