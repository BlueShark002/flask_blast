import hashlib  
from time import time
import re,os

def md5_string(input_string):  
    # 创建一个md5 hash对象  
    md5_hash = hashlib.md5()  
    # 更新hash对象以字符串数据  
    md5_hash.update(input_string.encode())  
    # 获取16进制的hash值  
    digest = md5_hash.hexdigest()  
    return digest  

def md5_time_content(string):
    time_content = "%s-%s"%(time(), string)
    return md5_string(time_content)

def parseOutfmt5(c):
    if re.search("No hits found",c):
        res = {
            "hit_id":[],
            "scores":[],
            "evalue":[],
            "gaps":[],
            "strand":[],
            "align_str":[],
            "query_cov":[],
            "ident":[]
        }
        return res
    hit_ids = re.findall(">(.+) *", c)
    scores = re.findall("Score = (\d+) bits",c)
    expects = re.findall("Expect = ([\d\.e-]+)",c)
    idents = re.findall("Identities = (.+?),",c)
    gaps = re.findall("Gaps = (.+)",c)
    strand = re.findall("Strand=(.+)",c)
    align = re.findall("(Query[^>]+)\n",c)[1:]
    align = [re.sub("Score[\w\W]+","",a) for a in align]
    align[-1] = re.sub("Lambda[^>]+","",align[-1])
    query_len = int(re.findall("\nLength=(.+)",c)[0])
    query_align_len = [int(ident.split("/")[0]) for ident in idents]
    query_cov = ["%.1f%s"%(100*qal/query_len,"%") for qal in query_align_len]
    res = {
        "hit_id":hit_ids,
        "scores":scores,
        "evalue":expects,
        "gaps":gaps,
        "strand":strand,
        "align_str":align,
        "query_cov":query_cov,
        "ident":idents,
        "query_len":query_len
    }
    # print(align)
    return res

def isFastaDNA(seq):
    m = re.search(">.+\n[^ATCG\n]+",seq)
    if m:
        return False
    return True

def isFastaProt(seq):
    m = re.search(">.+\n[^AFCUDNEQGHLIKOMPRSTVWYX\n]+",seq)
    if m:
        return False
    return True

def selectMkdir(dir):
    if os.path.exists(dir):
        return
    os.system("mkdir %s"%(dir))
    