line="T951888   0x0000ffff929a3c90  8b1c0021   add    %x1 %x28 lsl $0x00 -> %x1\n"

import re
isSetPrefixLen=False

if not isSetPrefixLen:
    Tmatch=re.match("^(T[a-zA-Z0-9]*) ",line).group(1)
print(Tmatch)
print(len(Tmatch))