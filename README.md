# PomChecker

## Overview
This is a simple utility to check if the pom and pom.template xml files are syntactically similar or not. The check is repeated as the program traverses to its children directories.

## Language & Compiler
Python 2.7+

## Usage
python pomchecker.py

The above command runs the program and checks the difference beteeen pom and pom templates. It does not output anything but instead writes the run to the session.log in the directory that the command is run.

In order to get the various output, you need pass what you want to the utility. The various output that can be got are given as below,

-1 (--pom_not_present) - This outputs the directories where the pom was not present  
-2 (--pomtemplate_not_present) - This outputs the directories where the pom template was not present  
-3 (--both_not_present) - This outputs the directories where both the pom and pom template was not present  
-4 (--both_same) - This outputs the directories where both the pom and pom template are the same  
-5 (--both_different) - This outputs the directories where both the pom and pom template are different  

So, to get the directories where the pom and pom template are different, run the command as,  

python pomchecker.py -4  

You can also get multiple outputs like,  

python pomchecker.py -4 -5  

You can control the start and stop directory during the run of the program. The default is to start from the current directory and end when all its children are processed. You can control them using the -start(--start_dir) and -stop(--stop_dir) options. For example,

python pomchecker.py -4 -start . -stop src  

You can also get the other options using the -h (--help) option.

## License
Free as in free speech.

## Contributions & Questions
Send me a mail on <raj@diskodev.com> or tweet me at <https://twitter.com/#!/rajkumar_p>
