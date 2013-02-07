import sys
import shutil
import os.path

'''
Author: Nathan Feldkamp <nathanf7@ksu.edu>
last updated: 10/21/2012
'''

'''
This script will parse the output from the makefile and copy the source files, cflags, and ldflags to a new project directory.
In the flight/revolution/Makefile. At approx line 459 add the following to the makefile:

#DS Added, NJF Modified
$(warning START OF PRINTOUT)
$(warning -#SRC#- $(SRC))
$(warning -#CFLAGS#- $(CFLAGS))
$(warning -#LDFLAGS#- $(LDFLAGS))
$(warning END OF PRINTOUT)

'''

def make_path_for_file(path):
    """
    Creates the path for a file.
    """
    dirs = path.split("\\")
    create_path = ""
    try:
        for d in dirs:
            # make sure to not create a dir for the file
            # TODO: Use a better check than .c or .h
            if(not ".c" in d and not ".h" in d):
                #TODO: Use path.join for joining create_path and d
                create_path += d+"\\"
                if(not os.path.exists(create_path)):
                    os.mkdir(create_path)
    except:
        return False
    return True

def copy_file(src_file,dst_file):
    """
    Creates the path for the dst file if it does not exist and
    copies it from the src to the dst path.
    """
    if(make_path_for_file(dst_file)):
        #TODO: Add try catch
        shutil.copyfile(src_file, dst_file)

