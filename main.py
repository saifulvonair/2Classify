#Copyright (c) 2017, Saiful Alam with Email: saiful_vonair@yahoo.com. All rights reserved.

#Redistribution and use in source and binary forms, with or without
#modification, are permitted provided that the following conditions
#are met:
# * Redistributions of source code must retain the above copyright
#   notice, this list of conditions and the following disclaimer.
# * Redistributions in binary form must reproduce the above copyright
#   notice, this list of conditions and the following disclaimer in the
#   documentation and/or other materials provided with the distribution.
#   Free for any kind of personal use but not for production purpose

#THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS ``AS IS'' AND ANY
#EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
#IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
#PURPOSE ARE DISCLAIMED.  IN NO EVENT SHALL THE COPYRIGHT OWNER OR
#CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
#EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
#PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR
#PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY
#OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
#(INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
#OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

import csv
import re

class Category:
    def __init__(self, id):
        self.name = ''
        self.id = id
        self.weight = {}
        self.value = 0
        self.ignore_list = []
        return

    def removeIgnoreList(self):
        self.ignore_list = []

    def add(self, key, w):
        self.weight[key] = w

    def get(self, key):
        if(self.weight[key] == None):
            return 0
        return self.weight[key]

    def addIgnoreList(self, list_item):
        for item in list_item:
            # Compare only key
            if(item.id == 0 ):
                self.ignore_list.append(item.word)
            # For specific category...
            else:
                if(item.id == self.id):
                    self.ignore_list.append(item.word)

    def loadData(self, key, value):
        # Added some Ignore list for category ...Even they are in the File.
        if (key not in self.ignore_list):  # Added some Ignore list for category ...Even they are in the File.
            self.weight[key] = int(value)
        else:
            print "Key ignore from list: ", key

    def update(self, key):
        if (key not in self.ignore_list):  # Added some Ignore list for category ...Even they are in the File.
            oldW = self.weight.get(key)
            if (oldW == None):
                oldW = 0;
            self.weight[key] = oldW + 1
        else:
            print "Key ignore from list: ", key
        #self.weight[key] = 1

    def keepMaxItems(self, key):
        list = []
        for key in self.weight:
            if(self.weight[key] < 1):
                list.append(key)
        for i in list:
            del self.weight[i]


    def calculateWight(self,parent, list, useMax, weight = 1):
        # This is very very important things for predictios.
        # Slitly change this will cause huge impact on predictios
        # We have to solve this by trial adn Error, so if we get 50-50 then need to
        # check this again.
        for item in list:
            keyValue = self.weight.get(item)
            if(keyValue == None):
                keyValue = 0;
            if(keyValue > 0):
                if(useMax == 1):
                    keyValue = 1 + keyValue * weight
                else:
                    keyValue = 1
            weight += keyValue

        self.value = weight
        return weight

class IgnoreWords:
    def __init__(self, id, word):
        self.id = id
        self.word = word

