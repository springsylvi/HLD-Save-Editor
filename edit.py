import sys, base64, os.path, json, re, configparser, platform, getpass

help_all = (
    "load       load data from a save file\n"
    "save       save data to a save file\n"
    "files      list existing save files\n"
    "set        assign a new value to a field\n"
    "append     append a string onto a string-valued field\n"
    "help       display help for a command\n"
    "print      print the value of a field\n"
    "transfer   transfer save data from one computer to another\n"
    "exit       exit the program")

help_text = {
    "all": help_all,
    "load": (
        "Usage: load [save_num]\n\n"
        "Load data from a save file. Equivalent to starting the program with parameter save_num."),
    "save": (
        "Usage: save [save_num]\n\n"
        "Save the current values to a save file."),
    "files": (
        "Usage: files\n\n"
        "List the save_num of each available save file."),
    "set": (
        "Usage: set [field_name] [value]\n       set num [field_name] [value]\n       set empty [field_name]\n"
        "Set field_name to value. In the first form, value is treated as a string. In the second, it is treated as a number. In the third, value is set to the empty string."),
    "append": (
        "Usage: append [field_name] [string]\n\n"
        "Append a string onto the end of field_name's current value. Fails if the value is not a string."),
    "help": (
        "Usage: help\n       help [command]\n\n"
        "Display help for a command, or general help for all commands if none is specified."),
    "print": (
        "Usage: print [field_name]\n       print all\n\n"
        "In the first form, print the value of field_name. In the second, print every name/value pair."),
    "transfer": (
        "Usage: transfer [src_save_num] [dst_save_num]\n       transfer all [src_save_num]\n\n"
        "Saves the current values to dst_save_num, but with the machine-specific header from src_save_num. In the second form, applies the header from src_save_num to all files."),
    "exit": (
        "Usage: exit\n\n"
        "Exit the program.")}

class InvalidArgsError(Exception):
    pass
        
class FileError(Exception):
    pass

# todo: rework this class as a virtual savefile object, no static methods
# and include savedata in the object. add a reload() method to reload data
# from the file
class SaveMetadata:
    def __init__(self, header, path):
        self.header = header
        self.path = path
        self.linux = (platform.system() == "Linux")

    def set_save(self, save_num):
        self.save_num = save_num
        if self.linux:
            self.name = os.path.join(self.path,
            "hyperlight_recordofthedrifter_"+str(save_num)+".sav")
        else:
            self.name = os.path.join(self.path,
            "HyperLight_RecordOfTheDrifter_"+str(save_num)+".sav")
            
    def get_name(self, save_num=None):
        if (save_num is None):
            return self.name
        if self.linux:
            return os.path.join(self.path,
                "hyperlight_recordofthedrifter_"+str(save_num)+".sav")
        else:
            return os.path.join(self.path,
                "HyperLight_RecordOfTheDrifter_"+str(save_num)+".sav")

    def get_save_num(self, name=None):
        if (name is None):
            return self.save_num

        if self.linux:
            match = re.match("\A(hyperlight_recordofthedrifter_)([^_].*)(\.sav)\Z", name, 0)
        else:
            match = re.match("\A(HyperLight_RecordOfTheDrifter_)([^_].*)(\.sav)\Z", name, 0)

        if match:
            return match.group(2)
        else:
            return None

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

# lists all savefiles in the directory
def savedata_files(metadata, args):
    for filename in os.listdir(metadata.path):
        save_num = metadata.get_save_num(filename)
        if save_num is not None:
            print(save_num)

# prints the value of a field
def savedata_print(savedata_map, args):
    if (len(args) != 2):
        raise InvalidArgsError("Usage: print [field_name]\n       print all")
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
        if (args[1] == "empty"):
            savedata_map[args[2]] = Field("")
        else:
            savedata_map[args[1]] = Field(args[2])
    elif (len(args) == 4 and args[1] == "num"):
        try:
            savedata_map[args[2]] = Field(float(args[3]))
        except:
            print("Could not convert '{}' to a number".format(args[3]))
    else:
        raise InvalidArgsError("Usage: set [field_name] [value]\n       set num [field_name] [value]")
    return

# reads data from a savefile
def savedata_load(metadata, args):
    if (len(args) != 2):
        raise InvalidArgsError("Usage: load [save_num]")
    filename = metadata.get_name(args[1])
    if (not os.path.exists(filename)):
        raise FileError("File does not exist")

    metadata.set_save(args[1])
    savefile = open(filename, "rb", buffering=0)
    savedata_full = base64.standard_b64decode(savefile.read())
    metadata.header = savedata_full[:60]
    savedata_text = savedata_full[60:].decode()[:-1]
    savefile.close()
    return parse_savedata(savedata_text)

