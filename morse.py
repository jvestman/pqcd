class Morse:

    morse = {
            ".-": "A",
            "-...": "B",
            "-.-.": "C",
            "-..": "D",
            ".": "E",
            "..-.": "F",
            "--.": "G",
            "....": "H",
            "..": "I",
            ".---": "J",
            "-.-": "K",
            ".-..": "L",
            "--": "M",
            "-.": "N",
            "---": "O",
            ".--.": "P",
            "--.-": "Q",
            ".-.": "R",
            "...": "S",
            "-": "T",
            "..-": "U",
            "...-": "V",
            ".--": "W",
            "-..-": "X",
            "-.--": "Y",
            "--..": "Z",
            "-----": "0",
            ".----": "1",
            "..---": "2",
            "...--": "3",
            "....-": "4",
            ".....": "5",
            "-....": "6",
            "--...": "7",
            "---..": "8",
            "----.": "9",
            ".-.-.-": ".",
            "..--..": "?",
            "-..-.": "/"
    }

    def __init__(self, bins, value_threshold, dit_threshold, dat_threshold, break_threshold):
        self.value_threshold = value_threshold
        self.dit_threshold = dit_threshold
        self.dat_threshold = dat_threshold
        self.break_threshold = break_threshold
        self.statuses = [0] * int(bins)
        self.codes = [""] * int(bins)
        self.listeners = []
        self.space_threshold = 20
        self.char_count = [0] * int(bins)

    def add_listener(self, listener):
        self.listeners.append(listener)

    def decode_morse(self, y, value):
        if value > self.value_threshold:
            if self.statuses[y] < 0:
                self.statuses[y] = 0
            self.statuses[y] = self.statuses[y] + 1
            self.char_count[y] += 1
        elif self.statuses[y] > self.dat_threshold:
            width = self.statuses[y]
            self.statuses[y] = 0
            self.codes[y] += '-'
            self.char_count[y] += 1
            for listener in self.listeners:
                listener.dat(y, width)
        elif self.statuses[y] > self.dit_threshold:
            width = self.statuses[y]
            self.statuses[y] = 0
            self.codes[y] += "."
            self.char_count[y] += 1
            for listener in self.listeners:
                listener.dit(y, width)
        elif self.statuses[y] == self.break_threshold:
            self.statuses[y] = self.statuses[y] - 1
            if self.codes[y] in self.morse:
                character = self.morse[self.codes[y]]
                if character:
                    for listener in self.listeners:
                        listener.character(y, character)
            else:
                for listener in self.listeners:
                    listener.unrecognized(y, self.char_count[y])
                print("Unrecognized code: \"" + self.codes[y] + "\"" + str(self.statuses[y]))
            self.codes[y] = ""
            self.char_count[y] = 0

        else:
            self.statuses[y] = self.statuses[y] - 1
            if self.codes[y] != "":
                self.char_count[y] += 1
            if self.statuses[y] == -self.space_threshold:
                for listener in self.listeners:
                    listener.character(y, ' ')
