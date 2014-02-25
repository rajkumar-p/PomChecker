import xml.etree.ElementTree as ET
import Queue
import string
import os.path

def aresame(pom_file, pom_template_file, logger):
    node1 = ET.parse(pom_file).getroot()
    node2 = ET.parse(pom_template_file).getroot()

    q = Queue.Queue()
    q.put(zip(node1, node2)[0])

    while not q.empty():
        (node1, node2) = q.get()

        if node1.tag != node2.tag:
            logger.write(error_message.format(tags_not_equal,
                                              node1.tag, node2.tag, file_newline))
            return False

        if node1.text != None:
            node1.text = node1.text.strip(string.whitespace)

        if node2.text != None:
            node2.text = node2.text.strip(string.whitespace)

        if node1.text != node2.text:
            logger.write(error_message.format(node_text_not_equal,
                                              node1.tag, node2.tag, file_newline))
            return False

        node1_attributes = node1.attrib
        node2_attributes = node2.attrib

        for key in node1_attributes.keys():
            if (node1_attributes[key] == node2_attributes[key]):
                del node2_attributes[key]
            else:
                logger.write(error_message.format(diff_in_attributes,
                                                  node1.tag, node2.tag, file_newline))
                return False

        if (len(node2_attributes) != 0):
            logger.write(error_message.format(diff_in_attributes,
                                              node1.tag, node2.tag, file_newline))
            return False

        node1_children = list(node1)
        node2_children = list(node2)

        if (len(node1_children) != len(node2_children)):
            logger.write(error_message.format(no_of_children_diff,
                                              node1.tag, node2.tag, file_newline))
            return False
        else:
            node1_children.sort()
            node2_children.sort()

            for item in zip(node1_children, node2_children):
                q.put(item)

    return True

# Load the default settings
logger = open("session.log", "w")

starting_dir = "."
stop_dir = "xxxxxx"

file_newline = "\n"

header_lines = 30*"-"
header_lines_with_newline = 30*"-" + file_newline

tags_not_equal = "Tags are not equal"
node_text_not_equal = "Node text are not equal"
diff_in_attributes = "Difference in attributes"
no_of_children_diff = "Number of children not equal"

dir_banner = "DIR: {0}{1}"
files_same = "Both the files are same.{0}"
files_not_same = "Pom and Pom template are different.{0}"

stopping_at_dir = "STOPPING AT DIR - {0}.{1}"

error_message = "{0}. Diff tag(s) - {1}, {2}.{3}"

error_msg_both_not_present = "Pom and pom template not present.{0}"
error_msg_pom_not_present = "Pom not present.{0}"
error_msg_pom_template_not_present = "Pom template not present.{0}"

pom_not_present = []
pomtemplate_not_present = []
both_not_present = []

both_docs_same = []
both_docs_different = []

directories = Queue.Queue()
directories.put(os.path.abspath(starting_dir))

while not directories.empty():
    current_dir = directories.get()

    if (current_dir == stop_dir):
        logger.write(stopping_at_dir.format(current_dir, file_newline))
        exit(0)

    # Push the child directories into the directories Q
    for d in [os.path.join(current_dir, directoy)
                for directoy in os.listdir(current_dir)
                    if os.path.isdir(current_dir + os.path.sep + directoy)]:
        directories.put(d)

    pom_file = current_dir + os.path.sep + "pom.xml"
    pom_template_file = current_dir + os.path.sep + "pom.template.xml"

    logger.write(header_lines_with_newline)
    logger.write(dir_banner.format(current_dir, file_newline))
    logger.write(header_lines_with_newline)

    pom_present = True
    pom_template_present = True

    try:
        with open(pom_file):
            pass
    except IOError:
        pom_present = False

    try:
        with open(pom_template_file):
            pass
    except IOError:
        pom_template_present = False

    if not pom_present and not pom_template_present:
        logger.write(error_msg_both_not_present.format(file_newline))
        logger.write(1*file_newline)
        both_not_present.append(current_dir)
        continue
    elif not pom_present:
        logger.write(error_msg_pom_not_present.format(file_newline))
        logger.write(1*file_newline)
        pom_not_present.append(current_dir)
        continue
    elif not pom_template_present:
        logger.write(error_msg_pom_template_not_present.format(file_newline))
        logger.write(1*file_newline)
        pomtemplate_not_present.append(current_dir)
        continue

    if (aresame(pom_file, pom_template_file, logger)):
        both_docs_same.append(current_dir)
        logger.write(files_same.format(file_newline))
    else:
        both_docs_different.append(current_dir)
        logger.write(files_not_same.format(file_newline))

    logger.write(1*file_newline)