class CategoryManager:
    def __init__(self):
        self.listItems = {}
        self.category = ['ONE', 'TWO', 'X']
        self.ignore_words = []
        self.word_length = 2
        return
    def removeAll(self):
        self.listItems = {}

    def writeWeight(self):
        MIN_WEIGHT = 1
        ofile = open('train.csv', "wb")
        # csv file writer
        writer = csv.writer(ofile, delimiter=',', quoting=csv.QUOTE_NONNUMERIC)
        row = []
        writer_max = csv.writer(open('train-max.csv', 'wb'), delimiter=',', quoting=csv.QUOTE_NONNUMERIC)
        row = []

        for key in self.listItems:
            obj =  self.listItems[key]
            for key in obj.weight:
                if(obj.weight[key] >= MIN_WEIGHT):
                    row.append(obj.id)
                    row.append(key)
                    row.append(obj.weight[key])
                    #row.append(1)#FIXME
                    print row;
                    # write expected result in to csv file
                    writer.writerow(row)
                    if(int(obj.weight[key]) > 1000):
                        writer_max.writerow(row)
                    row = []
        ofile.close()

    def add(self, item):
        self.listItems.append(item)

    def get(self, id):
        obj = self.listItems.get(id)
        if(obj == None):
            obj = Category(id)
            self.listItems[id] = obj
        return obj

    def getItemById(self, id, list_item):
        for i in list_item:
            if(i.id == id):
                return i
        return None

    def classify(self, text, useMax, weight = 1):
        text = text.replace('.', ' ')
        txt_list = text.lower().split(' ')
        items = []
        #print txt_list
        for key in self.listItems:
            obj = self.listItems[key]
            obj.calculateWight(self, txt_list, useMax, weight)
            items.append(obj)
        # Equal name provides both
        if (items[1].value == items[0].value and items[0].value != 0):
            items[0].name = self.category[2]
            items[1].name = self.category[2]
        # First category
        ii = self.getItemById(1, items)
        if(ii.value == 0):
            ii.value = -10  # Not First Category
        # Sort items
        items = sorted(items, key=lambda obj: obj.value, reverse=True)
        # Back to origin Name
        if(items[0].value != items[1].value):
            items[0].name = self.category[items[0].id-1]
            items[1].name = self.category[items[1].id-1]

        return  items

    def initCatgory(self):
        self.ignore_words = []
        self.loadClasses()

        with open('ignore_category_words.csv', 'rU') as f:
            reader = csv.reader(f)
            c = 0;
            for row in reader:
                w = IgnoreWords(int(row[0]), row[1])
                self.ignore_words.append(w)
            f.close()
        # Create 2 category
        self.get(1)
        self.get(2)
        for key in self.listItems:
            obj = self.listItems[key]
            obj.removeIgnoreList()
            obj.addIgnoreList(self.ignore_words)

    def processTrainData(self,row):

        try:
            category = self.get(int(row[0]))
            if category <= 0:
                print 'Invalid Row'
                return
        except:
            print 'Invalid Row'
            return
        category = self.get(int(row[0]))
        # Title
        text = row[1].strip().replace('"', '').decode('utf-8', 'ignore')
        if(len(row) > 2):
            # Description..
            text = text + row[2].strip().replace('"', '').decode('utf-8', 'ignore')
        text = text.replace('.', ' ').lower()
        text = text.replace('-', ' ')
        text = re.sub(r'[^a-zA-Z0-9 ]', r'', text)
        #text = re.sub(r'[^a-zA-Z ]', r'', text) #Only Alphabet.. BAD Result..

        if(len(text) <=0 ):
            return
        print text
        txt_list = text.lower().split(' ')
        for txt in txt_list:
            if(len(txt) > self.word_length):
              category.update(txt)

    def processModelData(self,row):
        category = self.get(int(row[0]))
        category.name = self.category[category.id-1]
        text = row[1].strip()
        category.loadData(text, row[2])

    def trainSystem(self, trainData):
        self.initCatgory();
        with open(trainData, 'rU') as f:
        #with open('train_dp36.csv', 'rU') as f:
            reader = csv.reader(f)
            c = 0;
            for row in reader:
                # ct = cm.get(int(row[0]))
                # ct.add(row[1], int(row[2]))
                self.processTrainData(row)
                c = c + 1;
                print "Process Row: ", str(c)
                # if(c == reader.)
                # print ct
            self.writeWeight()
            f.close()
            #self.keepMaxWinner()

    def loadPretrainModel(self):
        # Load old Model
        self.loadModel()
        with open('dbpedia_train.csv', 'rU') as f:
            reader = csv.reader(f)
            c = 0;
            for row in reader:
                # ct = cm.get(int(row[0]))
                # ct.add(row[1], int(row[2]))
                self.processTrainData(row)
                c = c + 1;
                print "Process Row: %s", str(c)
                # if(c == reader.)
                # print ct
            self.writeWeight()
            f.close()

    def loadClasses(self):
        self.category = []
        with open('classes.csv', 'rU') as f:
            reader = csv.reader(f)
            for row in reader:
                self.category.append(row[0])
                print "Loading class: ", row[0]

    def loadModel(self, modelFile):
        self.removeAll()
        self.initCatgory();
        with open(modelFile, 'rU') as f:
            reader = csv.reader(f)
            c = 0;
            for row in reader:
                # ct = cm.get(int(row[0]))
                # ct.add(row[1], int(row[2]))
                self.processModelData(row)
                c = c + 1;
                print "Loaind Row: ", str(c)

    def classifyText(self, text):
        list_res = self.classify(text, 0, 0)
        # FIXME
        if (list_res[1].value == list_res[0].value):
            list_res = self.classify(text, 1, 2)
        if (list_res[1].value == list_res[0].value):
            list_res = self.classify(text, 1, 3)

        return list_res

    def classifyMany(self, csvFile, col, UrlCol, outFile):

        with open(outFile, 'wb') as csv_file:
            print 'Delete old File'
        with open(csvFile, 'rU') as f:
            reader = csv.reader(f)
            c = 1;
            count = 0;
            equal = 0;
            for row in reader:
                # ct = cm.get(int(row[0]))
                # ct.add(row[1], int(row[2]))
                text = row[col].strip()
                list_res = self.classifyText(text)
                id = row[0].strip()
                row = []
                row.append(id)
                row.append(list_res[0].value)
                row.append(list_res[1].value)
                row.append(list_res[0].name)
                row.append(list_res[1].name)

                with open(outFile, 'ab') as csv_file:
                    csv_writer = csv.writer(csv_file, delimiter=',', quoting=csv.QUOTE_NONNUMERIC)
                    csv_writer.writerow(row)
                c = c + 1;

def main():
    cm = CategoryManager()
    cm.trainSystem('train_dp36.csv')
    #cm.loadPretrainModel();
    #cm.loadModel('train.csv')
    cm.classifyText('He lived and worked primarily in Washington D.C. and the Washington Post described her as a force in the Washington Color School')
    cm.classifyMany('test_dp3.csv', 2, 0, 'test_dp3_r.csv')
    cm.classifyMany('test_dp6.csv', 2, 0, 'test_dp6_r.csv')

if __name__ == "__main__":
    main()