
class Serial():
    buf = []
    timeout = 100
    def write(self, byte):
        Serial.buf.append(byte)

    def readline(self):
        line = ""
        if len(Serial.buf) > 0:
            element = Serial.buf.pop(0)
            tries = 0
            while element != '\n' and element != '\r' and tries >= Serial.timeout:
                line += element
                element = Serial.buf.pop(0)
                tries += 1
        return line + '\r'
