import logging
import logging.handlers

def main():
    import files

def setupLog():
    import config
    logger = logging.getLogger()
    logFormatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    fileHandler = logging.handlers.TimedRotatingFileHandler(config.logFile, encoding='utf-8', when='h', interval=1)
    fileHandler.setFormatter(logFormatter)
    fileHandler.setLevel(logging.DEBUG)
    consoleHandler = logging.StreamHandler()
    consoleHandler.setFormatter(logFormatter)
    consoleHandler.setLevel(logging.DEBUG)
    logger.setLevel(logging.DEBUG)
    logger.addHandler(fileHandler)
    logger.addHandler(consoleHandler)

if __name__ == '__main__':
    setupLog()
    main()