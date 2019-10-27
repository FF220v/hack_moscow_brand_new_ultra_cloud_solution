import logging

class Logger():
    '''Contains static methods for easy logging
    to one file from different modules and threads'''
   
    isLogFileDef = False
    logFile = None
    format_ = '(%(asctime)s)-|%(filename)s|-|%(name)s|-[%(levelname)s]: %(message)s'

    @staticmethod
    def def_logger_file(name='log.txt'):
        '''Creates (or opens) file for logging'''
        logging.basicConfig(level = logging.INFO,
            format = Logger.format_)
        Logger.logFile = logging.FileHandler(name)
        formater = logging.Formatter(Logger.format_)
        Logger.logFile.setFormatter(formater)
        Logger.isLogFileDef = True
        
    @staticmethod
    def get_logger_by_name(name):
        '''Returns ready to work logger object'''
        if not Logger.isLogFileDef:
            Logger.def_logger_file()
        logger=logging.getLogger(name)
        logger.setLevel(logging.INFO)
        logger.addHandler(Logger.logFile)
        #logger.debug('Logger "'+name+'" initialized')
        return logger
        
    