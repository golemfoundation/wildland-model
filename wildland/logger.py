from blessings import Terminal

class Logger:
    
    t = Terminal()

    def __init__ (self, name="", nest_level = 0, icon="", color=Terminal().dim):
        self.name = str(name)
        self.color = color
        self.icon = icon

    def log (self, message, icon=" "):
        t = Terminal()
        print ("[{icon}]{name} {message}{c}".format(
            icon=f"{t.yellow}{icon}{t.normal}",
            name= f" {self.color}{self.name}{t.normal}:" \
                    if self.name is not "" else "",
            message=message,
            c=t.normal))
