class Logger:

    def __init__ (self, name="", nest_level = 0):
        self.name = str(name)
        self.nest_level = nest_level

    def nest_up(self):
        self.nest_level+= 1

    def nest_down(self):
        self.nest_level-= 1
        assert self.nest_level >= 0

    def log (self, message, icon=" "):
        level = self.nest_level
        print ("[{icon}]{name}{space}{pad}{arrow} {message}".format(
            icon=icon,
            name= f" {self.name}: " if self.name is not "" else "",
            space=" " if level > 0 else "",
            pad="".ljust(level,'-'),
            arrow=">" if level > 0 else "",
            message=message))
