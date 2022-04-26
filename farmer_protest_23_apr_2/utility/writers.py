from utility.otherUtility import *


def textWriter(dataList: list, filePath: str):
    if filePath.endswith(".txt") is False:
        print(".txt Files Only. Please check the file type.")
        exit()
    if type(dataList) is not list:
        print("dataList must be list() type. Please check the type.")
        exit()

    folderPathParts = filePath.split('/')[:-1]
    folderPathsRecursive = ['/'.join(folderPathParts[:x])
                            for x in range(1, len(folderPathParts)+1)]
    for folderPath in folderPathsRecursive:
        makeDirectory(folderPath)

    dataList = [removeEscapes(str(x)) for x in dataList]

    with open(filePath, "w", encoding="utf-8") as outputFile:
        outputFile.writelines('\n'.join(dataList))

