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
            logger.write("diff tag(s) - [{0}, {1}]\n".format(node1.tag, node2.tag))
            return False

        if node1.text != None:
            node1.text = node1.text.strip(string.whitespace)

        if node2.text != None:
            node2.text = node2.text.strip(string.whitespace)

        if node1.text != node2.text:
            logger.write("diff tag(s) - [{0}, {1}]\n".format(node1.tag, node2.tag))
            return False

        node1_attributes = node1.attrib
        node2_attributes = node2.attrib

        for key in node1_attributes.keys():
            if (node1_attributes[key] == node2_attributes[key]):
                del node2_attributes[key]
            else:
                logger.write("diff tag(s) - [{0}, {1}]\n".format(node1.tag, node2.tag))
                return False

        if (len(node2_attributes) != 0):
            logger.write("diff tag(s) - [{0}, {1}]\n".format(node1.tag, node2.tag))
            return False

        node1_children = list(node1)
        node2_children = list(node2)

        if (len(node1_children) != len(node2_children)):
            logger.write("diff tag(s) - [{0}, {1}]\n".format(node1.tag, node2.tag))
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

header_lines = 30*"-"

directories = Queue.Queue()
directories.put(starting_dir)

while not directories.empty():
    current_dir = directories.get()

    if (current_dir == stop_dir):
        exit(0)

    pom_file = current_dir + os.path.sep + "pom.xml"
    pom_template_file = current_dir + os.path.sep + "pom.template.xml"

    logger.write(header_lines)
    logger.write("DIR: [{0}]\n".format(os.path.abspath()))
    logger.write(header_lines)

