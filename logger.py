class Logger:
    log_ident = 0

    def nest_up():
        Logger.log_ident+= 1

    def nest_down():
        Logger.log_ident-= 1
        assert Logger.log_ident >= 0

    def log (message):
        print ("{pad}- {message}".format(
            pad="".ljust(Logger.log_ident,'-'),
            message=message))
