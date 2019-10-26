import sys, base64, os.path, json, configparser

help_text = (
    "load       load data from a save file\n"
    "save       save data to a save file\n"
    "set        assign a new value to a field\n"
    "append     append a string onto a string-valued field\n"
    "help       display this message\n"
    "print      print the value of a field\n"
    "exit       exit the program")

class InvalidArgsError(Exception):
    def __init__(self, message):
        self.message = message

    def print(self):
        print(self.message)

class SaveMetadata:
    def __init__(self, header, path):
        self.header = header
        self.path = path

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
        raise InvalidArgsError("Usage: print [field_name]\n       print all") # test indentation
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
        raise InvalidArgsError("Usage: append [field_name] [string]")
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
        try:
            savedata_map[args[2]] = Field(float(args[3]))
        except:
            print("Could not convert '{}' to a number".format(args[3]))
    else:
        raise InvalidArgsError("Usage: set [field_name] [value]\n       set num [field_name] [value]") # test indentation
    return

# reads data from a savefile
def savedata_load(metadata, args):
    if (len(args) != 2):
        raise InvalidArgsError("Usage: load [save_num]")
    else:
        savefile = open(metadata.get_name(save_num), "rb", buffering=0)
        savedata_full = base64.standard_b64decode(savefile.read())
        metadata.header = savedata_full[:60]
        savedata_text = savedata_full[60:].decode()[:-1]
        savefile.close()
        return parse_savedata(savedata_text)

# saves the edited data to a savefile
def savedata_write(savedata_map, metadata, args):
    if (len(args) != 2):
        raise InvalidArgsError("Usage: save [save_num]")
    if (args[1] not in ["0","1","2","3"]):
        confirm = input("save_num does not correspond to a valid savefile.\n"
        "Save anyway? (y/n) ")
        if (confirm != "y"):
            return

    savedata_map_raw = {}
    for name, field in savedata_map.items():
        savedata_map_raw[name] = field.value
    savedata_text = json.dumps(savedata_map_raw) + " "

    savedata_full = metadata.header + savedata_text.encode()
    savefile_write = open(metadata.get_name(args[1]), "wb", buffering=0)
    savefile_write.write(base64.standard_b64encode(savedata_full))
    savefile_write.close()
    return

# replace this block with a separate function once more args are added, handle InvalidArgsError
if len(sys.argv) == 1:
    save_num = None
elif len(sys.argv) == 2:
    save_num = sys.argv[1]
    if (save_num not in ["0","1","2","3"]):
        confirm = input("save_num does not correspond to a valid savefile.\n"
        "Read anyway? (y/n) ")
        if (confirm != "y"):
            sys.exit()
else:
    print("Usage: python3 edit.py [save_num]")
    sys.exit()

# read config.ini
config = configparser.ConfigParser()
try:
    config_ini = open("config.ini", "r")
except:
    print("No config file found")
    sys.exit()

config.read_file(config_ini)
savefile_path = config.get("main", "path")
if (save_num is None):
    try:
        save_num = config.get("main", "save_num")
    except:
        print("No save number specified")
        sys.exit()


if (savefile_path is None):
    print("No savefile path specified")
    sys.exit()    

metadata = SaveMetadata(None, savefile_path)
try:
    savedata_map = savedata_load(metadata, sys.argv)
except InvalidArgsError:
    print("Usage: python3 edit.py [save_num]")
    sys.exit()
except:
    print("Error opening save", save_num)
    sys.exit()

while True:
    command_string = input(">>> ") 
    command = command_string.split(" ")
    try:
        if (command[0] == "print"):
            savedata_print(savedata_map, command)
        elif (command[0] == "append"):
            savedata_append(savedata_map, command)
        elif (command[0] == "set"):
            savedata_set(savedata_map, command)
        elif (command[0] == "save"):
            savedata_write(savedata_map, metadata, command)
        elif (command[0] == "exit"):
            sys.exit()
        elif (command[0] == "load"):
            savedata_map = savedata_load(metadata, args)
        elif (command[0] == "help"):
            print(help_text)
        else:
            print("Invalid command")
    except InvalidArgsError as err:
        err.print()
