class Document:
   __instance = None
   DocumentList = {}

   @staticmethod 
   def getInstance():
      if Document.__instance == None:
         Document()
      return Document.__instance

   def __init__(self):
      if Document.__instance != None:
         raise Exception("Documentクラス")
      else:
         Document.__instance = self

   def setValue(self, key, value):
        self.DocumentList[key] = value;

   def getValue(self, key):
      if key in self.DocumentList:
        return self.DocumentList[key]
      else:
         return ""
