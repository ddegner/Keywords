from tkinter import *
from tkinter import ttk
from tkinter.ttk import *
import boto3
from boto3.session import Session
from pathlib import Path
from configparser import ConfigParser
from clarifai.rest import ClarifaiApp

# Import and parse Configuration file
config = ConfigParser()
configFile = "config.ini"
configPath = Path(configFile)

global aws_access_key_id
global aws_secret_access_key
global bucket_name
global region_name
global clarifai_api_key


def SetConfig():
    global aws_access_key_id
    global aws_secret_access_key
    global bucket_name
    global region_name
    global clarifai_api_key

    config.read(configFile)

    aws_access_key_id = config.get('Amazon', 'aws_access_key_id')
    aws_secret_access_key = config.get('Amazon', 'aws_secret_access_key')
    bucket_name = config.get('Amazon', 'bucket_name')
    region_name = config.get('Amazon', 'region_name')

    clarifai_api_key = config.get('Clarifai', 'clarifai_api_key')

    return


def Connect():
    global aws_access_key_id
    global aws_secret_access_key
    global bucket_name
    global region_name
    global clarifai_api_key
    global your_bucket
    global ClarifaiConnection

    ClarifaiConnection = ClarifaiApp(api_key=clarifai_api_key)
    s3 = boto3.resource('s3', aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key,
                        region_name=region_name)
    your_bucket = s3.Bucket(bucket_name)

    return


# Copy to Clipboard
def CopyNext(temp):
    print(temp)
    root.clipboard_clear()
    keywordsList = [keywords.get(i) for i in keywords.curselection()]
    print(keywordsList)
    keywordsString = ', '.join(keywordsList)
    print(keywordsString.lower())
    root.clipboard_append(keywordsString.lower())

    images.current(images.current() + 1)
    GetKeywords("")

    return


# Get Images in S3
def GetImages():
    global ImagesList

    ImagesList = []

    # Populate Combobox
    for s3_file in your_bucket.objects.all():
        ImagesList.append([str(s3_file.key)])

    images['values'] = ImagesList
    images.current(0)

    return


def sub_dict(somedict, somekeys, default=None):
    return dict([(k, somedict.get(k, default)) for k in somekeys])


# Get Amazon Keywords for Image
def GetKeywords(EventTrigger):
    global ClarifaiConnection
    global clarifai_api_key

    keywords.delete(0, 'end')
    fileName = images.get()
    keywordList = {}
    # Amazon
    client = boto3.client('rekognition', aws_access_key_id=aws_access_key_id,
                          aws_secret_access_key=aws_secret_access_key, region_name=region_name)
    response = client.detect_labels(Image={'S3Object': {'Bucket': bucket_name, 'Name': fileName}}, MinConfidence=10)
    for Label in response["Labels"]:
        if Label["Confidence"] > 60 :
            keywordList[Label["Name"].lower()] = Label["Confidence"]
            print("amazon:" + Label["Name"] + " " + str(Label["Confidence"]))

    s3url = boto3.client('s3', aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key,
                         region_name=region_name)
    url = s3url.generate_presigned_url(ClientMethod='get_object', Params={'Bucket': bucket_name, 'Key': fileName},
                                       ExpiresIn=20000)

    # Clarifai
    model = ClarifaiConnection.models.get("general-v1.3")
    # print("https://s3.amazonaws.com/" + bucket_name + "/" + fileName)
    response = model.predict_by_url(str(url))
    for concept in response['outputs'][0]['data']['concepts']:
        keywordList[concept['name']] = (concept['value'] * 100)
        print("Clarifai: " + concept['name'] + " " +  str(concept['value'] * 100))

    for Label in keywordList.keys():
        keywords.insert(END, Label)

    return


def ClearS3():
    your_bucket.objects.all().delete()
    images['values'] = ""
    images.set("")
    keywords.delete(0, 'end')
    return


def createBucket():
    global aws_access_key_id
    global aws_secret_access_key
    global bucket_name
    global region_name
    global clarifai_api_key
    global your_bucket

    s3 = boto3.resource('s3', aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key,
                        region_name=region_name)
    s3.create_bucket(Bucket=EntryawsBucket.get())
    your_bucket = s3.Bucket(EntryawsBucket.get())
    your_bucket.Acl().put(ACL='public-read')

    return


