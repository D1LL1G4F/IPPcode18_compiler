import sys
import argparse
import os
import math
import xml.etree.ElementTree as ET
from xml.etree.ElementTree import ParseError


class Variable():
    name = None
    type = None
    value = None

    def __init__(self, name, type, value):
        self.name = name
        self.type = type
        if type == "string":
            self.value = value
        elif type == "int":
            try:
                self.value = int(value)
            except Exception:
                sys.stderr.write("ERROR 32: value of variable \"{}\" is wrong"
                                 " (supposed to be integer)\n".format(name))
                sys.exit(32)
        elif type == "bool":
            if value == "true":
                self.value = True
            elif value == "false":
                self.value = False
            else:
                sys.stderr.write("ERROR 32: value of variable \"{}\" is wrong"
                                 " (supposed to be boolean)\n".format(name))
                sys.exit(32)
        else:
            sys.stderr.write("ERROR 32: wrong type of variable \"{}\""
                             "\n".format(name))
            sys.exit(32)


class Frame():
    variable = None
    defined = None

    def __init__(self, status):
        self.variable = {}
        self.defined = status

    def defVar(self, name):
        self.variable[name] = None

    def setVar(self, var):
        if var.name in self.variable:
            self.variable[var.name] = var
        else:
            sys.stderr.write("ERROR 54: variable \"{}\" doesn't exist"
                             "\n".format(var.name))
            sys.exit(54)

    def clear(self):
        self.variable.clear()
        self.defined = False

    def define(self):
        self.defined = True


class StackFrame():
    stack = None
    empty = None

    def __init__(self, status):
        self.stack = ()
        self.empty = True




def argumentsHadling():
    parser = argparse.ArgumentParser(prog="interpret.py", add_help=True)
    parser.add_argument("--source", required=True, nargs=1, metavar="FILE",
                        help="input file with XML representation of src code")
    try:
        args = parser.parse_args()
    except SystemExit:
        sys.stderr.write("ERROR 10: Wrong arguments\n")
        sys.exit(10)

    return args


def openFile(fileName):
    if os.path.exists(fileName):
        try:
            file = open(fileName, 'r')
        except IOError:
            sys.stderr.write("ERROR 11: Could not open file to read\n")
            sys.exit(11)
    else:
        sys.stderr.write("ERROR 11: File not found\n")
        sys.exit(11)
    return file


def parseFile(file):
    try:
        tree = ET.parse(file)
    except ParseError:
        sys.stderr.write("ERROR 31: Wrongly formatted XML file\n")
        sys.exit(31)
    return tree


def checkTag(element, tag):
    if (element.tag != tag):
        sys.stderr.write("ERROR 31: Wrongly formatted XML file (wrong tag)\n")
        sys.exit(31)
    return


def checkProgramFormatting(program):
    checkTag(program, "program")
    if (len(program.attrib) != 1):
        sys.stderr.write("ERROR 31: Wrongly formatted XML file (wrong program"
                         " attributes)\n")
        sys.exit(31)
    language = program.attrib.get("language")
    if (language != "IPPcode18"):
        sys.stderr.write("ERROR 31: Wrongly formatted XML file (unsupported"
                         " language)\n")
        sys.exit(31)
    for instruction in program:
        checkTag(instruction, "instruction")
        if (len(instruction.attrib) != 2):
            sys.stderr.write("ERROR 31: Wrongly formatted XML file (wrong ins"
                             "truction attributes)\n")
            sys.exit(31)
        try:
            order = int(instruction.attrib.get("order"))
        except Exception:
            sys.stderr.write("ERROR 31: Wrongly formatted XML file (invalid or"
                             " missing order number in instruction)\n")
            sys.exit(31)
        if (order < 0):
            sys.stderr.write("ERROR 31: Wrongly formatted XML file (order nu"
                             "mber in instruction must be positive)\n")
            sys.exit(31)
        if (instruction.attrib.get("opcode") is None):
            sys.stderr.write("ERROR 31: Wrongly formatted XML file (missing o"
                             "pcode argument in instruction)\n")
            sys.exit(31)


