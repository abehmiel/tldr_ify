import unicodedata

def buzzclean(line):
    dirtychars="]["
    dubquotechars="“”"
    singquotechars="‘’"
    line = unicodedata.normalize("NFKD", line)
    for _ in line:
        if _ in dirtychars:
            line = line.replace(_,"")
        if _ in dubquotechars:
            line = line.replace(_,'"')
        if _ in singquotechars:
            line = line.replace(_,"'")
    if '{\n    "id": 0\n  }' in line:
        line = line.replace('{\n    "id": 0\n  }',' ')
    return line

