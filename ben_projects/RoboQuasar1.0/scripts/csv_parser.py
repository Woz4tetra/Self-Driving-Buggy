import sys

sys.path.insert(0, '../')

from board import logger

if __name__ == '__main__':
    arguments = sys.argv

    print(logger.parse(arguments[1]))