# function for finding instruction with selected instructionNumber
# arg1: instructionNumber -> order number of required instructionNumber
# arg2: program -> root of tree containing endOfProgram
# return val: if founded successfully returns instruction in case order number
#             doesn't exist returns instruction with next higher order number
#             and reports warning on stderr if there is no bigger order number
#             returns None
def lookUpInstuct(instructionNumber, program):
    endOfProgram = True
    followingInstructionNum = math.inf
    followingInstruction = None
    for instruction in program:
        instructOrderNum = int(instruction.attrib.get("order"))
        if instructOrderNum == instructionNumber:
            return instruction
        elif instructOrderNum > instructionNumber:
            endOfProgram = False
            if instructOrderNum < followingInstructionNum:
                followingInstructionNum = instructOrderNum
                followingInstruction = instruction
    if endOfProgram:
        return None
    else:
        sys.stderr.write("WARNING: Instruction number: {} not found continu"
                         "ing with instruction number: {}\n"
                         .format(instructionNumber, followingInstructionNum))
        return followingInstruction


def parseMove(instruction):
    instructOrderNum = int(instruction.attrib.get("order"))
    print(instruction.attrib)
    return instructOrderNum+1


def parseCreateframe(instruction):
    instructOrderNum = int(instruction.attrib.get("order"))
    print(instruction.attrib)
    return instructOrderNum+1


def parsePushframe(instruction):
    instructOrderNum = int(instruction.attrib.get("order"))
    print(instruction.attrib)
    return instructOrderNum+1


def parsePopframe(instruction):
    instructOrderNum = int(instruction.attrib.get("order"))
    print(instruction.attrib)
    return instructOrderNum+1


def parseDefvar(instruction):
    instructOrderNum = int(instruction.attrib.get("order"))
    print(instruction.attrib)
    return instructOrderNum+1


def parseCall(instruction):
    instructOrderNum = int(instruction.attrib.get("order"))
    print(instruction.attrib)
    return instructOrderNum+1


def parseReturn(instruction):
    instructOrderNum = int(instruction.attrib.get("order"))
    print(instruction.attrib)
    return instructOrderNum+1


def parsePushs(instruction):
    instructOrderNum = int(instruction.attrib.get("order"))
    print(instruction.attrib)
    return instructOrderNum+1


def parsePops(instruction):
    instructOrderNum = int(instruction.attrib.get("order"))
    print(instruction.attrib)
    return instructOrderNum+1


def parseAdd(instruction):
    instructOrderNum = int(instruction.attrib.get("order"))
    print(instruction.attrib)
    return instructOrderNum+1


def parseSub(instruction):
    instructOrderNum = int(instruction.attrib.get("order"))
    print(instruction.attrib)
    return instructOrderNum+1


def parseMul(instruction):
    instructOrderNum = int(instruction.attrib.get("order"))
    print(instruction.attrib)
    return instructOrderNum+1


def parseIdiv(instruction):
    instructOrderNum = int(instruction.attrib.get("order"))
    print(instruction.attrib)
    return instructOrderNum+1


def parseLt(instruction):
    instructOrderNum = int(instruction.attrib.get("order"))
    print(instruction.attrib)
    return instructOrderNum+1


def parseGt(instruction):
    instructOrderNum = int(instruction.attrib.get("order"))
    print(instruction.attrib)
    return instructOrderNum+1


def parseEq(instruction):
    instructOrderNum = int(instruction.attrib.get("order"))
    print(instruction.attrib)
    return instructOrderNum+1


def parseAnd(instruction):
    instructOrderNum = int(instruction.attrib.get("order"))
    print(instruction.attrib)
    return instructOrderNum+1


def parseOr(instruction):
    instructOrderNum = int(instruction.attrib.get("order"))
    print(instruction.attrib)
    return instructOrderNum+1


def parseNot(instruction):
    instructOrderNum = int(instruction.attrib.get("order"))
    print(instruction.attrib)
    return instructOrderNum+1


def parseInt2char(instruction):
    instructOrderNum = int(instruction.attrib.get("order"))
    print(instruction.attrib)
    return instructOrderNum+1


def parseStri2int(instruction):
    instructOrderNum = int(instruction.attrib.get("order"))
    print(instruction.attrib)
    return instructOrderNum+1


