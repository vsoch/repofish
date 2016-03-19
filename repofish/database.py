import os
import re

# Need function to parse a python module for available functions and options
def get_functions(module_folder):
    '''get_functions: parses a python module folder, and returns a data structure with arguments and defaults
    '''
    module_folder = os.path.abspath(module_folder)
    functions = dict()
    for root, subs, files in os.walk(module_folder):
        basename = os.path.basename(root)
        if basename not in ["tests","testing","test"] and not re.search("^_",basename):
            py_files = sorted(f for f in files if os.path.splitext(f)[1] in ".py")
            # Remove hidden and private files
            py_files = [x for x in py_files if not re.search("^_|^[.]",x)]
            # Add functions to data structure
            for py_file in py_files:
                module_functions = dict()
                classes = dict()
                module = os.path.splitext(py_file)[0]
                filey = open("%s/%s" %(root,py_file),"rb")
                lines = filey.read().splitlines()
                filey.close()
                if len(lines) > 0:
                    # First split code up by (likely) classes
                    class_idx = [x for x in range(len(lines)) if re.search("^class ",lines[x].strip())]
                    if len(class_idx) == 0:
                        class_idx = [len(lines)-1]  
                    class_idx.insert(0,0)
                    for c in range(len(class_idx)-1):
                        start_idx = class_idx[c]
                        end_idx = class_idx[c+1]     
                        new_functions = get_functions_lines(lines[start_idx:end_idx])
                        # If it's a class, append to classes
                        if re.search("^class ",lines[start_idx].strip()):
                            class_name = get_class_name(lines[start_idx])
                            if len(new_functions) > 0:
                                classes[class_name] = new_functions
                        else:
                            module_functions.update(new_functions)
                    # Only add to list if we found functions
                    add = False
                    if len(module_functions) > 0:
                        add = True
                        classes["*"] = module_functions
                    if len(classes.keys()) > 0:
                        add = True                    
                    if add == True:
                        functions[module] = classes
    return functions

def get_class_name(classline):
    classline = classline.replace("class","").strip()
    return classline.split("(")[0]

def get_functions_lines(lines):
    functions = dict()
    while len(lines) > 0:
       line = lines.pop(0).strip()
       # Functions outside of class
       if re.search("^def ",line):
           if not re.search("^#",line):
               function_name,function_args = line.split("(",1)
               function_name = function_name.split(" ")[-1]
               print "Adding function %s" %(function_name)
               # If no closing parens is present, we have to continue until we find one
               while not re.search("[)]:",function_args):
                   nextline = lines.pop(0)
                   function_args = "%s, %s" %(function_args,nextline)
               function_args = function_args.strip(":")
               function_args = [x.strip() for x in function_args.strip("):").split(",") if x != "self"]
               # Get defaults
               arg_list = []
               for function_arg in function_args:       
                   if re.search("=",function_arg):
                       arg_value,arg_default = function_arg.split("=",1)
                       arg_list.append({"name":arg_value,
                                       "default":arg_default})
                   else:                              
                       arg_list.append({"name":function_arg})
               functions[function_name] = dict()
               functions[function_name]["args"] = arg_list                        
    return functions
