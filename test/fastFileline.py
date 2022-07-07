def blocks(files, size=65536):
    while True:
        b = files.read(size)
        if not b: break
        yield b



with open("/home/shaojiemike/test/DynamoRIO/OpenBLASRawAssembly/open_test.log", "r",encoding="utf-8",errors='ignore') as f:
    print (sum(bl.count("\n") for bl in blocks(f)))