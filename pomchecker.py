import xml.etree.ElementTree as ET
import re
import Queue
import string
import os.path
import argparse

def areSame(pom_contents, pom_template_contents, logger):
    """
    Module checks if the two XML passed is syntactically similar
    input: pom_contents, pom_template_contents
    """
    node1 = ET.fromstring(pom_contents)
    node2 = ET.fromstring(pom_template_contents)

    # Q that contains the nodes
    q = Queue.Queue()
    q.put((node1, node2))

    # Process all the nodes in the XML tree
    while not q.empty():
        (node1, node2) = q.get()

        # Check if the tags are equal
        if not tagsAreEqual(node1, node2):
            writeLineToFile(logger, main_error_msg.format(error_msg_tags_not_equal,
                                              node1.tag, node2.tag))
            return False


        node1.text = stripNodeText(node1.text)
        node2.text = stripNodeText(node2.text)

        # Check if the node text are equal
        if not tagsTextAreEqual(node1, node2):
            writeLineToFile(logger, main_error_msg.format(error_msg_node_text_not_equal,
                                              node1.tag, node2.tag))
            return False

        # Check if the attributes are similar
        if not tagsAttributesAreEqual(node1, node2):
            writeLineToFile(logger, main_error_msg.format(error_msg_diff_in_attributes,
                                                node1.tag, node2.tag))

        # Process the current node's children
        node1_children = getNodesChildren(node1)
        node2_children = getNodesChildren(node2)

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

def tagsAreEqual(node1, node2):
    """
    Helper to check the given nodes
    input: node1, node2
    """
    return node1.tag == node2.tag

def tagsTextAreEqual(node1, node2):
    """
    Helper to check the given node's text
    input: node1, node2
    """
    return node1.text == node2.text

def tagsAttributesAreEqual(node1, node2):
    """
    Helper to check the given node's attributes
    input: node1, node2
    """
    node1_attributes = node1.attrib
    node2_attributes = node2.attrib

    for key in node1_attributes.keys():
        if node1_attributes[key] == node2_attributes[key]:
            del node2_attributes[key]
        else:
            return False

    if len(node2_attributes) != 0:
        return False

    return True

def getNodesChildren(node):
    """
    Helper to get a node's children
    input: node
    """
    return list(node)

def stripNodeText(text):
    """
    Helper to strip whitespace around a node text
    input: node
    """
    if text != None:
        return text.strip(string.whitespace)
    else:
        return ""

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

def getChildrenDirectories(current_dir):
    """
    Helper module to get the children directories
    input: current_dir
    """
    return [os.path.join(current_dir, directoy)
                for directoy in os.listdir(current_dir)
                    if os.path.isdir(current_dir + os.path.sep + directoy)]

def fileExists(file_name):
    """
    Helper module to check if a file exists
    input: file_name
    """
    try:
        with open(pom_file):
            return True
    except IOError:
        return False

def getDirName(current_dir):
    return os.path.basename(current_dir.strip("/\\"))

# Logger to be used during run
logger = open("pc_session.log", "w")

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

arguments_parser.add_argument("-v", "--version",
                              type=str,
                              help="Version that needs to go in place of ${temp.version}")


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

    # Push the child directories into the directories Q
    children = getChildrenDirectories(current_dir)

    for d in children:
        if getDirName(d) != stop_dir:
            directories.put(d)

    pom_file = current_dir + os.path.sep + "pom.xml"
    pom_template_file = current_dir + os.path.sep + "pom.template.xml"

    printDirBanner(logger, current_dir)

    pom_present_flag = True
    pom_template_present_flag = True

    # Check if files present
    pom_present_flag = fileExists(pom_file)
    pom_template_present_flag = fileExists(pom_template_file)

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

    # Read the pom and pom.template contents
    pom_fh = open(pom_file, "r")
    pom_template_fh = open(pom_template_file, "r")

    pom_contents = pom_fh.read()
    pom_template_contents = pom_template_fh.read()

    pom_fh.close()
    pom_template_fh.close()

    # Make the substitution of ${temp.version} in pom.template
    # The substitution is to be made only if version was passed
    if commandline_arguments.version:
        p = re.compile(r"\$\{temp\.version\}")
        pom_template_subs_contents = p.sub(commandline_arguments.version, pom_template_contents)

    # Check if both the files are same
    if areSame(pom_contents, pom_template_contents, logger):
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
