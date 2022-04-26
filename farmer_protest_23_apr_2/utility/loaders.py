def textLoader(filePath: str, dataType: str):
    if filePath.endswith(".txt") is False:
        print(".txt Files Only. Please check the file type.")
        exit()
    if dataType == "str":
        typeFunc = str
    elif dataType == "int":
        typeFunc = int
    elif dataType == "float":
        typeFunc = float
    else:
        print("Invalid data type chosen. Please choose an appropriate value.")
        exit()

    with open(filePath, "r", encoding="utf-8") as inputFile:
        dataList = [typeFunc(x.strip()) for x in inputFile.readlines()]

    return dataList
