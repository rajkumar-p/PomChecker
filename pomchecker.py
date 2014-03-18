import xml.etree.ElementTree as ET
import Queue
import string
import os.path
import argparse

def areSame(pom_file, pom_template_file, logger):
    """
    Module checks if the two XML passed is syntactically similar
    input: file1, file2
    """
    node1 = ET.parse(pom_file).getroot()
    node2 = ET.parse(pom_template_file).getroot()

    # Q that contains the nodes
    q = Queue.Queue()
    q.put((node1, node2))

    # Process all the nodes in the XML tree
    while not q.empty():
        (node1, node2) = q.get()

        # Check if the tags are equal
        if node1.tag != node2.tag:
            writeLineToFile(logger, main_error_msg.format(error_msg_tags_not_equal,
                                              node1.tag, node2.tag))
            return False

        if node1.text != None:
            node1.text = node1.text.strip(string.whitespace)

        if node2.text != None:
            node2.text = node2.text.strip(string.whitespace)

        # Check if the node text are equal
        if node1.text != node2.text:
            writeLineToFile(logger, main_error_msg.format(error_msg_node_text_not_equal,
                                              node1.tag, node2.tag))
            return False

        # Check if the attributes are similar
        node1_attributes = node1.attrib
        node2_attributes = node2.attrib

        for key in node1_attributes.keys():
            if node1_attributes[key] == node2_attributes[key]:
                del node2_attributes[key]
            else:
                writeLineToFile(logger, main_error_msg.format(error_msg_diff_in_attributes,
                                                  node1.tag, node2.tag))
                return False

        if len(node2_attributes) != 0:
            writeLineToFile(logger, main_error_msg.format(error_msg_diff_in_attributes,
                                              node1.tag, node2.tag))
            return False

        # Process the current node's children
        node1_children = list(node1)
        node2_children = list(node2)

        if len(node1_children) != len(node2_children):
            writeLineToFile(logger, main_error_msg.format(error_msg_no_children_diff,
                                              node1.tag, node2.tag))
            return False
        else:
            node1_children.sort(key=lambda node: node.tag)
            node2_children.sort(key=lambda node: node.tag)

            for item in zip(node1_children, node2_children):
                q.put(item)

    return True

def writeToFile(file_handle, string_to_be_written):
    """
    Helper to write to a file
    input: file_handle, string_to_be_written
    """
    file_handle.write(string_to_be_written)

def writeLineToFile(file_handle, string_to_be_written):
    """
    Helper to write line to file
    input: file_handle, string_to_be_written
    """
    writeToFile(file_handle, string_to_be_written)
    writeToFile(file_handle, "\n")

def printList(li):
    """
    Helper to print a list
    input: list
    """
    for item in li:
        print item

def printHeader(title):
    """
    Helper to print the title and a banner below
    input: title
    """
    print title
    print "-" * len(title)

def printDirBanner(file_handle, current_dir):
    """
    Helper to print a banner around the current directory
    input: current_dir
    """
    writeLineToFile(file_handle, len(current_dir)*header_char)
    writeLineToFile(file_handle, current_dir)
    writeLineToFile(file_handle, len(current_dir)*header_char)

# Logger to be used during run
logger = open("pomchecker_session.log", "w")

# Parse the command line arguments
arguments_parser = argparse.ArgumentParser()

arguments_parser.add_argument("-1", "--pom_not_present",
                              action="store_true",
                              help="Shows the list of directories where pom files are not present")

arguments_parser.add_argument("-2", "--pomtemplate_not_present",
                              action="store_true",
                              help="Shows the list of directories where pom template files are not present")

arguments_parser.add_argument("-3", "--both_not_present",
                              action="store_true",
                              help="Shows the list of directories where pom and pom template files are not present")

arguments_parser.add_argument("-4", "--both_same",
                              action="store_true",
                              help="Shows the list of directories where pom and pom template files are the same")

arguments_parser.add_argument("-5", "--both_different",
                              action="store_true",
                              help="Shows the list of directories where pom and pom template files are the not the same")

arguments_parser.add_argument("-nh", "--no_header",
                              action="store_true",
                              help="Flag to not show headers in the output")

