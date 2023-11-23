# uglylogger

An ugly, slow Logger class for python

## FAQ

### Why required python version is equal or greater than 3.10?  
- match .. case .. is introduced in [3.10](https://docs.python.org/3/whatsnew/3.10.html) and I am not interested in supporting older releases  

### Why is it ugly?
- I am not an expert on Python
- It is not thread-safe
- I don't know what happens if two instances are created with the same name, and I don't care. I'd never do that
- The solo purpose is to have an easy to use and easy to read logger class

### Why is it ugly but not that ugly?
- it is easy to use and easy to read
- I may keep this library up-to-date and even optimize it in the future
- at least it has a CI/CD pipeline

## Installation

`pip install uglylogger`

## Release Notes

[Release notes](RELEASE_NOTES.md)  

## Usage

### Instantiate
```
# A logger which can log both to console and to a file
logger = Logger("name", "file.log")  

# A logger which can only log to console
logger = Logger("name")  
```

### Release the resources
```
logger.release()
```
- Releases the resources, it's safe to delete the log file after calling this method

### Color Mode
```
logger.set_color_mode(LogColorMode.COLORED)
```
- coloroed output if the console/terminal supports it
```
logger.set_color_mode(LogColorMode.MONO)
```
- no color used for the console/terminal output

### Log to console
```
logger.console("Message", color=LogColor.BLACK, level=LogLevel.DEBUG)
```
- color and level are optional
- if not provided, default color is BLACK
- if not provided, default level is DEBUG

### Log to file
```
logger.file("Message", level=LogLevel.DEBUG)
```
- level is optional
- if not provided, default level is DEBUG
- if instantiated without a file name, nothing happens

### Log to both file and console
```
logger.log("Message", color=LogColor.BLACK, level=LogLevel.DEBUG, output=LogOutput.ALL)
```
- color, level and output are optional
- if not provided, default color is BLACK
- if not provided, default level is DEBUG
- if not provided, default output is ALL
- if instantiated without a file name, writing to file is ignored


### Other ways of logging

`logger.debug("Message", color=LogColor.BLACK, output=LogOutput.ALL)`  
`logger.info("Message", color=LogColor.BLACK, output=LogOutput.ALL)`  
`logger.warning("Message", color=LogColor.BLACK, output=LogOutput.ALL)`  
`logger.error("Message", color=LogColor.BLACK, output=LogOutput.ALL)`  
`logger.critical("Message", color=LogColor.BLACK, output=LogOutput.ALL)`  

### Available LogColor
    - BLACK
    - RED
    - GREEN
    - YELLOW
    - BLUE
    - MAGENTA
    - CYAN
    - WHITE

### Available LogLevel
    - DEBUG
    - INFO
    - WARNING
    - ERROR
    - CRITICAL

### Available LogOutput
    - NONE
    - CONSOLE
    - FILE
    - ALL

## set log format
```
logger.set_format([
    ...
    LogFormatBlock.XXX
    ...
])
```

### Available LogFormatBlock
    - NAME
    - LEVEL
    - DATETIME
    - MESSAGE
    - FILE
    - LINE
    - FUNCTION

### Example Formats
```
logger.set_format([LogFormatBlock.MESSAGE])
logger.console("Hello World!")
# Output : Hello World!
```
```
logger.set_format([
    "[",
    LogFormatBlock.LEVEL,
    "] ",
    LogFormatBlock.MESSAGE]
)
logger.console("Hello World!")
# Output : [DEBUG] Hello World!
```