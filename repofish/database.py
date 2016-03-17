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
                module = os.path.splitext(py_file)[0]
                filey = open("%s/%s" %(root,py_file),"rb")
                lines = filey.read().splitlines()
                lines = [x.replace("def","").strip() for x in lines if re.search("def",x)]  
                for function in lines:
                    if not re.search("^_",function):
                        try: # lines with "def" that aren't functions
                            function_name,function_args = function.split("(")
                            print "Adding function %s" %(function_name)
                            function_args = [x.strip() for x in function_args.strip("):").split(",") if x != "self"]
                            # Get defaults
                            arg_list = []
                            for function_arg in function_args:       
                                if re.search("=",function_arg):
                                    arg_value,arg_default = function_arg.split("=")
                                    arg_list.append({"name":arg_value,
                                                    "default":arg_default})
                                else:                              
                                    arg_list.append({"name":function_arg})
                            functions[function_name] = dict()
                            functions[function_name]["args"] = arg_list 
                        except:
                            pass    

    return functions
