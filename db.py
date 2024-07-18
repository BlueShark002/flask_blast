import utils,re,os

class BlastDb:
    """
    blast操作类，主要功能：
        * 建库功能
        * 比对功能
    """
    def __init__(self, db_root_dir, query_root_dir):
        """
        初始化
            db_root_dir：数据库目录
            query_root_dir：比对数据保存目录
        """
        self.db_root_dir = os.getcwd()+"/"+db_root_dir
        self.db_root_dir = self.db_root_dir.replace("\\","/")
        self.query_root_dir = self.db_root_dir.replace(db_root_dir,query_root_dir)
        print(self.db_root_dir)
        print(self.query_root_dir)

    def getDbList(self):
        """
        返回本地已经建立的数据库名单
        """
        db = os.listdir(self.db_root_dir)
        db_list = []
        for name in db:
            if not re.search("\.db",name):continue
            db_list.append(name)
        return db_list
    
    def getDbPath(self,db_name):
        """
        返回数据库的完整地址
        """
        return "%s/%s/%s"%(self.db_root_dir,db_name,db_name)
    
    def execBlastn(self,args,query, db):
        """
        执行blastn
        """
        # ["seqs","evalue","hit-num","dbtype","db-select"]
        command = "blastn -query %s -db %s -evalue %s -max_target_seqs %s -outfmt 0"%(query,db,args["evalue"],args["hit-num"])
        print("blast>>>>",command)
        out = os.popen(command).read()
        res = utils.parseOutfmt5(out)
        return res
    
    def execBlastp(self, args,query, db):
        """
        执行blastp
        """
        command = "blastp -query %s -db %s -evalue %s -max_target_seqs %s -outfmt 0"%(query,db,args["evalue"],args["hit-num"])
        print("blastp,>>>>",command)
        out = os.popen(command).read()
        res = utils.parseOutfmt5(out)
        return res
    
    def execMakeBlastdb(self, db_path, db_type, db_out):
        """
        执行建立数据库makeblastdb操作
        """
        command = "makeblastdb -dbtype %s -in %s -out %s"%(db_type, db_path, db_out)
        out = os.popen(command).read()
        res = {"success":1,"mes":"Makeblastdb success"}
        return res

    def makeBlastdb(self, file, db_name, db_type):
        """
        建库前数据处理
        """
        raw_file_name = file.filename
        db_path = "%s/raw_db/%s"%(self.db_root_dir, raw_file_name)
        db_my_dir = "%s/%s.db"%(self.db_root_dir, db_name)
        db_my_path = "%s/%s.db"%(db_my_dir, db_name)
        file.save(db_path)
        # valid db
        f = open(db_path)
        c = f.read()
        if db_type=="nucl":
            if utils.isFastaDNA(c):
                return self.execMakeBlastdb(db_path, db_type, db_my_path)
        elif db_type=="prot":
            print(utils.isFastaProt(c))
            if utils.isFastaProt(c):
                return self.execMakeBlastdb(db_path, db_type, db_my_path)
        return {"success":0,"mes":"Upload fasta data and dbtype are inconsistent"}


    def startBlast(self, args):
        """
        blast前数据处理
        """
        seqs = args["seqs"].replace("\r","")
        file_name = "%s.fasta"%(utils.md5_time_content(seqs))
        file_path  = "%s/%s"%(self.query_root_dir, file_name)
        f = open(file_path, "w")
        f.write(seqs)
        f.close()
        # start blast
        if args["dbtype"]=="nucl":
            res = self.execBlastn(args, file_path, self.getDbPath(args["db-select"]))
            return res
        elif args["dbtype"]=="prot":
            res = self.execBlastp(args, file_path, self.getDbPath(args["db-select"]))
            return res 
        
