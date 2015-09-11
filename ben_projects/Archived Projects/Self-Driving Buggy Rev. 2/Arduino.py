import serial
import time
import os
from sys import platform as _platform

def findAll(inputList, input):
    return [index for index, element in enumerate(inputList) if element == input]


class Arduino(object):
    maxCommand = 2 ** 16

    def __init__(self, address=None, baud=115200, timeout=0.1, disabled=False, boardTag='uno', forceUpload=False,
                 **commands):
        self.address = address
        self.baud = baud
        self.timeout = timeout
        self.disabled = disabled
        self.boardTag = boardTag

        self.commands = {}
        for (commandName, reservation) in commands.iteritems():
            self.addCommand(commandName, reservation)

        self.commandHistory = {}
        for command in self.commands.keys():
            self.commandHistory[command] = None

        if self.disabled == False:
            self._initializeSerial(address, baud, timeout)
            if self.address is not None:
                self._updateAndUploadINO(forceUpload)
            time.sleep(1)

    def _initializeSerial(self, address, baud, timeout):
        if address is None:
            for possibleAddress in Arduino._possibleAddresses():
                try:
                    self.serialReference = serial.Serial(possibleAddress, baud, timeout=timeout)
                    self.address = possibleAddress
                except:
                    pass
            if self.address is None:
                raise Exception("No Arduinos could be found! Did you plug it in? Try entering the address manually.")
        else:
            self.serialReference = serial.Serial(address, baud, timeout=timeout)

    @staticmethod
    def _possibleAddresses():
        if _platform == "darwin":  # OS X
            devices = os.listdir("/dev/")
            arduinoDevices = []
            for device in devices:
                if device.find("cu.usbmodem") > -1:
                    arduinoDevices.append("/dev/" + device)
            return arduinoDevices
        elif _platform == "linux" or _platform == "linux2":  # linux
            return []
        elif _platform == "win32":  # Windows
            return []

    def __getitem__(self, item):
        reservation = self.commands[item]
        if len(reservation) == 3:  # a writable object
            return self.commandHistory[item]
        elif len(reservation) == 2:  # a readable object
            self._sendCommand(item, reservation[0])
            return self._readSerial()

    def __setitem__(self, key, value):
        self._sendCommand(key, value)

    def disableArduino(self):
        self.disabled = False
        self.serialReference = None

    def enableArduino(self):
        self.disabled = True
        self._initializeSerial(self.address, self.baud, self.timeout)

    def addCommand(self, name, reservation):
        commandMin = 0
        if reservation is not None:
            commandLength = reservation[1] - reservation[0]
        else:
            commandLength = 1
        numUnreserved = 0

        for index in xrange(Arduino.maxCommand):
            if (commandMin + commandLength) > Arduino.maxCommand:
                raise Exception("Out of commands! An impressive feat! Max number is " + str(Arduino.maxCommand))
            if self._isCommandReserved(index) == False:
                numUnreserved += 1
            else:
                numUnreserved = 0
                commandMin = index + 1

            if numUnreserved == commandLength:
                if reservation is not None:
                    self.commands[name] = (commandMin, commandLength + commandMin, reservation)
                else:
                    self.commands[name] = (commandMin, reservation)
                break

    def _isCommandReserved(self, commandNumber):
        for (commandName, reservation) in self.commands.iteritems():
            if len(reservation) == 3:  # a writable object
                if reservation[0] <= commandNumber <= reservation[1]:
                    return True
            elif len(reservation) == 2:  # a readable object
                if commandNumber == reservation[0]:
                    return True
        return False

    def _updateAndUploadINO(self, forceUpload):
        with open("Board/src/Controller.ino", "r") as inoFile:
            arduinoCode = inoFile.read()
        # these flags indicate where in the ino file to write the appropriate code
        dataConditionalsStartFlag = "// ----- data conditionals start -----"
        dataConditionalsEndFlag = "// -----  data conditionals end  -----"
        functionsStartFlag = "// ----- functions start -----"
        functionsEndFlag = "// -----  functions end  -----"

        # find the indices of the flags in the file
        dataConditionalsStart = arduinoCode.find(dataConditionalsStartFlag)
        dataConditionalsEnd = arduinoCode.find(dataConditionalsEndFlag)
        functionsStart = arduinoCode.find(functionsStartFlag)
        functionsEnd = arduinoCode.find(functionsEndFlag)

        # make no changes to everything before dataConditionalsStart including the flag itself
        outputCode = arduinoCode[:(dataConditionalsStart + len(dataConditionalsStartFlag) + 1)] + "\n"

        # find how many tabs the block we're currently in has
        tabSpaces = ''
        for line in arduinoCode.split("\n"):
            if dataConditionalsStartFlag in line:
                whiteSpaceEnd = line.find(dataConditionalsStartFlag)
                tabSpaces = line[:whiteSpaceEnd]

        # based on the input commands, generate the conditionals code and add it to the output
        outputCode += self._generateDataConditionalsCode(tabSpaces) + "\n" + tabSpaces + dataConditionalsEndFlag

        # make no changes between dataConditionalsEnd and functionsStart including the flag itself
        outputCode += arduinoCode[(dataConditionalsEnd + len(dataConditionalsEndFlag)): (
            functionsStart + len(functionsStartFlag) + 1)] + "\n"

        # recover lines that were in the original code blocks
        functionStubLines = arduinoCode[functionsStart:functionsEnd + len(functionsEndFlag) + 1].split("\n")
        linesToKeep = []
        for start, end in zip(findAll(functionStubLines, "{"), findAll(functionStubLines, "}")):
            linesToKeep.append(functionStubLines[start + 1:end])
        linesToKeep.append('')  # if there are more blocks than lines to keep, use the empty string

        outputCode += self._generateFunctionsCode(linesToKeep)
        outputCode += "\n" + functionsEndFlag

        with open("Board/backup.ino", "r") as inoFile:
            initialCode = inoFile.read()

        if arduinoCode != outputCode or initialCode != outputCode or forceUpload is True:
            print "\nArduino ino file updated! Uploading file to Arduino board. (address: " + str(self.address) + ")"
            print "\nLines changed:"
            lineNum = 1
            for lineOrig, lineNew in zip(arduinoCode.split("\n"), outputCode.split("\n")):
                if lineOrig != lineNew:
                    print "\t" + str(lineNum) + ": '" + lineOrig.strip() + "' ----> '" + lineNew.strip() + "'"
                lineNum += 1

            with open("Board/src/Controller.ino", "w") as inoFile:
                inoFile.write(outputCode)
            with open("Board/backup.ino", "w") as inoFile:
                inoFile.write(outputCode)
            os.system("cd Board && platformio run --target upload && cd ..")
            print("\n\nUpload complete. Please restart the program.")
            quit()

    def _generateFunctionsCode(self, linesToKeep):
        index = 0
        outputCode = ""
        for commandName in sorted(self.commands.keys()):
            if len(self.commands[commandName]) == 3:  # writable object
                functionTag = "void set_"
            else:
                functionTag = "unsigned int get_"
            outputCode += functionTag + commandName + "(int input)\n{\n"

            if len(linesToKeep) > 0:
                for line in linesToKeep[index]:
                    outputCode += line + "\n"
            else:
                outputCode += "return 0;\n"
            outputCode += "}\n"
            index += 1
            if index >= len(linesToKeep):
                index = len(linesToKeep) - 1
        return outputCode

    def _generateDataConditionalsCode(self, tabSpaces=""):
        dataConditionalsCode = ""
        for (commandName, reservation) in self.commands.iteritems():
            if dataConditionalsCode == "":
                dataConditionalsCode += tabSpaces + "if "
            else:
                dataConditionalsCode += tabSpaces + "else if "

            if len(reservation) == 3:  # writable object
                dataConditionalsCode += "(" + str(reservation[0]) + " <= data && data <= " + str(
                    reservation[1]) + ") {\n"  # example: if (0 <= data && data <= 100) {

                functionTag = "    set_"

                if reservation[0] > 0:
                    dataConditionalsCode += tabSpaces + functionTag + commandName + "(data - " + \
                                            str(reservation[0]) + ");\n" + tabSpaces + "}\n"
                    # example:    set_servo(data - 100);
                else:
                    dataConditionalsCode += tabSpaces + functionTag + commandName + "(data);\n" + tabSpaces + "}\n"
                    # example:    set_servo(data);

            else:  # readable object:
                dataConditionalsCode += "(data == " + str(reservation[0]) + ") {\n"
                # example: if (data == 50) {

                functionTag = "    sendData(get_"

                if reservation[0] > 0:
                    dataConditionalsCode += tabSpaces + functionTag + commandName + "(data - " + \
                                            str(reservation[0]) + ");\n" + tabSpaces + "}\n"
                    # example:    Serial.println(set_servo(data - 100));
                else:
                    dataConditionalsCode += tabSpaces + functionTag + commandName + "(data));\n" + tabSpaces + "}\n"
                    # example:    Serial.println(set_servo(data));



        return dataConditionalsCode

    @staticmethod
    def _decimalToChar(commandNumber):
        upperByte = commandNumber / 0x100
        lowerByte = commandNumber % 0x100
        return chr(upperByte) + chr(lowerByte)

    def _sendCommand(self, name, command):
        if self.disabled == False:
            reservation = self.commands[name]
            if len(reservation) == 3:  # writable object
                commandRange = reservation[2]
                if commandRange[0] <= command <= commandRange[1]:
                    # the command's minimum value
                    absoluteMinValue = reservation[0]
    
                    # if "command" has a range that is negative, this adjusts it to the positive range
                    relativeMinValue = abs(reservation[2][0])
    
                    adjustedCommand = command + absoluteMinValue + relativeMinValue
                    self.serialReference.write(Arduino._decimalToChar(adjustedCommand))
                else:
                    raise Exception("Command out of range! " + str(command) + ", " + name + " has a range of " +
                                    str(commandRange[0]) + "..." + str(commandRange[1]) + " inclusive")
            else:  # readable object
                self.serialReference.write(Arduino._decimalToChar(command + reservation[0]))
            self.commandHistory[name] = command

    def _readSerial(self):
        if self.disabled == False:
            lowerData = self.serialReference.read()
            upperData = self.serialReference.read()

            if len(upperData) == 0:
                upperData = 0
            else:
                upperData = ord(upperData)

            if len(lowerData) == 0:
                lowerData = 0
            else:
                lowerData = ord(lowerData)
            data = upperData * 0x100 + lowerData
            if data:
                return data

    def __str__(self):
        return str(self.commands)
