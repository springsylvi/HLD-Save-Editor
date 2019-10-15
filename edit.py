import sys, base64, os.path, json

# names of numeric fields
num_fields = ["drifterkey","compShell","sword","cape","specialUp","healthUp",
    "halluc","eq00","eq01","checkRoom","checkX","checkY","checkHP","checkBat",
    "checkAmmo","checkStash","checkCID","playT","dateTime","noviceMode",
    "charDeaths","hasMap","gear","gunReminderTimes","gearReminderTimes",
    "successfulHealTimes","successfulWarpTimes","successfulCollectTimes",
    "CH","badass","tutHeal","fireplaceSave","newcomerHoardeMessageShown"]

class SaveMetadata:
    def __init__(self, header, path, savefile):
        self.header = header
        self.path = path
        self.savefile = savefile

    def get_name(self, save_num):
        return os.path.join(self.path,
            "HyperLight_RecordOfTheDrifter_"+str(save_num)+".sav")

class Field:
    def __init__(self, value):
        self.value = value

    def __str__(self):
        if isinstance(self.value, str):
            return "'"+self.value+"'"
        else:
            return str(self.value)

    __repr__ = __str__

    def append(self, value):
        if isinstance(self.value, str):
            self.value += value
        else:
            print("Can't append to numeric value")
        return

# converts savedata from text format to a dictionary.
def parse_savedata(savedata_text):
    savedata_map = json.loads(savedata_text)
    for name, value in savedata_map.items():
        savedata_map[name] = Field(value)
    return savedata_map

# prints the value of a field
def savedata_print(savedata_map, args):
    if (len(args) != 2):
        print("Usage: print [field_name]\n       print all")
        return
    if (args[1] == "all"):
        for name,field in savedata_map.items():
            print(name, ": ", field, sep="")
            
    else:
        field = savedata_map.get(args[1])
        if (field != None):
            print(field)
        else:
            print("Save does not contain field '{}'".format(args[1]))
    return

# appends a string to the value of a field
def savedata_append(savedata_map, args):
    if (len(args) != 3):
        print("Usage: append [field_name] [string]")
        return
    field = savedata_map.get(args[1])
    if (field != None):
        field.append(args[2])
    else:
        print("Save does not contain field '{}'".format(args[1]))
    return

# sets the value of a field
def savedata_set(savedata_map, args):
    if (len(args) == 3):
        savedata_map[args[1]] = Field(args[2])
    elif (len(args) == 4 and args[1] == "num"):
        savedata_map[args[2]] = Field(float(args[3]))
    else:
        print("Usage: set [field_name] [value]\n       set num [field_name] [value]")
        return
    return

# saves the edited data to a savefile
def savedata_write(savedata_map, metadata, save_num, args):
    if (len(args) != 2):
        print("Usage: save [save_num]")
        return
    if (args[1] not in ["0","1","2","3"]):
        confirm = input("save_num does not correspond to a valid savefile. \
        Save anyway? (y/n) ")
        if (confirm != "y"):
            return

    savedata_text = "" # implement conversion from savedata_map

    print("about to save file")
    return

    savedata_full = metadata.header + savedata_text.encode()
    if (save_num == args[1]):
        # saving changes to file
        os.truncate(metadata.get_name(save_num), 0)
        metadata.savefile.write(base64.standard_b64encode(savedata_full))
    else:
        # copying to new file
        savefile_write = open(metadata.get_name(args[1]),
            "wb", buffering=0)
        savefile_write.write(base64.standard_b64encode(savedata_full))
        savefile_write.close()
    return

if len(sys.argv) == 1:
    print("Not implemented argc=1 yet")
    save_num = None # read this value from config.ini
    sys.exit()
elif len(sys.argv) == 2:
    save_num = sys.argv[1]
else:
    print("Usage: python3 edit.py [save_num]")
    sys.exit()

# read config.ini
savefile_path = "/Users/NOT_CONNOR/Library/Application Support/com.HeartMachine.HyperLightDrifter"

metadata = SaveMetadata(None, savefile_path, None)

try:
    savefile = open(metadata.get_name(save_num), "r+b", buffering=0)
    metadata.savefile = savefile
except:
    print("Error opening save", save_num)
    sys.exit()


# load save data
savedata_full = base64.standard_b64decode(savefile.read())
savedata_header = savedata_full[:60]
metadata.header = savedata_header
savedata_text = savedata_full[60:].decode()[:-1]

# edit save data
savedata_map = parse_savedata(savedata_text)
while True:
    command_string = input(">>> ") 
    command = command_string.split(" ")
    if (command[0] == "print"):
        savedata_print(savedata_map, command)
    elif (command[0] == "append"):
        savedata_append(savedata_map, command)
    elif (command[0] == "set"):
        savedata_set(savedata_map, command)
    elif (command[0] == "save"):
        savedata_write(savedata_map, metadata, save_num, command)
    elif (command[0] == "exit"):
        savefile.close()
        sys.exit()
    else:
        print("Invalid command")
