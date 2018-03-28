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
        if self.defined:
            self.variable[name] = None
        else:
            sys.stderr.write("ERROR 55: accesing undefined frame\n")
            sys.exit(55)

    def isVarDefined(self, varName):
        return varName in self.variable

    def isVarInitialized(self, varName):
        if self.variable[varName] is None:
            return False
        else:
            return True

    def getVar(self, varName):
        return self.variable[varName]

    def setVar(self, var):
        if var.name in self.variable:
            self.variable[var.name] = var
        else:
            sys.stderr.write("ERROR 54: variable \"{}\" is undefined"
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

    def __init__(self):
        self.stack = []
        self.empty = True

    def push(self, frame):
        self.empty = False
        if frame.defined is not True:
            sys.stderr.write("ERROR 55: pushing undefined frame\n")
            sys.exit(55)
        self.stack.append(frame)

    def pop(self):
        if self.empty:
            sys.stderr.write("ERROR 55: LF doesn't exist (empty stackframe)\n")
            sys.exit(55)
        if self.stack.count() == 1:
            self.empty = True
        return self.stack.pop()

    def getLF(self):
        if self.empty:
            sys.stderr.write("ERROR 55: LF doesn't exist (empty stackframe)\n")
            sys.exit(55)
        return self.stack[self.stack.count() - 1]


class CallStack():
    stack = None
    empty = None

    def __init__(self):
        self.stack = []
        self.empty = True

    def push(self, instructNumber):
        self.empty = False
        self.stack.append(instructNumber)

    def pop(self):
        if self.empty:
            sys.stderr.write("ERROR 56: Call stack is empty\n")
            sys.exit(56)
        if self.stack.count() == 1:
            self.empty = True
        return self.stack.pop()


class DataStack():
    stack = None
    empty = None

    def __init__(self):
        self.stack = []
        self.empty = True

    def push(self, variable):
        self.empty = False
        self.stack.append(variable)

    def pop(self):
        if self.empty:
            sys.stderr.write("ERROR 56: Data stack is empty\n")
            sys.exit(56)
        if self.stack.count() == 1:
            self.empty = True
        return self.stack.pop()


GF = Frame(True)
TF = Frame(False)
stackframe = StackFrame()
labels = {}
callstack = CallStack()
datastack = DataStack()


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
    if (len(program.attrib) < 1):
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


def checkArgFormat(instruct, numOfArgs):
    cnt = 0
    for arg in instruct:
        cnt += 1
        checkTag(arg, "arg" + str(cnt))
    if cnt != numOfArgs:
        instructOrderNum = int(instruct.attrib.get("order"))
        sys.stderr.write("ERROR 32: instruction number: {} has invalid amount"
                         " of arguments\n".format(instructOrderNum))
        sys.exit(32)


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


def getVarFrame(rawVar):
    possibleFrames = ["GF", "LF", "TF"]
    if len(rawVar) < 4:
        sys.stderr.write("ERROR 32: invalid format of variable \"{}\""
                         "\n".format(rawVar))
        sys.exit(32)
    varFrame = rawVar[:2]
    if varFrame in possibleFrames:
        return varFrame
    else:
        sys.stderr.write("ERROR 32: invalid format of variable \"{}\" (wron"
                         "g frame)\n".format(rawVar))
        sys.exit(32)


def getVarName(rawVar):  # TODO correct name validation
    varFrame = rawVar[2:]
    if varFrame[0] == "@":
        return varFrame[1:]
    else:
        sys.stderr.write("ERROR 32: invalid format of variable \"{}\""
                         "\n".format(rawVar))
        sys.exit(32)


def verifyVar(arg, instructOrderNum):
    if arg.attrib.get("type") != "var":
        sys.stderr.write("ERROR 32: instruction number: {} has wrong argum"
                         "ent type (expected var)\n"
                         .format(instructOrderNum))
        sys.exit(32)
    else:
        getVarFrame(arg.text)
        getVarName(arg.text)


def verifyType(arg, instructOrderNum):
    if arg.attrib.get("type") != "type":
        sys.stderr.write("ERROR 32: instruction number: {} has wrong argum"
                         "ent type (expected type)\n"
                         .format(instructOrderNum))
        sys.exit(32)
    validTypes = ["string", "bool", "int"]
    if arg.text not in validTypes:
        sys.stderr.write("ERROR 32: instruction number: {} has wrong argum"
                         "ent value (expected string|bool|int))\n"
                         .format(instructOrderNum))
        sys.exit(32)


def verifyString(str):  # TODO
    pass


def verifyInt(str):  # TODO
    pass


def verifyBoolean(str):  # TODO
    pass


def strToBool(str):
    if str == "true":
        return True
    else:
        return False


def boolToStr(bool):
    if bool:
        return "true"
    else:
        return "false"


def verifySymb(arg, instructOrderNum):  # DONE
    argType = arg.attrib.get("type")
    if argType == "var":
        getVarFrame(arg.text)
        getVarName(arg.text)
    elif argType == "string":
        verifyString(arg.text)
    elif argType == "int":
        verifyInt(arg.text)
    elif argType == "bool":
        verifyBoolean(arg.text)
    else:
        sys.stderr.write("ERROR 32: instruction number: {} has wrong argum"
                         "ent type (expected var|string|int|bool)\n"
                         .format(instructOrderNum))
        sys.exit(32)


def getVarValue(frame, name):
    if frame == "GF":
        global GF
        if GF.isVarDefined(name):
            if GF.isVarInitialized(name):
                value = GF.getVar(name).value
            else:
                sys.stderr.write("ERROR 56: variable: \"{}\" is defined but"
                                 " unitialized when accessing it's value\n"
                                 .format(name))
                sys.exit(56)
        else:
            sys.stderr.write("ERROR 54: variable: \"{}\" is unitialized\n"
                             .format(name))
            sys.exit(54)
    elif frame == "TF":
        global TF
        if TF.defined:
            if TF.isVarDefined(name):
                if TF.isVarInitialized(name):
                    value = TF.getVar(name).value
                else:
                    sys.stderr.write("ERROR 56: variable: \"{}\" is defined bu"
                                     "t unitialized when accessing it's value"
                                     "\n".format(name))
                    sys.exit(56)
            else:
                sys.stderr.write("ERROR 54: variable: \"{}\" is unitialized\n"
                                 .format(name))
                sys.exit(54)
        else:
            sys.stderr.write("ERROR 54: accessing variable: \"{}\" from"
                             " undefined frame\n".format(name))
            sys.exit(54)
    elif frame == "LF":
        global stackframe
        LF = stackframe.getLF()
        if LF.defined:
            if LF.isVarDefined(name):
                if LF.isVarInitialized(name):
                    value = LF.getVar(name).value
                else:
                    sys.stderr.write("ERROR 56: variable: \"{}\" is defined bu"
                                     "t unitialized when accessing it's value"
                                     "\n".format(name))
                    sys.exit(56)
            else:
                sys.stderr.write("ERROR 54: variable: \"{}\" is unitialized\n"
                                 .format(name))
                sys.exit(54)
        else:
            sys.stderr.write("ERROR 54: accessing variable: \"{}\" from"
                             " undefined frame\n".format(name))
            sys.exit(54)
    else:
        sys.stderr.write("ERROR in getVarValue() that should never occur :/")
        sys.exit(32)
    return value


def getVarType(frame, name):
    if frame == "GF":
        global GF
        if GF.isVarDefined(name):
            if GF.isVarInitialized(name):
                type = GF.getVar(name).type
            else:
                sys.stderr.write("ERROR 56: variable: \"{}\" is defined but"
                                 " unitialized when accessing it's type\n"
                                 .format(name))
                sys.exit(56)
        else:
            sys.stderr.write("ERROR 54: variable: \"{}\" is unitialized\n"
                             .format(name))
            sys.exit(54)
    elif frame == "TF":
        global TF
        if TF.defined:
            if TF.isVarDefined(name):
                if TF.isVarInitialized(name):
                    type = TF.getVar(name).type
                else:
                    sys.stderr.write("ERROR 56: variable: \"{}\" is defined bu"
                                     "t unitialized when accessing it's type"
                                     "\n".format(name))
                    sys.exit(56)
            else:
                sys.stderr.write("ERROR 54: variable: \"{}\" is unitialized\n"
                                 .format(name))
                sys.exit(54)
        else:
            sys.stderr.write("ERROR 54: accessing variable: \"{}\" from"
                             " undefined frame\n".format(name))
            sys.exit(54)
    elif frame == "LF":
        global stackframe
        LF = stackframe.getLF()
        if LF.defined:
            if LF.isVarDefined(name):
                if LF.isVarInitialized(name):
                    type = LF.getVar(name).type
                else:
                    sys.stderr.write("ERROR 56: variable: \"{}\" is defined bu"
                                     "t unitialized when accessing it's type"
                                     "\n".format(name))
                    sys.exit(56)
            else:
                sys.stderr.write("ERROR 54: variable: \"{}\" is unitialized\n"
                                 .format(name))
                sys.exit(54)
        else:
            sys.stderr.write("ERROR 54: accessing variable: \"{}\" from"
                             " undefined frame\n".format(name))
            sys.exit(54)
    else:
        sys.stderr.write("ERROR in getVarValue() that should never occur :/")
        sys.exit(32)
    return type


def setVariable(varFrame, varName, constType, constValue):
    if varFrame == "GF":
        global GF
        newVar = Variable(varName, constType, constValue)
        GF.setVar(newVar)
    elif varFrame == "TF":
        global TF
        if TF.defined:
            newVar = Variable(varName, constType, constValue)
            TF.setVar(newVar)
        else:
            sys.stderr.write("ERROR 54: accessing variable: \"{}\" from"
                             " undefined frame\n".format(varName))
            sys.exit(54)
    elif varFrame == "LF":
        global stackframe
        LF = stackframe.getLF()
        if LF.defined:
            newVar = Variable(varName, constType, constValue)
            LF.setVar(newVar)
        else:
            sys.stderr.write("ERROR 54: accessing variable: \"{}\" from"
                             " undefined frame\n".format(varName))
            sys.exit(54)
    else:
        sys.stderr.write("ERROR in setVarValue() that should never occur :/")
        sys.exit(32)


def getSymbVal(arg):
    arg2Type = arg.attrib.get("type")
    if arg2Type == "var":
        varFrame = getVarFrame(arg.text)
        varName = getVarName(arg.text)
        return getVarValue(varFrame, varName)
    else:
        return arg.text


def getSymbType(arg):
    arg2Type = arg.attrib.get("type")
    if arg2Type == "var":
        varFrame = getVarFrame(arg.text)
        varName = getVarName(arg.text)
        return getVarType(varFrame, varName)
    else:
        return arg2Type


def parseMove(instruction, interpreting):  # DONE
    instructOrderNum = int(instruction.attrib.get("order"))
    if interpreting is False:
        checkArgFormat(instruction, 2)
        verifyVar(instruction[0], instructOrderNum)
        verifySymb(instruction[1], instructOrderNum)
    else:
        arg1 = instruction[0]
        arg2 = instruction[1]
        arg1Frame = getVarFrame(arg1.text)
        arg1Name = getVarName(arg1.text)
        arg2Type = getSymbType(arg2)
        arg2Value = getSymbVal(arg2)
        setVariable(arg1Frame, arg1Name, arg2Type, arg2Value)
        return instructOrderNum+1


def parseCreateframe(instruction, interpreting):  # DONE
    if interpreting is False:
        checkArgFormat(instruction, 0)
    else:
        instructOrderNum = int(instruction.attrib.get("order"))
        global TF
        if TF.defined:
            TF.clear()
            TF.define()
        else:
            TF.define()
        return instructOrderNum+1


def parsePushframe(instruction, interpreting):  # DONE
    if interpreting is False:
        checkArgFormat(instruction, 0)
    else:
        instructOrderNum = int(instruction.attrib.get("order"))
        global TF
        global stackframe
        stackframe.push(TF)
        TF.clear()
        return instructOrderNum+1


def parsePopframe(instruction, interpreting):  # DONE
    if interpreting is False:
        checkArgFormat(instruction, 0)
    else:
        instructOrderNum = int(instruction.attrib.get("order"))
        global TF
        global stackframe
        TF = stackframe.pop()
        return instructOrderNum+1


def parseDefvar(instruction, interpreting):  # DONE
    instructOrderNum = int(instruction.attrib.get("order"))
    if interpreting is False:
        checkArgFormat(instruction, 1)
        verifyVar(instruction[0], instructOrderNum)

    if interpreting is True:
        arg1 = instruction[0]
        varFrame = getVarFrame(arg1.text)
        varName = getVarName(arg1.text)
        if varFrame == "GF":
            global GF
            GF.defVar(varName)
        if varFrame == "LF":
            global stackframe
            LF = stackframe.getLF()
            LF.defVar(varName)
        if varFrame == "TF":
            global TF
            TF.defVar(varName)
        return instructOrderNum+1


def parseCall(instruction, interpreting):  # DONE
    instructOrderNum = int(instruction.attrib.get("order"))
    if interpreting is False:
        checkArgFormat(instruction, 1)
        arg1 = instruction[0]
        if arg1.attrib.get(type) == "label":
            label = arg1.text
            if len(label) < 1:
                sys.stderr.write("ERROR 32: instruction number: {} has in"
                                 "valid label name\n"
                                 .format(instructOrderNum))
                sys.exit(32)
            else:
                if label in labels:
                    pass
                else:
                    sys.stderr.write("ERROR 52: label: \"{}\" doesn't exist"
                                     "\n".format(label))
                    sys.exit(52)
        else:
            sys.stderr.write("ERROR 32: instruction number: {} has wrong:"
                             " argument type (expected label)\n"
                             .format(instructOrderNum))
            sys.exit(32)
    else:
        global labels
        global callstack
        callstack.push(instructOrderNum)
        label = instruction[0].text
        return labels[label]


def parseReturn(instruction, interpreting):  # DONE
    if interpreting is False:
        checkArgFormat(instruction, 0)
    else:
        global callstack
        return callstack.pop()


def parsePushs(instruction, interpreting):  # DONE
    instructOrderNum = int(instruction.attrib.get("order"))
    if interpreting is False:
        checkArgFormat(instruction, 1)
        verifySymb(instruction[0], instructOrderNum)
    else:
        arg = instruction[0]
        argType = getSymbType(arg)
        argValue = getSymbVal(arg)
        newStackVar = Variable("stackVar", argType, argValue)
        global datastack
        datastack.push(newStackVar)
        return instructOrderNum+1


def parsePops(instruction, interpreting):  # DONE
    instructOrderNum = int(instruction.attrib.get("order"))
    if interpreting is False:
        checkArgFormat(instruction, 1)
        verifySymb(instruction[0], instructOrderNum)
    else:
        global datastack
        stackVar = datastack.pop()
        arg = instruction[0]
        argFrame = getVarFrame(arg.text)
        argName = getVarName(arg.text)
        setVariable(argFrame, argName, stackVar.type, stackVar.value)
        return instructOrderNum+1


def parseAdd(instruction, interpreting):  # DONE
    instructOrderNum = int(instruction.attrib.get("order"))
    if interpreting is False:
        checkArgFormat(instruction, 3)
        verifyVar(instruction[0], instructOrderNum)
        verifySymb(instruction[1], instructOrderNum)
        verifySymb(instruction[2], instructOrderNum)
    else:
        arg1 = instruction[0]
        arg2 = instruction[1]
        arg3 = instruction[2]
        arg1Frame = getVarFrame(arg1.text)
        arg1Name = getVarName(arg1.text)
        arg2Type = getSymbType(arg2)
        arg2Value = getSymbVal(arg2)
        arg3Type = getSymbType(arg3)
        arg3Value = getSymbVal(arg3)
        if arg2Type == "int" and arg2Type == arg3Type:
            result = arg2Value + arg3Value
            setVariable(arg1Frame, arg1Name, arg2Type, result)
        else:
            sys.stderr.write("ERROR 53: invalid operand types in instruction n"
                             "umber: {} (both operands must be integers)"
                             .format(instructOrderNum))
            sys.exit(53)
        return instructOrderNum+1


def parseSub(instruction, interpreting):
    instructOrderNum = int(instruction.attrib.get("order"))
    if interpreting is False:
        checkArgFormat(instruction, 3)
        verifyVar(instruction[0], instructOrderNum)
        verifySymb(instruction[1], instructOrderNum)
        verifySymb(instruction[2], instructOrderNum)
    else:
        arg1 = instruction[0]
        arg2 = instruction[1]
        arg3 = instruction[2]
        arg1Frame = getVarFrame(arg1.text)
        arg1Name = getVarName(arg1.text)
        arg2Type = getSymbType(arg2)
        arg2Value = getSymbVal(arg2)
        arg3Type = getSymbType(arg3)
        arg3Value = getSymbVal(arg3)
        if arg2Type == "int" and arg2Type == arg3Type:
            result = arg2Value - arg3Value
            setVariable(arg1Frame, arg1Name, arg2Type, result)
        else:
            sys.stderr.write("ERROR 53: invalid operand types in instruction n"
                             "umber: {} (both operands must be integers)"
                             .format(instructOrderNum))
            sys.exit(53)
        return instructOrderNum+1


def parseMul(instruction, interpreting):
    instructOrderNum = int(instruction.attrib.get("order"))
    if interpreting is False:
        checkArgFormat(instruction, 3)
        verifyVar(instruction[0], instructOrderNum)
        verifySymb(instruction[1], instructOrderNum)
        verifySymb(instruction[2], instructOrderNum)
    else:
        arg1 = instruction[0]
        arg2 = instruction[1]
        arg3 = instruction[2]
        arg1Frame = getVarFrame(arg1.text)
        arg1Name = getVarName(arg1.text)
        arg2Type = getSymbType(arg2)
        arg2Value = getSymbVal(arg2)
        arg3Type = getSymbType(arg3)
        arg3Value = getSymbVal(arg3)
        if arg2Type == "int" and arg2Type == arg3Type:
            result = arg2Value * arg3Value
            setVariable(arg1Frame, arg1Name, arg2Type, result)
        else:
            sys.stderr.write("ERROR 53: invalid operand types in instruction n"
                             "umber: {} (both operands must be integers)"
                             .format(instructOrderNum))
            sys.exit(53)
        return instructOrderNum+1


def parseIdiv(instruction, interpreting):
    instructOrderNum = int(instruction.attrib.get("order"))
    if interpreting is False:
        checkArgFormat(instruction, 3)
        verifyVar(instruction[0], instructOrderNum)
        verifySymb(instruction[1], instructOrderNum)
        verifySymb(instruction[2], instructOrderNum)
    else:
        arg1 = instruction[0]
        arg2 = instruction[1]
        arg3 = instruction[2]
        arg1Frame = getVarFrame(arg1.text)
        arg1Name = getVarName(arg1.text)
        arg2Type = getSymbType(arg2)
        arg2Value = getSymbVal(arg2)
        arg3Type = getSymbType(arg3)
        arg3Value = getSymbVal(arg3)
        if arg2Type == "int" and arg2Type == arg3Type:
            if arg3Value == 0:
                sys.stderr.write("ERROR 57: division by zero in instruction n"
                                 "umber: {}"
                                 .format(instructOrderNum))
                sys.exit(57)
            result = arg2Value // arg3Value
            setVariable(arg1Frame, arg1Name, arg2Type, result)
        else:
            sys.stderr.write("ERROR 53: invalid operand types in instruction n"
                             "umber: {} (both operands must be integers)"
                             .format(instructOrderNum))
            sys.exit(53)
        return instructOrderNum+1


def parseLt(instruction, interpreting):
    instructOrderNum = int(instruction.attrib.get("order"))
    if interpreting is False:
        checkArgFormat(instruction, 3)
        verifyVar(instruction[0], instructOrderNum)
        verifySymb(instruction[1], instructOrderNum)
        verifySymb(instruction[2], instructOrderNum)
    else:
        arg1 = instruction[0]
        arg2 = instruction[1]
        arg3 = instruction[2]
        arg1Frame = getVarFrame(arg1.text)
        arg1Name = getVarName(arg1.text)
        arg2Type = getSymbType(arg2)
        arg2Value = getSymbVal(arg2)
        arg3Type = getSymbType(arg3)
        arg3Value = getSymbVal(arg3)
        if arg2Type == arg3Type:
            result = arg2Value < arg3Value
            setVariable(arg1Frame, arg1Name, "bool", boolToStr(result))
        else:
            sys.stderr.write("ERROR 53: invalid operand types in instruction n"
                             "umber: {} (both operands must have same type)"
                             .format(instructOrderNum))
            sys.exit(53)
        return instructOrderNum+1


def parseGt(instruction, interpreting):
    instructOrderNum = int(instruction.attrib.get("order"))
    if interpreting is False:
        checkArgFormat(instruction, 3)
        verifyVar(instruction[0], instructOrderNum)
        verifySymb(instruction[1], instructOrderNum)
        verifySymb(instruction[2], instructOrderNum)
    else:
        arg1 = instruction[0]
        arg2 = instruction[1]
        arg3 = instruction[2]
        arg1Frame = getVarFrame(arg1.text)
        arg1Name = getVarName(arg1.text)
        arg2Type = getSymbType(arg2)
        arg2Value = getSymbVal(arg2)
        arg3Type = getSymbType(arg3)
        arg3Value = getSymbVal(arg3)
        if arg2Type == arg3Type:
            result = arg2Value < arg3Value
            setVariable(arg1Frame, arg1Name, "bool", boolToStr(result))
        else:
            sys.stderr.write("ERROR 53: invalid operand types in instruction n"
                             "umber: {} (both operands must have same type)"
                             .format(instructOrderNum))
            sys.exit(53)
        return instructOrderNum+1


def parseEq(instruction, interpreting):
    instructOrderNum = int(instruction.attrib.get("order"))
    if interpreting is False:
        checkArgFormat(instruction, 3)
        verifyVar(instruction[0], instructOrderNum)
        verifySymb(instruction[1], instructOrderNum)
        verifySymb(instruction[2], instructOrderNum)
    else:
        arg1 = instruction[0]
        arg2 = instruction[1]
        arg3 = instruction[2]
        arg1Frame = getVarFrame(arg1.text)
        arg1Name = getVarName(arg1.text)
        arg2Type = getSymbType(arg2)
        arg2Value = getSymbVal(arg2)
        arg3Type = getSymbType(arg3)
        arg3Value = getSymbVal(arg3)
        if arg2Type == arg3Type:
            result = arg2Value == arg3Value
            setVariable(arg1Frame, arg1Name, "bool", boolToStr(result))
        else:
            sys.stderr.write("ERROR 53: invalid operand types in instruction n"
                             "umber: {} (both operands must have same type)"
                             .format(instructOrderNum))
            sys.exit(53)
        return instructOrderNum+1


def parseAnd(instruction, interpreting):
    instructOrderNum = int(instruction.attrib.get("order"))
    if interpreting is False:
        checkArgFormat(instruction, 3)
        verifyVar(instruction[0], instructOrderNum)
        verifySymb(instruction[1], instructOrderNum)
        verifySymb(instruction[2], instructOrderNum)
    else:
        arg1 = instruction[0]
        arg2 = instruction[1]
        arg3 = instruction[2]
        arg1Frame = getVarFrame(arg1.text)
        arg1Name = getVarName(arg1.text)
        arg2Type = getSymbType(arg2)
        arg2Value = getSymbVal(arg2)
        arg3Type = getSymbType(arg3)
        arg3Value = getSymbVal(arg3)
        if arg2Type == "bool" and arg2Type == arg3Type:
            result = strToBool(arg2Value) and strToBool(arg3Value)
            setVariable(arg1Frame, arg1Name, "bool", boolToStr(result))
        else:
            sys.stderr.write("ERROR 53: invalid operand types in instruction n"
                             "umber: {} (both operands must be bool)"
                             .format(instructOrderNum))
            sys.exit(53)
        return instructOrderNum+1


def parseOr(instruction, interpreting):
    instructOrderNum = int(instruction.attrib.get("order"))
    if interpreting is False:
        checkArgFormat(instruction, 3)
        verifyVar(instruction[0], instructOrderNum)
        verifySymb(instruction[1], instructOrderNum)
        verifySymb(instruction[2], instructOrderNum)
    else:
        arg1 = instruction[0]
        arg2 = instruction[1]
        arg3 = instruction[2]
        arg1Frame = getVarFrame(arg1.text)
        arg1Name = getVarName(arg1.text)
        arg2Type = getSymbType(arg2)
        arg2Value = getSymbVal(arg2)
        arg3Type = getSymbType(arg3)
        arg3Value = getSymbVal(arg3)
        if arg2Type == "bool" and arg2Type == arg3Type:
            result = strToBool(arg2Value) or strToBool(arg3Value)
            setVariable(arg1Frame, arg1Name, "bool", boolToStr(result))
        else:
            sys.stderr.write("ERROR 53: invalid operand types in instruction n"
                             "umber: {} (both operands must be bool)"
                             .format(instructOrderNum))
            sys.exit(53)
        return instructOrderNum+1


def parseNot(instruction, interpreting):
    instructOrderNum = int(instruction.attrib.get("order"))
    if interpreting is False:
        checkArgFormat(instruction, 2)
        verifyVar(instruction[0], instructOrderNum)
        verifySymb(instruction[1], instructOrderNum)
    else:
        arg1 = instruction[0]
        arg2 = instruction[1]
        arg1Frame = getVarFrame(arg1.text)
        arg1Name = getVarName(arg1.text)
        arg2Type = getSymbType(arg2)
        arg2Value = getSymbVal(arg2)
        if arg2Type == "bool":
            result = not strToBool(arg2Value)
            setVariable(arg1Frame, arg1Name, "bool", boolToStr(result))
        else:
            sys.stderr.write("ERROR 53: invalid operand type in instruction n"
                             "umber: {} (operand must be bool)"
                             .format(instructOrderNum))
            sys.exit(53)
        return instructOrderNum+1


def parseInt2char(instruction, interpreting):
    instructOrderNum = int(instruction.attrib.get("order"))
    if interpreting is False:
        checkArgFormat(instruction, 2)
        verifyVar(instruction[0], instructOrderNum)
        verifySymb(instruction[1], instructOrderNum)
    else:
        arg1 = instruction[0]
        arg2 = instruction[1]
        arg1Frame = getVarFrame(arg1.text)
        arg1Name = getVarName(arg1.text)
        arg2Type = getSymbType(arg2)
        arg2Value = getSymbVal(arg2)
        if arg2Type == "int":
            try:
                character = chr(arg2Value)
            except ValueError:
                sys.stderr.write("ERROR 58: invalid UNICODE value in operation"
                                 " number: {}" .format(instructOrderNum))
                sys.exit(58)
            setVariable(arg1Frame, arg1Name, "string", str(character))
        else:
            sys.stderr.write("ERROR 53: invalid operand type in instruction n"
                             "umber: {} (operand must be int)"
                             .format(instructOrderNum))
            sys.exit(53)
        return instructOrderNum+1


def parseStri2int(instruction, interpreting):
    instructOrderNum = int(instruction.attrib.get("order"))
    if interpreting is False:
        checkArgFormat(instruction, 3)
        verifyVar(instruction[0], instructOrderNum)
        verifySymb(instruction[1], instructOrderNum)
        verifySymb(instruction[2], instructOrderNum)
    else:
        arg1 = instruction[0]
        arg2 = instruction[1]
        arg3 = instruction[2]
        arg1Frame = getVarFrame(arg1.text)
        arg1Name = getVarName(arg1.text)
        arg2Type = getSymbType(arg2)
        arg2Value = getSymbVal(arg2)
        arg3Type = getSymbType(arg3)
        arg3Value = getSymbVal(arg3)
        if arg2Type == "string" and arg3Type == "int":
            try:
                ordCharValue = ord(arg2Value[arg3Value])
            except IndexError:
                sys.stderr.write("ERROR 58: indexing out of string in instruct"
                                 "ion number: {}"
                                 .format(instructOrderNum))
                sys.exit(58)
            setVariable(arg1Frame, arg1Name, "int", ordCharValue)
        else:
            sys.stderr.write("ERROR 53: invalid operand types in instruction n"
                             "umber: {} (symb1 = string, symb2 = int)"
                             .format(instructOrderNum))
            sys.exit(53)
        return instructOrderNum+1


def parseRead(instruction, interpreting):
    instructOrderNum = int(instruction.attrib.get("order"))
    if interpreting is False:
        checkArgFormat(instruction, 2)
        verifyVar(instruction[0], instructOrderNum)
        verifyType(instruction[1], instructOrderNum)
    else:
        arg1 = instruction[0]
        arg2 = instruction[1]
        arg1Frame = getVarFrame(arg1.text)
        arg1Name = getVarName(arg1.text)
        type = arg2.text
        if type == "int":
            input = input()
            try:
                value = int(input)
            except Exception:
                value = 0
            setVariable(arg1Frame, arg1Name, "int", value)
        if type == "bool":
            input = input()
            if input.lower() == "true":
                setVariable(arg1Frame, arg1Name, "bool", "true")
            else:
                setVariable(arg1Frame, arg1Name, "bool", "false")
        if type == "string":
            input = input()
            setVariable(arg1Frame, arg1Name, "string", input)
        return instructOrderNum+1


def parseWrite(instruction, interpreting):
    instructOrderNum = int(instruction.attrib.get("order"))
    if interpreting is False:
        checkArgFormat(instruction, 1)
        verifySymb(instruction[0], instructOrderNum)
    else:
        arg1 = instruction[0]
        arg1Value = getSymbVal(arg1)
        print(arg1Value)
        return instructOrderNum+1


def parseConcat(instruction, interpreting):
    instructOrderNum = int(instruction.attrib.get("order"))
    print(instruction.attrib)
    return instructOrderNum+1


def parseStrlen(instruction, interpreting):
    instructOrderNum = int(instruction.attrib.get("order"))
    print(instruction.attrib)
    return instructOrderNum+1


def parseGetchar(instruction, interpreting):
    instructOrderNum = int(instruction.attrib.get("order"))
    print(instruction.attrib)
    return instructOrderNum+1


def parseSetchar(instruction, interpreting):
    instructOrderNum = int(instruction.attrib.get("order"))
    print(instruction.attrib)
    return instructOrderNum+1


def parseType(instruction, interpreting):
    instructOrderNum = int(instruction.attrib.get("order"))
    print(instruction.attrib)
    return instructOrderNum+1


def parseLabel(instruction, interpreting):
    instructOrderNum = int(instruction.attrib.get("order"))
    print(instruction.attrib)
    return instructOrderNum+1


def parseJump(instruction, interpreting):
    instructOrderNum = int(instruction.attrib.get("order"))
    print(instruction.attrib)
    return instructOrderNum+1


def parseJumpifeq(instruction, interpreting):
    instructOrderNum = int(instruction.attrib.get("order"))
    print(instruction.attrib)
    return instructOrderNum+1


def parseJumpifneq(instruction, interpreting):
    instructOrderNum = int(instruction.attrib.get("order"))
    print(instruction.attrib)
    return instructOrderNum+1


def parseDprint(instruction, interpreting):
    instructOrderNum = int(instruction.attrib.get("order"))
    print(instruction.attrib)
    return instructOrderNum+1


def parseBreak(instruction, interpreting):
    instructOrderNum = int(instruction.attrib.get("order"))
    print(instruction.attrib)
    return instructOrderNum+1


def loadLabels(program):
    global labels
    for instruction in program:
        instructOrderNum = instruction.attrib.get("order")
        opcode = instruction.attrib.get("opcode")
        if opcode == "LABEL":
            checkArgFormat(instruction, 1)
            arg1 = instruction[0]
            if arg1.attrib.get(type) == "label":
                label = arg1.text
                if len(label) < 1:
                    sys.stderr.write("ERROR 32: instruction number: {} has in"
                                     "valid label name\n"
                                     .format(instructOrderNum))
                    sys.exit(32)
                else:
                    if label in labels:
                        sys.stderr.write("ERROR 52: label: \"{}\" is already d"
                                         "efined\n".format(label))
                        sys.exit(52)
                    else:
                        labels[label] = instructOrderNum
            else:
                sys.stderr.write("ERROR 32: instruction number: {} has wrong:"
                                 " argument type (expected label)\n"
                                 .format(instructOrderNum))
                sys.exit(32)


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


def verifyInstruct(instruct):
    opcode = instruct.attrib.get("opcode")
    if opcode in opcodeParser:
        opcodeParser[opcode](instruct, False)
    else:
        sys.stderr.write("ERROR 32: Unknown opcode \"{}\"\n".format(opcode))
        sys.exit(32)


def interpretInstruction(instruction):
    opcode = instruction.attrib.get("opcode")
    return opcodeParser[opcode](instruction, True)


def main():
    args = argumentsHadling()  # parsing of argiments
    fileName = ''.join(args.source)
    file = openFile(fileName)  # open file
    program = parseFile(file).getroot()  # get root from XML file

    checkProgramFormatting(program)  # check valid tags/args of prog and instr.

    loadLabels(program)

    # pre-runtime verification of program
    for instruct in program:
        verifyInstruct(instruct)

    # interpretation
    nextInstructionNumber = 1  # start with first instruction
    instruction = lookUpInstuct(nextInstructionNumber, program)
    while (instruction is not None):
        nextInstructionNumber = interpretInstruction(instruction)
        instruction = lookUpInstuct(nextInstructionNumber, program)


if __name__ == '__main__':
    main()