arguments_parser.add_argument("-start", "--start_dir",
                              type=str,
                              help="The start directory from where to start the check")

arguments_parser.add_argument("-stop", "--stop_dir",
                              type=str,
                              help="The directory from where to stop processing it and its children")


commandline_arguments = arguments_parser.parse_args()

# Load defaults if not given in the command line arguments
if commandline_arguments.start_dir:
    starting_dir = commandline_arguments.start_dir
else:
    starting_dir = "."

if commandline_arguments.stop_dir:
    stop_dir = commandline_arguments.stop_dir
else:
    stop_dir = "XXXXXXXXXX"

header_char = "-"

# Error messages
error_msg_tags_not_equal = "Tags are not equal"
error_msg_node_text_not_equal = "Node text are not equal"
error_msg_diff_in_attributes = "Difference in attributes"
error_msg_no_children_diff = "Number of children not equal"

error_msg_files_same = "Both the files are same."
error_msg_files_not_same = "Pom and Pom template are different."

stopping_at_dir = "STOPPING AT DIR - {0}."

main_error_msg = "{0}. Diff tag(s) - {1}, {2}."

error_msg_both_not_present = "Pom and pom template not present."
error_msg_pom_not_present = "Pom not present."
error_msg_pom_template_not_present = "Pom template not present."

# List to contain the outputs
pom_not_present_list = []
pomtemplate_not_present_list = []
both_not_present_list = []

both_same_list = []
both_different_list = []

# Directories Q
directories = Queue.Queue()
directories.put(os.path.abspath(starting_dir))

# Recuse till no directory left to process
while not directories.empty():
    current_dir = directories.get()

    if current_dir == stop_dir:
        writeLineToFile(logger, stopping_at_dir.format(current_dir))
        continue

    # Push the child directories into the directories Q
    for d in [os.path.join(current_dir, directoy)
                for directoy in os.listdir(current_dir)
                    if os.path.isdir(current_dir + os.path.sep + directoy)]:
        directories.put(d)

    pom_file = current_dir + os.path.sep + "pom.xml"
    pom_template_file = current_dir + os.path.sep + "pom.template.xml"

    printDirBanner(logger, current_dir)

    pom_present_flag = True
    pom_template_present_flag = True

    # Check if files present
    try:
        with open(pom_file):
            pass
    except IOError:
        pom_present_flag = False

    try:
        with open(pom_template_file):
            pass
    except IOError:
        pom_template_present_flag = False

    # Populate output lists
    if not pom_present_flag and not pom_template_present_flag:
        writeLineToFile(logger, error_msg_both_not_present)
        writeLineToFile(logger, "")
        both_not_present_list.append(current_dir)
        continue
    elif not pom_present_flag:
        writeLineToFile(logger, error_msg_pom_not_present)
        writeLineToFile(logger, "")
        pom_not_present_list.append(current_dir)
        continue
    elif not pom_template_present_flag:
        writeLineToFile(logger, error_msg_pom_template_not_present)
        writeLineToFile(logger, "")
        pomtemplate_not_present_list.append(current_dir)
        continue

    if areSame(pom_file, pom_template_file, logger):
        both_same_list.append(current_dir)
        writeLineToFile(logger, error_msg_files_same)
    else:
        both_different_list.append(current_dir)
        writeLineToFile(logger, error_msg_files_not_same)

    writeLineToFile(logger, "")

# Give output asked
if commandline_arguments.pom_not_present:
    if not commandline_arguments.no_header:
        printHeader("Poms not present")

    printList(pom_not_present_list)
    print("")

if commandline_arguments.pomtemplate_not_present:
    if not commandline_arguments.no_header:
        printHeader("Pom templates not present")

    printList(pomtemplate_not_present_list)
    print("")

if commandline_arguments.both_not_present:
    if not commandline_arguments.no_header:
        printHeader("Pom and pom template not present")

    printList(both_not_present_list)
    print("")

if commandline_arguments.both_same:
    if not commandline_arguments.no_header:
        printHeader("Pom and pom template same")

    printList(both_same_list)
    print("")

if commandline_arguments.both_different:
    if not commandline_arguments.no_header:
        printHeader("Pom and pom template different")

    printList(both_different_list)
    print("")
