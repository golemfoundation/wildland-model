class Logger:
    log_ident = 0

    def nest_up():
        Logger.log_ident+= 1

    def nest_down():
        Logger.log_ident-= 1
        assert Logger.log_ident >= 0

    def log (message, icon=" "):
        level = Logger.log_ident
        print ("[{icon}]{space}{pad}{arrow} {message}".format(
            icon=icon,
            space=" " if level > 0 else "",
            pad="".ljust(level,'-'),
            arrow=">" if level > 0 else "",
            message=message))
