import re

file = open('D:\\lines5.txt')
lines = file.read().split(';')


#variables used
i = 0 
j=0 #index used throughout - name better next time
junkvar = 0 #junk variable - poor programming :( 
notfirstrecord = 0 #to track the first record and ensure that gets printed
indexStart = 0 #this is where the bill of items begin
indexEnd = 0 #this is where the bill of items end
#templist = []
startitemlist = ['EUR', 'eur', 'Eur', 'USD', 'Usd', 'usd', 'GBP', 'Gbp', 'gbp', '$', '£' ]
enditemlist = ['zu zahlen', 'Zu Zahlen', 'ZU ZAHLEN', 'total', 'Total', 'TOTAL']
recList = list() #this is the actual dictionary of items
itemListIndex = [] #indexes of all items are stored here
alphaTest = ''
containsLetters = False

recorddate = False
while (j<len(lines) and recorddate==False):
    txt = lines[j]
    xx = re.search("([0-2][0-9])\.([0-1][0-9])\.([2-3][0-9])", txt)
    if(str(xx) != "None"):
        recorddate = True
        purchasedate = xx.string
    j+=1

j = 0
recorddate = False
while (j<len(lines) and recorddate==False):
    txt = lines[j]
    substring1 = "Datum"
    if substring1 in txt: 
        print(txt[6:].replace(".", ""))
        print(lines[j+1][:5].replace(":",""))
        recorddate = True
    j+=1

j=0
recordtime = False
while (j<len(lines) and recordtime==False):
    txt = lines[j]
    xx = re.search("([0-2][0-9])\:([0-5][0-9])", txt)
    if(str(xx) != "None"):
        purchasetime = xx.string
        recordtime = True
    j+=1

j=0
storename = False
while (j<len(lines)):
    if(storename == False):
        txt = lines[j]
        xx = re.search("(([D][L]))", txt)
        if(str(xx) != "None"):
            storename = True
        j+=1
    else:
        purchaseStore = lines[j]
        j=len(lines)

mergedstrings = purchasedate+purchasetime
billdatetime = re.sub("[^\w]+",'',mergedstrings)


#recognizes the start and end of each bill - the keywords are in lists and are declared
#Logic - it looks for each item in the lists 'enditemlist' and 'startitemlist' in the indexed element of the 'lines' list
while(i<len(lines)):
	if (enditemlist.count(lines[i])>0):
		indexEnd = i
	elif(startitemlist.count(lines[i])>0):
		indexStart = i
	i += 1

j=indexStart+1


#This builds an index of items starting with letters, i.e. 'Itemnames' -> THis will be used to map which elements are item names later
while (j<indexEnd):
	if ' x ' in lines[j]:
		junkvar = 0
	elif lines[j].startswith(('0','1','2','3','4','5','6','7','8','9','-')) == True:
		junkvar = 0 
	else:
		itemListIndex.append(j)
	j += 1

#print(itemListIndex)
j=indexStart+1
isNotItemName = False
record = {}

while (j<indexEnd):
    if j in itemListIndex: 
        if notfirstrecord>0: #Since first item is always an Itemname, it skipped this, hence this function
            recList.append(record.copy())
            record['Itemname'] = lines[j]
            record['Price'] = ''
            record['QuantityUnit'] = ''
        notfirstrecord += 1
        record['Itemname'] = lines[j]
        record['Price'] = ''
        record['QuantityUnit'] = ''
        isNotItemName = False
    else: 
        if isNotItemName == False: 
            #write to Price 
            templist = lines[j].split()
            alphaTest= templist[0].lower()
            newalphaTest = "".join(i for i in alphaTest if i in "0123456789,")
            record['Price'] = float(newalphaTest.replace(',','.'))
            isNotItemName = True #set flag as true - next iteration checks for True/False, if it doesn't belong to the itemListIndex

        elif isNotItemName == True:
            record['QuantityUnit']=lines[j]
            #write to QuantityUnit 
            isNotItemName = False
            
    j += 1
recList.append(record.copy())
print(*recList)

print('\n'+purchasedate+'\n'+purchasetime+'\n'+purchaseStore+'\n'+billdatetime)
