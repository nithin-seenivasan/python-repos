import json
import boto3
import os
import urllib.parse
from decimal import Decimal

print('loading OCR function')

#initializing Boto with the AWS services
s3 = boto3.client('s3')
client = boto3.client('textract')
dynamodb = boto3.resource('dynamodb')

def getTextractData(bucketName, documentKey):
    print('Loading getTextractData')
    # Call Amazon Textract, process using S3 object
    response = client.detect_document_text(
    Document={'S3Object': {'Bucket': bucketName, 'Name': documentKey}})
    detectedText = ''
    for item in response['Blocks']:
        if item['BlockType'] == 'LINE':
            detectedText += item['Text'] + ';' 
    return detectedText

#Write OCR output to S3 file
def writeTextractToS3File(textractData, createdS3Document):
    generateFilePath = os.path.splitext(createdS3Document)[0] + '.txt' #generate FilePath with the original file's path
    s3.put_object(Body=textractData, Bucket="results-ocr-backend", Key=generateFilePath) #generate the Text File


##string logic
def parseString(textInput):
    lines = textInput.split(';')

    #initialize variables
    i = 0 
    j=0 #index used throughout - name better next time
    junkvar = 0 #junk variable 
    notfirstrecord = 0 #to track the first record and ensure that gets printed
    indexStart = 0 #this is where the bill of items begin
    indexEnd = 0 #this is where the bill of items end
    startitemlist = ['EUR', 'eur', 'Eur', 'USD', 'Usd', 'usd', 'GBP', 'Gbp', 'gbp', '$', '£' ]
    enditemlist = ['zu zahlen', 'Zu Zahlen', 'ZU ZAHLEN', 'total', 'Total', 'TOTAL']
    recList = list() #this is the actual dictionary of items
    itemListIndex = [] #indexes of all items are stored here
    alphaTest = ''
    #containsLetters = False
    


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

    j=indexStart+1
    isNotItemName = False
    record = {}

    #Sorts the list data into 3 categories 
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
                templist = lines[j].split()
                alphaTest= templist[0].lower()
                newalphaTest = "".join(i for i in alphaTest if i in "0123456789,-")
                record['Price'] = Decimal(newalphaTest.replace(',','.')) #write to Price
                isNotItemName = True #set flag as true - next iteration checks for True/False, if it doesn't belong to the itemListIndex
    
            elif isNotItemName == True:
                record['QuantityUnit']=lines[j] #write to QuantityUnit
                isNotItemName = False                
        j += 1
    recList.append(record.copy())
    insert_data(recList)

# insert_data function for inserting data into dynamodb table
def insert_data(recordsList):
    table = dynamodb.Table('userdata-dev')
    print('initialized the dev - table ')
    for m in range(len(recordsList)):
        record = recordsList[m]
        table.put_item(
            Item={
                'uid': str(m),
                'Itemname': record['Itemname'],
                'Price': record['Price'],
                'QuantityUnit': record['QuantityUnit']
            }
        )
    print('Writing to DB Successful')

#Lambda Handler - this is what runs first when the Lambda is executed
def lambda_handler(event, context):

    bucket = event['Records'][0]['s3']['bucket']['name']
    key = urllib.parse.unquote_plus(event['Records'][0]['s3']['object']['key'], encoding='utf-8')

    try:
        detectedText = getTextractData(bucket, key)
        a = parseString(detectedText)

    except Exception as e:
        print(e)
        print('Error getting object {} from bucket {}. Make sure they exist and your bucket is in the same region as this function.'.format(key, bucket))
        raise e