def Settings():
    global EntryawsKeyID
    global EntryawsSecret
    global EntryawsBucket
    global EntryClarifai
    global region_name

    global SettingsWin

    config.read(configFile)

    aws_access_key_id = config.get('Amazon', 'aws_access_key_id')
    aws_secret_access_key = config.get('Amazon', 'aws_secret_access_key')
    bucket_name = config.get('Amazon', 'bucket_name')
    region_name = config.get('Amazon', 'region_name')

    clarifai_api_key = config.get('Clarifai', 'clarifai_api_key')

    SettingsWin = Tk()
    SettingsWin.title("Settings")
    SettingsWin.configure(background="#ececec", padx=15, pady=15)
    SettingsWin.attributes("-topmost", True)

    Label(SettingsWin, text="AWS Access Key ID").grid(row=0, column=0, sticky='e')
    EntryawsKeyID = Entry(SettingsWin)
    EntryawsKeyID.insert(0, aws_access_key_id)
    EntryawsKeyID.grid(row=0, column=1)

    LabelawsSecret = Label(SettingsWin, text="AWS Secret Access Key").grid(row=1, column=0, sticky='e')
    EntryawsSecret = Entry(SettingsWin)
    EntryawsSecret.insert(0, aws_secret_access_key)
    EntryawsSecret.grid(row=1, column=1)

    LabelawsBucket = Label(SettingsWin, text="AWS Bucket").grid(row=2, column=0, sticky='e')
    EntryawsBucket = Entry(SettingsWin)
    EntryawsBucket.insert(0, bucket_name)
    EntryawsBucket.grid(row=2, column=1)
    ButBucket = Button(SettingsWin, command=createBucket)
    ButBucket.config(text="Create")
    ButBucket.grid(row=2, column=2)

    LabelClarifai = Label(SettingsWin, text="Clarifai Secret Key").grid(row=3, column=0, sticky='e', pady=(15, 0))
    EntryClarifai = Entry(SettingsWin)
    EntryClarifai.insert(0, clarifai_api_key)
    EntryClarifai.grid(row=3, column=1, pady=(15, 0))

    ButCancel = Button(SettingsWin, command=SettingsWin.destroy)
    ButSave = Button(SettingsWin, command=writeConfig)
    ButCancel.config(text="Cancel")
    ButCancel.grid(row=4, column=1, sticky='e', pady=(15, 0))
    ButSave.config(text="Save")
    ButSave.grid(row=4, column=2, sticky='w', pady=(15, 0))

    SettingsWin.mainloop()
    return


def Refresh():
    Connect()
    GetImages()
    GetKeywords("")
    keywords.focus_set()
    return


def writeConfig():
    cfgfile = open(configFile, 'w')
    print("Open Config")

    # add the settings to the structure of the file, and lets write it out...
    config.set('Amazon', 'aws_access_key_id', str(EntryawsKeyID.get()))
    config.set('Amazon', 'aws_secret_access_key', str(EntryawsSecret.get()))
    config.set('Amazon', 'region_name',
               'us-east-1')  # *********************** Temproarily Hardcoded  ***********************
    config.set('Amazon', 'bucket_name', str(EntryawsBucket.get()))

    config.set('Clarifai', 'clarifai_api_key', str(EntryClarifai.get()))

    config.write(cfgfile)
    cfgfile.close()

    config.read(configFile)
    SetConfig()

    global SettingsWin

    SettingsWin.destroy()

    return


# Root Window ------------------------------------------------
root = Tk()
root.title("Keywords")
root.geometry("400x600")
root.configure(background="#cdc9c9")

# create keywords Listbox
keywords = Listbox(root, bd=0, bg="#cdc9c9", selectmode='multiple')

# create images Combobox
images = ttk.Combobox(root, state="readonly")
SelectedImage = images.current()
images.bind("<<ComboboxSelected>>", GetKeywords)

# create toolbar
toolbar = Frame(root)

ButSettings = Button(toolbar, text="Settings", command=Settings)
#PhoSettings = PhotoImage(file="img/settings.gif")
# PhoSettings = PhoSettings.subsample(2)
#ButSettings.config(image=PhoSettings)

ButRefresh = Button(toolbar, text="Refresh Images", command=Refresh)
#PhoRefresh = PhotoImage(file="img/refresh.gif")
# PhoRefresh = PhoRefresh.subsample(2)
#ButRefresh.config(image=PhoRefresh)

ButClearS3 = Button(toolbar,  text="Delete All", command=ClearS3)
#PhoClearS3 = PhotoImage(file="img/delete.gif")
# PhoClearS3 = PhoClearS3.subsample(2)
#ButClearS3.config(image=PhoClearS3)

ButSettings.pack(side=LEFT)
ButRefresh.pack(side=LEFT)
ButClearS3.pack(side=LEFT)

# ****** Packing starts here ******

toolbar.pack(side=TOP, fill=X, expand=0)
images.pack(side=TOP, fill=X, expand=0)
keywords.pack(side=BOTTOM, fill=BOTH, expand=1, padx=7, pady=7)

root.bind('<Command-c>', CopyNext)

if configPath.is_file() == False:
    cfgfile = open(configFile, 'w')
    print("Write Config")
    config.add_section('Amazon')
    config.add_section('Clarifai')
    config.set('Amazon', 'aws_access_key_id', '')
    config.set('Amazon', 'aws_secret_access_key', '')
    config.set('Amazon', 'region_name',
               'us-east-1')  # *********************** Temproarily Hardcoded  ***********************
    config.set('Amazon', 'bucket_name',
               'must be lowercase')  # *********************** Temproarily Hardcoded  ***********************
    config.set('Clarifai', 'clarifai_api_key', '')
    config.write(cfgfile)
    cfgfile.close()
    Settings()

else:
    SetConfig()

root.mainloop()