def parseRead(instruction):
    instructOrderNum = int(instruction.attrib.get("order"))
    print(instruction.attrib)
    return instructOrderNum+1


def parseWrite(instruction):
    instructOrderNum = int(instruction.attrib.get("order"))
    print(instruction.attrib)
    return instructOrderNum+1


def parseConcat(instruction):
    instructOrderNum = int(instruction.attrib.get("order"))
    print(instruction.attrib)
    return instructOrderNum+1


def parseStrlen(instruction):
    instructOrderNum = int(instruction.attrib.get("order"))
    print(instruction.attrib)
    return instructOrderNum+1


def parseGetchar(instruction):
    instructOrderNum = int(instruction.attrib.get("order"))
    print(instruction.attrib)
    return instructOrderNum+1


def parseSetchar(instruction):
    instructOrderNum = int(instruction.attrib.get("order"))
    print(instruction.attrib)
    return instructOrderNum+1


def parseType(instruction):
    instructOrderNum = int(instruction.attrib.get("order"))
    print(instruction.attrib)
    return instructOrderNum+1


def parseLabel(instruction):
    instructOrderNum = int(instruction.attrib.get("order"))
    print(instruction.attrib)
    return instructOrderNum+1


def parseJump(instruction):
    instructOrderNum = int(instruction.attrib.get("order"))
    print(instruction.attrib)
    return instructOrderNum+1


def parseJumpifeq(instruction):
    instructOrderNum = int(instruction.attrib.get("order"))
    print(instruction.attrib)
    return instructOrderNum+1


def parseJumpifneq(instruction):
    instructOrderNum = int(instruction.attrib.get("order"))
    print(instruction.attrib)
    return instructOrderNum+1


def parseDprint(instruction):
    instructOrderNum = int(instruction.attrib.get("order"))
    print(instruction.attrib)
    return instructOrderNum+1


def parseBreak(instruction):
    instructOrderNum = int(instruction.attrib.get("order"))
    print(instruction.attrib)
    return instructOrderNum+1


opcodeParser = {
     "MOVE": parseMove,
     "CREATEFRAME": parseCreateframe,
     "PUSHFRAME": parsePushframe,
     "POPFRAME": parsePopframe,
     "DEFVAR": parseDefvar,
     "CALL": parseCall,
     "RETURN": parseReturn,
     "PUSHS": parsePushs,
     "POPS": parsePops,
     "ADD": parseAdd,
     "SUB": parseSub,
     "MUL": parseMul,
     "IDIV": parseIdiv,
     "LT": parseLt,
     "GT": parseGt,
     "EQ": parseEq,
     "AND": parseAnd,
     "OR": parseOr,
     "NOT": parseNot,
     "INT2CHAR": parseInt2char,
     "STRI2INT": parseStri2int,
     "READ": parseRead,
     "WRITE": parseWrite,
     "CONCAT": parseConcat,
     "STRLEN": parseStrlen,
     "GETCHAR": parseGetchar,
     "SETCHAR": parseSetchar,
     "TYPE": parseType,
     "LABEL": parseLabel,
     "JUMP": parseJump,
     "JUMPIFEQ": parseJumpifeq,
     "JUMPIFNEQ": parseJumpifneq,
     "DPRINT": parseDprint,
     "BREAK": parseBreak,
}


def interpretInstruction(instruction):
    opcode = instruction.attrib.get("opcode")
    if opcode in opcodeParser:
        return opcodeParser[opcode](instruction)
    else:
        sys.stderr.write("ERROR 32: Unknown opcode \"{}\"\n".format(opcode))
        sys.exit(32)


def main():
    args = argumentsHadling()  # parsing of argiments
    fileName = ''.join(args.source)
    file = openFile(fileName)  # open file
    program = parseFile(file).getroot()  # get root from XML file

    checkProgramFormatting(program)  # check valid tags/args of prog and instr.

    nextInstructionNumber = 1  # start with first instruction
    instruction = lookUpInstuct(nextInstructionNumber, program)
    while (instruction):
        nextInstructionNumber = interpretInstruction(instruction)
        instruction = lookUpInstuct(nextInstructionNumber, program)


if __name__ == '__main__':
    main()
