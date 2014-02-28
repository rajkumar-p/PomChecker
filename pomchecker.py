import xml.etree.ElementTree as ET
import Queue
import string
import os.path
import argparse

def areSame(pom_file, pom_template_file, logger):
    node1 = ET.parse(pom_file).getroot()
    node2 = ET.parse(pom_template_file).getroot()

    q = Queue.Queue()
    q.put((node1, node2))

    while not q.empty():
        (node1, node2) = q.get()

        if node1.tag != node2.tag:
            writeLineToLog(logger, main_error_msg.format(error_msg_tags_not_equal,
                                              node1.tag, node2.tag))
            return False

        if node1.text != None:
            node1.text = node1.text.strip(string.whitespace)

        if node2.text != None:
            node2.text = node2.text.strip(string.whitespace)

        if node1.text != node2.text:
            writeLineToLog(logger, main_error_msg.format(error_msg_node_text_not_equal,
                                              node1.tag, node2.tag))
            return False

        node1_attributes = node1.attrib
        node2_attributes = node2.attrib

        for key in node1_attributes.keys():
            if node1_attributes[key] == node2_attributes[key]:
                del node2_attributes[key]
            else:
                writeLineToLog(logger, main_error_msg.format(error_msg_diff_in_attributes,
                                                  node1.tag, node2.tag))
                return False

        if len(node2_attributes) != 0:
            writeLineToLog(logger, main_error_msg.format(error_msg_diff_in_attributes,
                                              node1.tag, node2.tag))
            return False

        node1_children = list(node1)
        node2_children = list(node2)

        if len(node1_children) != len(node2_children):
            writeLineToLog(logger, main_error_msg.format(error_msg_no_children_diff,
                                              node1.tag, node2.tag))
            return False
        else:
            node1_children.sort(key=lambda node: node.tag)
            node2_children.sort(key=lambda node: node.tag)

            for item in zip(node1_children, node2_children):
                q.put(item)

    return True

def writeToLog(logger, string_to_be_written):
    logger.write(string_to_be_written)

def writeLineToLog(logger, string_to_be_written):
    writeToLog(logger, string_to_be_written)
    writeToLog(logger, "\n")

def printList(li):
    for item in li:
        print item

def printHeader(title):
    print title
    print "-" * len(title)

def printDirBanner(current_dir):
    writeLineToLog(logger, len(current_dir)*header_char)
    writeLineToLog(logger, current_dir)
    writeLineToLog(logger, len(current_dir)*header_char)

# Load the default settings
logger = open("session.log", "w")

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

commandline_arguments = arguments_parser.parse_args()

starting_dir = "."
stop_dir = "xxxxxx"

header_char = "-"

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

pom_not_present_list = []
pomtemplate_not_present_list = []
both_not_present_list = []

both_same_list = []
both_different_list = []

directories = Queue.Queue()
directories.put(os.path.abspath(starting_dir))

while not directories.empty():
    current_dir = directories.get()

    if current_dir == stop_dir:
        writeLineToLog(logger, stopping_at_dir.format(current_dir))
        exit(0)

    # Push the child directories into the directories Q
    for d in [os.path.join(current_dir, directoy)
                for directoy in os.listdir(current_dir)
                    if os.path.isdir(current_dir + os.path.sep + directoy)]:
        directories.put(d)

    pom_file = current_dir + os.path.sep + "pom.xml"
    pom_template_file = current_dir + os.path.sep + "pom.template.xml"

    printDirBanner(current_dir)

    pom_present_flag = True
    pom_template_present_flag = True

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

    if not pom_present_flag and not pom_template_present_flag:
        writeLineToLog(logger, error_msg_both_not_present)
        writeLineToLog(logger, "")
        both_not_present_list.append(current_dir)
        continue
    elif not pom_present_flag:
        writeLineToLog(logger, error_msg_pom_not_present)
        writeLineToLog(logger, "")
        pom_not_present_list.append(current_dir)
        continue
    elif not pom_template_present_flag:
        writeLineToLog(logger, error_msg_pom_template_not_present)
        writeLineToLog(logger, "")
        pomtemplate_not_present_list.append(current_dir)
        continue

    if areSame(pom_file, pom_template_file, logger):
        both_same_list.append(current_dir)
        writeLineToLog(logger, error_msg_files_same)
    else:
        both_different_list.append(current_dir)
        writeLineToLog(logger, error_msg_files_not_same)

    writeLineToLog(logger, "")

if commandline_arguments.pom_not_present:
    printHeader("Poms not present")
    printList(pom_not_present_list)
    print("")

if commandline_arguments.pomtemplate_not_present:
    printHeader("Pom templates not present")
    printList(pomtemplate_not_present_list)
    print("")

if commandline_arguments.both_not_present:
    printHeader("Pom and pom template not present")
    printList(both_not_present_list)
    print("")

if commandline_arguments.both_same:
    printHeader("Pom and pom template same")
    printList(both_same_list)
    print("")

if commandline_arguments.both_different:
    printHeader("Pom and pom template different")
    printList(both_different_list)
    print("")
