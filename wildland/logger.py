from blessings import Terminal

class Logger:
    
    t = Terminal()

    def __init__ (self, name="", nest_level = 0, color=""):
        self.name = str(name)
        self.nest_level = nest_level
        self.color = color

    def nest_up(self):
        self.nest_level+= 1

    def nest_down(self):
        self.nest_level-= 1
        assert self.nest_level >= 0

    def log (self, message, icon=" "):
        level = self.nest_level
        t = Logger.t
        print ("[{icon}]{name}{space}{pad}{arrow} {message}".format(
            icon=f"{t.green}{icon}{t.normal}",
            name= f" {t.dim}{self.name}{t.normal}: " \
                    if self.name is not "" else "",
            space=" " if level > 0 else "",
            pad="".ljust(level,'-'),
            arrow=">" if level > 0 else "",
            message=self.color + message + t.normal))
