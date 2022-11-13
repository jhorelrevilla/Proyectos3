from anytree import Node, RenderTree
import pandas as pd
from anytree.dotexport import RenderTreeGraph
from anytree.exporter import DotExporter
import json

"""-----------------------------------------------------"""


class Tokenize:
    def __init__(self, df):
        # diccionario de todos los tokens unicos
        self.itemset = self.getItemset(df)
        self.data = df[['tweet', 'tweetFiltrado', 'likes_count']].copy()
        # convierte el tweet en una serie de tokens
        self.data['tokens'] = self.data['tweetFiltrado'].apply(
            lambda x: self.tokenizeTweet(str(x), self.itemset))

    def getItemset(self, BD):
        result = {}
        contador = 0
        for tweet in BD['tweetFiltrado'].values.tolist():
            for word in tweet.split():
                if (word in result):
                    continue
                else:
                    result[word] = contador
                    contador += 1
        return result

    def tokenizeTweet(self, tweet, tokenDict):
        result = []
        for word in tweet.split():
            result.append(str(tokenDict[word]))
        return ' '.join(result)


"""-----------------------------------------------------"""


class Sententree:
    def __init__(self, dataDf, palabrasNecesarias, topic, numTopic):
        self.tokens = Tokenize(dataDf)
        # rawTopic=self.getTopic(numTopic)
        self.nodosListID = []
        self.topic = self.tokenizarTopic(topic)
        self.numTopic = numTopic
        # nodo=getNodo
        self.maxFont = 180
        self.minFont = 100
        self.maxBdSize = 0
        # crear nodo a partir de la palabra con mayor apoyo
        self.nodoRaiz = self.getNodeTopic(dataDf)
        # self.topic.remove(self.nodoRaiz.seq[0])
        self.leafNodes = self.generacionPatrones(
            self.nodoRaiz, palabrasNecesarias)
    # ------------------------------------------------------------------------------------

    def getNodoLargestSupport(self, leafNodes):
        pos = 0
        # busca la posicion del nodo con mayor cantidad de elementos en la DB
        for nodePos in range(len(leafNodes)):
            if (len(leafNodes[pos].DB) < len(leafNodes[nodePos].DB)):
                pos = nodePos
        result = leafNodes[pos]
        del leafNodes[pos]
        return result
    # ------------------------------------------------------------------------------------

    def tokenizarTopic(self, rawTopic):
        result = []
        for word in rawTopic:
            result.append(str(self.tokens.itemset[word]))
        return result
    # ------------------------------------------------------------------------------------

    def growSeqTopics(self, s):
        s0 = []
        s1 = []
        bdDict = {}
        # cuenta el numero de token
        for tweetId in s.DB:
            for token in self.tokens.data['tokens'][int(tweetId)].split():
                if token in bdDict:
                    bdDict[token] += 1
                else:
                    bdDict[token] = 1

        # Escoger palabras del topico
        word = None
        if (len(s.seq) > 1):
            # evita palabras de la secuencia
            #print(f"tam seq {len(s.seq)}")
            if (len(s.seq) > 0):
                for wordSeq in s.seq:
                    if wordSeq in bdDict:
                        bdDict.pop(wordSeq)
            word = str(max(bdDict, key=lambda x: bdDict[x]))
        else:
            topicDict = {}
            for wordTopic in self.topic:
                if wordTopic in bdDict:
                    topicDict[wordTopic] = bdDict[wordTopic]
            word = str(max(topicDict, key=lambda x: topicDict[x]))

        # divide la bd
        for tweetId in s.DB:
            tweetTokens = self.tokens.data['tokens'][int(tweetId)].split()
            if word in tweetTokens:
                s0.append(tweetId)
            else:
                s1.append(tweetId)
        return word, list(s0), list(s1)
    # ------------------------------------------------------------------------------------

    def generacionPatrones(self, nodoRaiz, palabrasNecesarias):
        leafNodes = []
        leafNodes.append(nodoRaiz)

        while (palabrasNecesarias > 0 and leafNodes):
            # pop pattern with the largest support from leaf sequential patterns
            s = self.getNodoLargestSupport(leafNodes)
            newS0 = None
            newS1 = None
            if (not s.children):
                # Find the most frequent super sequences s' of s that is exactly one word longer than s;
                # word,s0,s1=growSeq(s,tokens)
                word, s0, s1 = self.growSeqTopics(s)
                """
                print(f"escoge la palabra {list(self.tokens.itemset.keys())[int(word)]} token {word}")
                print(f"s0 contiene {len(s0)}")
                print(f"s1 contiene {len(s1)}")
                print(f"seq {s.seq}")
                print(f"Top Tweets {s0[:2]}")
                """
                # crea el nodo s0(palabra) y s1(no palabra)
                # Agrega s0 como hijo izq
                palabraCorpus = list(self.tokens.itemset.keys())[int(word)]
                newS0 = Node(f"{palabraCorpus}({len(s0)})", parent=s)
                newS0.word=int(word)
                newS0.DB = s0
                newS0.seq = list(s.seq)
                newS0.seq.append(word)
                """ CREAR NODOS PARA EL GRAFO"""
                newS0.graphNodes = list(s.graphNodes)

                fontSize = ((self.maxFont*len(s0))/self.maxBdSize)
                if fontSize < self.minFont:
                    fontSize += self.minFont
                # self.tokens.data['tokens'][int(tweetId)]
                topTweets = [self.tokens.data['tweetFiltrado']
                             [int(tweetId)] for tweetId in s0[:1]]

                nodoJson = {
                    "name": f"{self.numTopic}-{palabrasNecesarias}",
                    "fontSize": fontSize,
                    "label": palabraCorpus,
                    "rawText": str(topTweets),
                    "rawTextID": s0[:1],
                    "size": len(s0),
                    "width": 100,
                    "height": 30
                }
                self.nodosListID.append(
                    f"{self.numTopic}-{palabrasNecesarias}")
                newS0.graphNodes.append(nodoJson)
                """ CREAR ARISTAS PARA EL GRAFO"""
                newS0.graphLinks = dict(s.graphLinks)
                newS0.graphLinks[word] = f"{self.numTopic}-{palabrasNecesarias}"

                # Agrega s1 como hijo derecho
                newS1 = Node(f"nodo nulo({len(s1)})", parent=s)
                newS1.DB = s1
                newS1.seq = list(s.seq)
                newS1.graphNodes = list(s.graphNodes)
                newS1.graphLinks = dict(s.graphLinks)

            palabrasNecesarias -= 1
            # push s' and s to leaf sequential patterns
            if (newS0 and newS1):
                leafNodes.append(newS0)
                leafNodes.append(newS1)
            # print("-------------------------")
        return leafNodes
    # ------------------------------------------------------------------------------------

    def getNodeTopic(self, df):
        nodoRaiz = Node("All tweets")
        nodoRaiz.seq = []

        nodoRaiz.DB = [i for i in range(0, df.shape[0])]

        word, s0, s1 = self.growSeqTopics(nodoRaiz)

        self.topic.remove(word)

        palabraCorpus = list(self.tokens.itemset.keys())[int(word)]
        newNodo = Node(f"{palabraCorpus}")
        newNodo.id = 0
        newNodo.word=int(word)
        newNodo.DB = s0
        newNodo.seq = [word]
        self.maxBdSize = len(s0)
        topTweets = [self.tokens.data['tweetFiltrado']
                     [int(tweetId)] for tweetId in s0[:1]]
        label = list(self.tokens.itemset.keys())[int(word)]
        nodoJson = {
            "name": f"{self.numTopic}-0",
            "fontSize": self.maxFont,
            "label": label,
            "rawText": str(topTweets),
            "rawTextID": s0[:1],
            "size": len(s0),
            "width": 100,
            "height": 30
        }
        self.nodosListID.append(f"{self.numTopic}-0")
        newNodo.graphNodes = [nodoJson]
        newNodo.graphLinks = {word: f"{self.numTopic}-0"}
        return newNodo
    # ------------------------------------------------------------------------------------

    def getNodePos(self, node):
        return self.nodosListID.index(node)+self.numTopic
    # ------------------------------------------------------------------------------------

    def getData(self):

        nodos = self.getNodes()
        links = self.getLinks()
        restricciones = self.getRestricciones()
        grupos = self.getGrupos()

        result = {
            "nodes": nodos,
            "links": links,
            "constraints": restricciones,
            "groups": grupos
        }
        return result
    # ------------------------------------------------------------------------------------

    def getGrupos(self):
        grupos = [
            {
                "leaves": [i+self.numTopic for i in range(len(self.getNodes()))],
                "grupo":self.numTopic
            }
        ]
        return grupos
    # ------------------------------------------------------------------------------------

    def getLinks(self):
        result = []
        dicSeq = {}
        grafo={}
        secuencias = []
        # extraer secuencias
        for leaf in self.leafNodes:
            secuencia = []
            pointer = leaf
            if (pointer.name.find("nodo nulo") != -1):
                continue
            while (pointer.parent):
                if (pointer.name.find("nodo nulo") != -1):
                    pointer = pointer.parent
                    continue
                secuencia.append(pointer)
                pointer = pointer.parent
            secuencia.append(pointer)

            secuencias.append(secuencia)

        for seq in secuencias:
            for word in seq:
                print(f"{word.name}  ", end="")
            print("")

        for secuencia in secuencias:
          print("-----------------")
          print(f"palabra {secuencia[0].name}") 
          listPalabras=[ str(i.word) for i in secuencia]
          topTweetId = secuencia[0].graphNodes[-1]['rawTextID'][0]
          topTweet = self.tokens.data['tokens'][int(topTweetId)].split()

          print(f"listPalabras {listPalabras}")
          print (f"topTweet {topTweet}")
          
          tempo = {}

          # recorre la secuencia y ordena las palabras en el orden que aparecen
          for palabra in listPalabras:
            tempo[palabra] = topTweet.index(palabra)
          #print(f"tempo {tempo}")
          tempo = {k: v for k, v in sorted(
            tempo.items(), key=lambda item: item[1])}
          print(f"orden que aparecen {tempo}")
          print(secuencia[0].graphLinks)

          
          for word in range(1,len(listPalabras)):
            source = list(tempo.keys())[word-1]
            source = secuencia[0].graphLinks[source]

            target = list(tempo.keys())[word]
            target = secuencia[0].graphLinks[target]

            if source not in grafo:
              grafo[source] = [target]
            else:
              if target not in grafo[source]:
                grafo[source].append(target)
        print(f"grafo {grafo}")
        for k, v in grafo.items():
          for target in v:
              result.append(
                  {
                    "source": self.getNodePos(k),
                    "target": self.getNodePos(target)
                  }
              )
        print("####################################################")
        """
        for secuencia in secuencias:
          for seq in secuencia:
            print("--------------------------")
            # consigue el tweet mas valioso de
            topTweetId = seq.graphNodes[-1]['rawTextID'][0]
            # almacena los tokens
            topTweet = self.tokens.data['tokens'][int(topTweetId)].split()

            #print (f"topTweet {topTweet}")
            tempo = {}
            # recorre la secuencia y ordena las palabras en el orden que aparecen
            for nodo in seq.graphLinks:
                #            Posicion palabra % tam links
                #tempo[nodo]=topTweet.index(nodo) % (len(seq.graphLinks)+1)
                tempo[nodo] = topTweet.index(nodo)
            #print(f"tempo {tempo}")
            tempo = {k: v for k, v in sorted(
                tempo.items(), key=lambda item: item[1])}
            print(f"orden que aparecen {tempo}")

            print(f"seq.graphLinks {seq.graphLinks}")

            # genera los enlaces con las palabras seguidas
            for palabra in range(1, len(seq.seq)):

                source = list(tempo.keys())[palabra-1]
                source = seq.graphLinks[source]

                target = list(tempo.keys())[palabra]
                target = seq.graphLinks[target]

                print(f"source {source}")
                
            result.append(
              {
                "source":self.getNodePos(source),
                "target":self.getNodePos(target)
              }
            )
        
                if source not in dicSeq:
                    dicSeq[source] = [target]
                else:
                    if target not in dicSeq[source]:
                        dicSeq[source].append(target)

        # print(json.dumps(result))
        # print("----------------")
        #print(dicSeq)

        for k, v in dicSeq.items():
            for target in v:
                result.append(
                    {
                        "source": self.getNodePos(k),
                        "target": self.getNodePos(target)
                    }
                )
        """
        return result
    # ------------------------------------------------------------------------------------

    def getRestricciones(self):
        result = []
        restriccionXSource = {}
        restriccionXTarget = {}
        for link in self.getLinks():
            constrait = {
                "axis": "x",
                "left": link["source"],
                "right": link["target"],
                "gap": 50
            }
            result.append(constrait)
            if (link['source'] in restriccionXSource):
                restriccionXSource[link['source']].append(link['target'])
            else:
                restriccionXSource[link['source']] = [link['target']]

            if (link['target'] in restriccionXTarget):
                restriccionXTarget[link['target']].append(link['source'])
            else:
                restriccionXTarget[link['target']] = [link['source']]
        print(restriccionXSource)
        print(restriccionXTarget)

        for k, v in restriccionXSource.items():
            if (len(v) >= 2):
                newRestriction = {
                    "type": "alignment",
                    "axis": "x",
                    "offsets": []
                }
                for nodo in v:
                    newRestriction["offsets"].append({
                        "node": nodo,
                        "offset": "0"
                    })
                result.append(newRestriction)
        # ///////////////////////////////////
        for k, v in restriccionXTarget.items():
            if (len(v) >= 2):
                newRestriction = {
                    "type": "alignment",
                    "axis": "x",
                    "offsets": []
                }
                for nodo in v:
                    newRestriction["offsets"].append({
                        "node": nodo,
                        "offset": "0"
                    })
                result.append(newRestriction)
        return result
    # ------------------------------------------------------------------------------------

    def getNodes(self):
        nodosDict = []
        result = []
        for seq in self.leafNodes:
            if (len(seq.seq)) >= 1:
                for nodo in seq.graphNodes:
                    if nodo['name'] not in nodosDict:
                        result.append(nodo)
                        nodosDict.append(nodo['name'])
                    else:
                        continue
        return result
    # ------------------------------------------------------------------------------------

    def plotTree(self):
        DotExporter(self.nodoRaiz).to_picture("ArbolSententree.png")