def main():
    """
    The main function for the script.
    """
    
    #Check that the number of arguments is exactly 2
    if(len(sys.argv) != 2):
        sys.exit("\nError Incorrect Usage\n\n\tUsage\n\t\t parse_make_log.py makefileoutput.txt\n")
    
    #TODO: Make verbose a command line argument
    verbose = True
    #TODO: Make copy a command line argument
    copy = True
    
    # The following three patterns are used in the make file when printing out the 3 lists of items.
    # We use these patterns to detect the lines we should be parsing, so it is important that the 
    # patterns below match the patterns in the makefile.
    src_pattern = "-#SRC#-"
    cflags_pattern = "-#CFLAGS#-"
    ldflags_pattern = "-#LDFLAGS#-"
    
    #This is the name of the temporary directory that will be copied into the Atollic project.
    #TODO: Make new_proj_name a command line argument or ask for it.
    new_project_name = "ksu_revo"
    
    # Get the current working directory (cwd) and make sure the drive letter is capitalized.
    # The output from the make file is not always capitalized so we need to make sure everything is the same.
    cwd = os.getcwd()[0].upper() + os.getcwd()[1:]
    
    #This creates the path to the temporary project.
    new_dir = os.path.normpath(os.path.join(cwd,"../"+new_project_name))
    
    # Remove the existing shadow directory
    if(os.path.exists(new_dir)):
        #print("\nWarning!\n\t" + new_dir + "already exists and will be erased.\nPress any key to continue..."),
        #raw_input()
        if(copy):
            print("\nWarning!\n\t" + new_dir + "already exists and will be erased.")
            shutil.rmtree(new_dir)
    
    #This is the path to the Revolution code in the OpenPilot Repository (this should never change)
    base_path = "flight/Revolution/"    
    
    print("Parsing " + os.path.join(cwd,str(sys.argv[1])) + "\n\tFiles will be copied to the intermediate directory at: "+new_dir)
    
    #Now try to open the file that was passed in.
    try:
        fh = open(sys.argv[1])
    except IOError as ioe:
        sys.exit("\nError opening \"" + sys.argv[1]+"\"\n\t" + ioe.strerror)
    
    # Set up for storing the data.
    src_files = []
    cflags = []
    symbols = []
    includes_dirs = []
    ldflags = []
    
    for line in fh:
        # Strip return and extra spaces and split into list on spaces
        row = line.rstrip().rsplit(" ")
        # This just filters out useless data 
        if(len(row) > 2):
            # pattern is one of the values specified above
            pattern = row[1]
            
            #Parse the Source Files
            if(pattern == src_pattern):
                print("\n Pattern: "+src_pattern)
                for i,src_file in enumerate(row):
                    src_file = src_file.rstrip()
                    old_file = src_file
                    if(i > 1 and src_file != " " and src_file != "." and src_file != ""):
                        if(src_file[0:2] == "./"):
                            src_file = base_path + src_file[2:]
                        elif(src_file[0:2] == ".."):
                            src_file = base_path + src_file
                        else:
                            src_file = src_file[0].upper()+src_file[1:]
                        
                        src_file = os.path.abspath(os.path.normpath(src_file))
                        src_file = src_file[0].upper()+src_file[1:]
                        src_files.append(src_file)
                        
                        file_exists = os.path.exists(src_file)
                        
                        new_src_file = src_file.replace(cwd,new_dir)
                        
                        if(verbose):
                            print("\tBefore: "+old_file+"\n\tAfter : "+src_file+"\n\tExists: "+str(file_exists)+"\n\tNew   : "+new_src_file+"\n")
                        
                        if(file_exists and copy):
                            if(src_file != new_src_file):
                                copy_file(src_file,new_src_file)
                            else:
                                print("\nError: \n\tThere was an error replacing the cwd of the source file with the shadow directory.\n\tPlease contact the author.")
            
            #Parse the CFLAGS
            elif(pattern == cflags_pattern):
                print("\nPattern: "+cflags_pattern)
                for i,cflag in enumerate(row):
                    #Filter out useless data
                    if(i > 1 and cflag != ""):
                        if(cflag[0:2] == "-I"):
                            if(verbose):
                                print("\t"+cflag)
                            
                            include_dir = cflag[2:]
                            
                            if(include_dir[0:2] == ".."):
                                include_dir = os.path.abspath(os.path.normpath(base_path + include_dir))
                            elif(include_dir[0:2] == "c:" or include_dir[0:2] == "C:"):
                                include_dir = include_dir[0].upper()+include_dir[1:]
                                include_dir = os.path.abspath(os.path.normpath(include_dir.replace(str(cwd+"\\").replace("\\","/"),"")))
                            else:
                                include_dir = os.path.abspath(os.path.normpath(base_path+include_dir))
                            
                            # Make sure the drive letter is capitalized.
                            include_dir = include_dir[0].upper()+include_dir[1:]
                            
                            if(os.path.exists(include_dir)):
                                new_inc_dir = include_dir.replace(cwd,new_dir)
                                includes_dirs.append(os.path.abspath(os.path.normpath(new_inc_dir)))
                                files = os.listdir(include_dir)
                                for f in files:
                                    # Check that file is a file we want to copy.
                                    if(".h" in f or f == "board_hw_defs.c"):
                                        old_inc_file = os.path.join(include_dir,f)
                                        file_exists = os.path.exists(old_inc_file)
                                        new_inc_file = os.path.join(new_inc_dir,f)
                                        
                                        if(verbose):
                                            print("\tSource: "+old_inc_file+"\n\tExists: "+str(file_exists)+"\n\tNew   : "+new_inc_file+"\n")
                                        
                                        if(file_exists and copy):
                                            if(old_inc_file != new_inc_file):
                                                copy_file(old_inc_file,new_inc_file)
                                            else:
                                                print("\nError: \n\tThere was an error replacing the cwd of the header file with the shadow directory.\n\tPlease contact the author.")

                        elif(cflag[0:2] == "-D"):
                            symbols.append(cflag[2:])
                            if(verbose):
                                print("\t"+cflag)
                        else:
                            if(cflag[0:2] == "c:"):
                                cflag = cflag[0].upper()+cflag[1:]
                                cflag = os.path.normpath(cflag.replace(str(cwd+"\\").replace("\\","/"),new_dir+"\\"))
                            cflags.append(cflag)
                            if(verbose):
                                print("\t"+cflag)
            
            # Parse the LDFLAGS
            elif(pattern == ldflags_pattern):
                print("\nPattern: "+ldflags_pattern)
                for i,ldflag in enumerate(row):
                    if(i > 1 and ldflag != ""):
                        if(ldflag[0:2] == "-T"):
                            ld = ldflag[2:]
                            ld = os.path.normpath(os.path.join(os.path.join(new_dir,base_path),ld)).replace("\\","/")
                            ldflag = "-T"+ld
                        elif(ldflag[0:9] == "-Wl,-Map="):
                            ld = ldflag[9:]
                            ld = ld[0].upper()+ld[1:]
                            ld = os.path.normpath(ld.replace(str(cwd+"\\").replace("\\","/"),new_dir+"\\")).replace("\\","/")
                            ldflag = "-Wl,-Map="+ld
                        ldflags.append(ldflag)
                        if(verbose):
                            print("\t"+ldflag)
    
    fh = open(os.path.join(new_dir,"INCLUDES.txt"),"w")
    for inc_dir in includes_dirs:
        val = inc_dir
        #The following line encloses the include dir in the xml for the eclipse .cproject
        val = "<listOptionValue builtIn=\"false\" value=\"&quot;${workspace_loc:/${ProjName}"+inc_dir.replace(new_dir,"")+"}&quot;\"/>"
        val = val.replace('\\', '/')
        fh.write(val+"\n")
    fh.close()
    print("INCLUDES.txt written.")
    
    fh = open(os.path.join(new_dir,"SYMBOLS.txt"),"w")
    for symbol in symbols:
        #The following line encloses the include symbols in the xml for the eclipse .cproject
        fh.write("<listOptionValue builtIn=\"false\" value=\""+symbol+"\"/>\n")
    fh.close()
    print("SYMBOLS.txt written")
    
    fh = open(os.path.join(new_dir,"CFLAGS.txt"),"w")
    for cflag in cflags:
        fh.write(cflag+" "+"\n")
    fh.close()
    print("CFLAGS.txt written")
    
    fh = open(os.path.join(new_dir,"LDFLAGS.txt"),"w")
    for ldf in ldflags:
        fh.write(ldf+" "+"\n")
    fh.close()
    print("LDFLAGS.txt written.")


if(__name__ == "__main__"):
    main()
