

import pandas as pd
from modelo.SententreeModel import Sententree
import json

class Sententopic:
  def __init__(self,dataDf,numPalabrasPerTopic):  

    self.topicList=self.getTopicList()
    self.numPalabrasPerTopic=numPalabrasPerTopic
    dataDf['topico'] = dataDf.apply(lambda x: self.dividirDfTopicos(x.tweetFiltrado) , axis=1)

    self.SententopicDfList=self.createSententopicDf(dataDf)
    self.SententopicList=[]
    
    for i in range(len(self.SententopicDfList)):
    #for i in range(2):
      self.SententopicList.append(
            Sententree(self.SententopicDfList[i],
                       numPalabrasPerTopic,
                       self.topicList[i],
                       i
                       ))
  #-------------------------------------------------------
  def dividirDfTopicos(self,tweet):
    resultTopics=[]
    for topic in self.topicList:
      numPalabras=0
      for word in tweet.split():
        if word in topic:
          numPalabras+=1
      if numPalabras==0:
        resultTopics.append(-1)
        continue;  
      resultTopics.append(float(numPalabras/len(topic)))
    return resultTopics.index(max(resultTopics))  
  #-------------------------------------------------------
  def getTopicList(self):
    return [["pay", "apple", "payment", "interest", "equal", "split", "0", "purchase", "week", "cost", "order", "klarna", "6", "wallet", "buy", "introducing", "4", "online", "directly", "tap", "allows", "tracking", "allow", "digital", "break", "info", "announces", "service", "challenge", "introduced"],
    ["keynote", "event", "day", "park", "today", "announcement", "tim", "craig", "watching", "morning", "cook", "join", "ready", "minute", "fun", "excited", "started", "stuff", "developer", "special", "team", "stream", "coverage", "bit", "community", "year", "good", "person", "glass", "tweet"],
    ["lock", "screen", "font", "lockscreen", "clock", "widget", "wallpaper", "style", "bottom", "roll", "option", "io", "activity", "multiple", "message", "notification", "customize", "change", "focus", "16", "edit", "customizable", "mark", "unread", "ios16", "live", "customization", "biggest", "imessages", "undo"],
    ["heart", "workout", "sleep", "rate", "zone", "afib", "medication", "history", "metric", "track", "watch", "#applewatch", "face", "health", "fitness", "tracking", "custom", "9", "siri", "drug", "#watchos9", "sensor", "reminder", "watchos", "running", "interaction", "form", "ui", "app", "calendar"],
    ["gpu", "transistor", "cpu", "5nm", "unified", "24gb", "memory", "25", "core", "performance", "medium", "billion", "faster", "10", "20", "m1", "#m2", "power", "gen", "announcing", "chip", "8", "18", "glance", "pc", "m2", "announces", "latest", "number", "processor"],
    ["safety", "location", "abusive", "domestic", "access", "relationship", "abuse", "reset", "check", "privacy", "personal", "sharing", "account", "data", "help", "setting", "people", "icloud", "case", "shared", "helpful", "family", "tool", "stop", "library", "content", "share", "allows", "photo", "automatically"],
    ["car", "cluster", "instrument", "carplay", "vehicle", "integration", "next-gen", "#carplay", "manufacturer", "late", "2023", "play", "speed", "entire", "industry", "ui", "control", "experience", "showing", "google", "level", "integrated", "seriously", "power", "building", "generation", "sneak", "powered", "pretty", "smart"],
    ["retina", "136", "liquid", "magsafe", "1080p", "pound", "charging", "speaker", "27", "notch", "port", "spatial", "thin", "18", "bezel", "audio", "inch", "display", "fast", "hour", "color", "battery", "high", "space", "keyboard", "charge", "min", "midnight", "charger", "colour"],
    ["window", "manager", "group", "spotlight", "safari", "search", "ventura", "multitasking", "mail", "tab", "metal", "stage", "desktop", "macos", "side", "collaboration", "continuity", "improved", "passkey", "facetime", "overlapping", "#macosventura", "desk", "freeform", "view", "shortcut", "front", "called", "handoff", "ipad"],
    ["macbook", "pro", "m2", "air", "13-inch", "education", "month", "#macbookpro", "13", "model", "1299", "price", "pricing", "india", "1199", "r", "start", "beta", "launch", "chip", "2022", "public", "starting", "14", "july", "fall", "release", "macbooks", "official", "#macbookair"]]
  #-------------------------------------------------------  
  def createSententopicDf(self,df):
    result=[]
    for topic in range(len(self.topicList)):
      topicDf=df.loc[df['topico'] == topic]
      #print(f"topico {topic} tienen {topicDf.shape}")
      topicDf.reset_index(drop=True, inplace=True)
      result.append(topicDf)
    return result
  #-------------------------------------------------------
  def printSententopic(self):
    for tree in self.SententopicList:
      tree.printSententree()
  #-------------------------------------------------------
  def getDataJson(self):
    nodosID=[]
    nodos=[]
    links=[]
    restricciones=[]
    grupos=[]
    

    for sententree in self.SententopicList:
      if not sententree.visible:
        continue
      nodos.extend(sententree.getNodes())
      links.extend(sententree.getLinks())
      restricciones.extend(sententree.getRestricciones())
      grupos.extend(sententree.getGrupos())

    print("----------------------------------------------")
    print(grupos)
    print("----------------------------------------------")
    #nodo inicial y links y restricciones

    nodosID= [ nodo['name'] for nodo in nodos]
    nodosID.append("Sententopic")
    print(len(nodos))
    print(nodosID)
    
    nodos.append(
        {
          "label":"Sententopic",
          "width":60,
          "heigth":40
        }
    )
    
    print("actualizar enlaces")
    #actualizar enlaces
    for link in links:
      
      source=nodosID.index(link['source'])
      target=nodosID.index(link['target'])
      print(f"source {type(source)}")
      print(f"target {target}")
      link['source']=source
      link['target']=target
      print(f"link {link}")
    # actualizar constraits
    for restriccion in restricciones:
      if(len(restriccion)==4):
        restriccion['left']=nodosID.index(restriccion['left'])
        restriccion['right']=nodosID.index(restriccion['right'])
        continue
      for offset in restriccion['offsets']:
        offset['node']=nodosID.index(offset['node'])
      print(restriccion)
    # crear enlaces del nodo
    for sententree in self.SententopicList:
      if not sententree.visible:
        continue
      links.append(
          {
            "source":len(nodos)-1,
            "target":nodosID.index(sententree.nodosListID[0]),
            "lenght":300,
          }
      )
      restricciones.append(
          {
            "axis":"x",
            "left":len(nodos)-1,
            "right":nodosID.index(sententree.nodosListID[0]),
            "gap":300
          }
      )
    

    #actualizar grupos
    for grupo in grupos:
      grupo['leaves']=[nodosID.index(nodo) for nodo in grupo['leaves']]

    result={
        "nodes":nodos,
        "links":links,
        "constraints":restricciones,
        "groups":grupos
      }
    return result
