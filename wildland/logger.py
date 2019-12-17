from blessings import Terminal

class Logger:
    
    t = Terminal()

    def __init__ (self, name="", nest_level = 0, icon="", color=Terminal().dim):
        self.name = str(name)
        self.color = color
        self.icon = icon

    def log (self, message, icon=" ", msg_color=Terminal().normal):
        t = Terminal()
        print ("[{icon}]{name} {message}".format(
            icon=f"{t.yellow}{icon}{t.normal}",
            name= f" {self.color}{self.name}{t.normal}:" \
                    if self.name is not "" else "",
            message=f"{msg_color}{message}{t.normal}"))
