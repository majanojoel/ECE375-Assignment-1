import subprocess, os.path, json
from pathlib import Path


#Colors
T_CLR_MSG = '\033[94m'
T_CLR_WARN = '\033[93m'
T_CLR_ERROR = '\033[91m'
T_CLR_SUCCESS = '\033[92m'
T_CLR_TERMINATOR = '\033[0m'

def printText(type, text):
    print(f"{type}{text}\n{T_CLR_TERMINATOR}")


#### HELPER FUNCTIONS #######

def generateArgs(plugin, args):
    argString = ""
    for arg in args:
        argString+=f" -fplugin-arg-{plugin}-{arg}"
    return argString

printText(T_CLR_MSG, "Welcome to v0.5 of this script!")

if not os.path.isdir("src"):
    printText(T_CLR_ERROR, "src folder not found exiting!")
    exit()
elif not os.path.isdir("build"):
    printText(T_CLR_ERROR, "build folder not found, please run meson setup build in root of project.")
    exit()

data = {}
# Opening JSON file
with open('script-config.json', 'r') as f:
    # returns JSON object as a dictionary
    data = json.load(f)
  
if data == {}:
    printText(T_CLR_ERROR, "Failed to load JSON file. Exiting!")
    exit()

pluginDict = data['clang-plugins']
staticChecksDict = {}
if "static-checks" in data:
    staticChecksDict = data['static-checks']


#generate file list
fileList = []
CPPfileList = list(Path("./src").rglob("*.[c][p][p]")) #CPP files
CfileList = list(Path("./src").rglob("*.[c]")) #C files

if(len(CPPfileList) == 0):
    fileList = list(CfileList)
else:
    fileList = list(CPPfileList)

#### LINKS ####

printText(T_CLR_MSG, "Downloading required plugins. Please wait.")
for plugin in pluginDict:
    if os.path.isfile(f"{plugin}.so"): continue
    output=subprocess.getoutput(f"curl -L0 https://github.com/majanojoel/ECE496_ClangPlugins/raw/main/libraries/{plugin}_stable.so -o {plugin}.so")
    # Check if plugin downloaded
    if not os.path.isfile(f"{plugin}.so"):
        printText(T_CLR_ERROR, f"Couldn't download {plugin}.so. Exiting!")
        exit()

printText(T_CLR_SUCCESS, "Plugins downloaded. Running checks next.")

testsPassed = True
######## Checks ##############
for file in fileList:
    for plugin, pluginArg in pluginDict.items():
        printText(T_CLR_MSG, f"Running {plugin} check on {str(file)}")
        argString = ''
        if pluginArg != '':
            argString = generateArgs(plugin, pluginArg)
        output=subprocess.getoutput(f"clang-15 -fplugin=./{plugin}.so{argString} -c {str(file)}")
        if(output != ""): 
            testsPassed = False
            printText(T_CLR_ERROR, output)
        else:
            printText(T_CLR_SUCCESS, f"{plugin} check passed!")


### Clang Tools checks ####

#"No bugs found."
if "scan-build" in staticChecksDict:
    printText(T_CLR_MSG, "Running scan-build on project")
    output=subprocess.getoutput(f"scan-build-15 meson compile -C build")
    if "No bugs found." in output:
        printText(T_CLR_SUCCESS, "scan-build found no bugs.")
    else:
        printText(T_CLR_ERROR, "Bugs found. scan-build output:")
        print(output)
        testsPassed = False

######## Compilation #########
extraCompileArgs = ""
if "address-sanitizer" in staticChecksDict:
    printText(T_CLR_MSG, "Address Sanitizer enabled. Reconfiguring build system.")
    print(subprocess.getoutput("meson setup --reconfigure -Db_sanitize=address -Db_lundef=false build"))
    printText(T_CLR_MSG, "meson reconfigured, memory address related issues in your program will now cause a crash.")
    

if(testsPassed):
    printText(T_CLR_SUCCESS, "All checks passed, compiling next!")
    output = subprocess.getoutput(f"meson compile -C build")
    printText(T_CLR_MSG, "Meson Output:")
    print(output + "\n")
    printText(T_CLR_SUCCESS, "Script complete! Please test your program or if meson failed, fix the problems and run again.")
else: 
    printText(T_CLR_WARN, "One or more tests failed. Please fix the errors in your code and retry running the script.")