# saves the edited data to a savefile
def savedata_write(savedata_map, metadata, args):
    if (len(args) != 2):
        raise InvalidArgsError("Usage: save [save_num]")

    savedata_map_raw = {}
    for name, field in savedata_map.items():
        savedata_map_raw[name] = field.value
    savedata_text = json.dumps(savedata_map_raw) + " "

    savedata_full = metadata.header + savedata_text.encode()
    savefile_write = open(metadata.get_name(args[1]), "wb", buffering=0)
    try:
        savefile_write.write(base64.standard_b64encode(savedata_full))
    except:
        raise FileError("File cannot be written")
    savefile_write.close()
    return

# changes the header to match another savefile
def savedata_transfer(savedata_map, metadata, args):
    if (len(args) != 3):
        raise InvalidArgsError("Usage: transfer [src_save_num] [dst_save_num]\n       transfer all [src_save_num]")
    if (args[1] == "all"):
        src_filename = metadata.get_name(args[2])
        files = []
        for filename in os.listdir(metadata.path):
            save_num = metadata.get_save_num(filename)
            if (save_num is not None and save_num != args[2]):
                files.append(save_num)
    else:
        src_filename = metadata.get_name(args[1])
        files = [metadata.get_name(args[2])]
    if (not os.path.exists(src_filename)):
        raise InvalidArgsError("Source file does not exist")

    for dst_filename in files:
        src_savefile = open(src_filename, "rb", buffering=0)
        src_header = base64.standard_b64decode(src_savefile.read())[:60]
        src_metadata = SaveMetadata(src_header, metadata.path)
        savedata_write(savedata_map, src_metadata, ["save", dst_filename])
        src_savefile.close()
    return

# sets the drifter's coordinates to an entrance
def set_entrance(savedata_map, metadata, args):
    if (len(args) == 1):
        entrance = 0
    elif (len(args) == 2):
        try:
            entrance = int(args[1])
        except:
            raise InvalidArgsError("Usage: entrance\n       entrance [entrance_num]")
    else:
        raise InvalidArgsError("Usage: entrance\n       entrance [entrance_num]")

    entrances = open("entrances.csv")
    # read line number corresponding to checkRoom
    # get nth entry on that line for the nth entrance coords


# diplay help for a command, or generic help if none is specified
def display_help(args):
    if (len(args) == 1):
        help_id = "all"
    elif (len(args) == 2):
        help_id = args[1]
    else:
        raise InvalidArgsError("Usage: help\n       help [command]")

    if (help_id in help_text):
        print(help_text[help_id])
    else:
        raise InvalidArgsError("Invalid help topic")
    return

# get the default savefile path for the user's OS
def autofill_path(config):
    sysname = platform.system()
    username = getpass.getuser()
    if (sysname == "Windows"):
        path = "C:\\Users\\{}\\AppData\\Local\\HyperLightDrifter".format(username)
    elif (sysname == "Darwin"):
        path = "/Users/{}/Library/Application Support/com.HeartMachine.HyperLightDrifter".format(username)
    elif (sysname == "Linux"):
        path = "/home/{}/.config/HyperLightDrifter".format(username)
    else:
        raise Exception("Unknown OS")

    if os.path.exists(path):
        return path
    raise Exception("Default path does not exist")

if len(sys.argv) != 2:
    print("Usage: python3 edit.py [save_num]")
    sys.exit()

# read config.ini
config = configparser.ConfigParser()
try:
    config_ini = open("config.ini", "r")
except FileNotFoundError:
    config_ini = open("config.ini", "x+")
except:
    print("No config file found")
    sys.exit()

config.read_file(config_ini)
config_ini.close()
savefile_path = config.get("main", "path", fallback=None)
if (savefile_path is None):
    confirm = input("No savefile path specified. Attempt to auto-fill? (y/n) ")
    if (confirm != "y"):
        sys.exit()
    try:
        savefile_path = autofill_path(config)
        if not "main" in config:
            config.add_section("main")
        config["main"]["path"] = savefile_path
        with open("config.ini", "w+") as config_ini:
            config.write(config_ini)
        print("Set path to", savefile_path)
    except Exception as err:
        print("Failed to auto-fill path:", err)
        sys.exit()

metadata = SaveMetadata(None, savefile_path)
try:
    savedata_map = savedata_load(metadata, sys.argv)
except InvalidArgsError:
    print("Usage: python3 edit.py [save_num]")
    sys.exit()
except:
    print("Error opening save", sys.argv[1])
    sys.exit()

while True:
    command_string = input("{}$ ".format(metadata.get_save_num())) 
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
            savedata_map = savedata_load(metadata, command)
        elif (command[0] == "help"):
            display_help(command)
        elif (command[0] == "files"):
            savedata_files(metadata, command)
        elif (command[0] == "transfer"):
            savedata_transfer(savedata_map, metadata, command)
        else:
            print("Invalid command")
    except InvalidArgsError as err:
        print(err)
    except FileError as err:
        print(err)
