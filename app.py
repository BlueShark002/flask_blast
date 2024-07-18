from flask import Flask,render_template,send_from_directory,Response,make_response,request
import flask
import os
import utils,re
from time import sleep
from db import BlastDb

#------------------------
# 主要变量 flask实例，blastdb类，静态目录 
app = Flask(__name__)  # Flask 实例 
BLAST_DB = BlastDb("static/blast-db", "static/blast-query") 
STATIC_DIR = os.path.join(os.path.dirname(__file__), 'static')  

#------------------------
# 路由处理
# 1. 基于目录和文件的路由：/<path:filename>
# 2. 查询已经建立的数据库路由：/api/get_blastdb
# 3. 上传fasta数据进行建库的路由：/api/upload_db
# 4. 上传比对数据进行blast的路由：/api/start_blast

# 基于文件和目录的路由
@app.route('/<path:filename>')  
def serve_static(filename):   
    file_path = os.path.join(STATIC_DIR, filename)  
    if os.path.exists(file_path):  
        # 确保请求的是文件，不是目录  
        if os.path.isfile(file_path):  
            return send_from_directory(STATIC_DIR, filename)  
        else:  
            return "Directory access is not allowed.", 403  
    else:  
        # 如果文件不存在，返回 404 错误  
        return "File not found.", 404  

# 查询已经建立的数据库路由
@app.route('/api/get_blastdb', methods=['POST'])
def get_blastdb(): 
    res = BLAST_DB.getDbList()  
    return flask.jsonify({"db_list":res}) 

# 上传fasta数据进行建库的路由
@app.route('/api/upload_db', methods=['POST'])
def upload_db(): 
    dbtype = request.form.get("dbtype", None)
    dbname = request.form.get("db-name", None)
    # --------------------
    # valid data
    if not dbtype:
        return flask.jsonify({"success":0, "mes":"dbtype is empty"}) 
    if not dbname:
        return flask.jsonify({"success":0, "mes":"dbname is empty"}) 
    file = request.files["db-file"]
    print("***********",request.files.get("db-file","empty"))
    print("***********",file.content_type)
    file_raw_name = file.filename
    # upload file is empty
    if file_raw_name=="":
        return flask.jsonify({"success":0, "mes":"Upload fasta file is empty"}) 
    # dbtype = request.files["dbtype"]
    res = BLAST_DB.makeBlastdb(file,dbname,dbtype)
    print(">>>>>>>>>",request.files)
    print(">>>>>>>>>",dbtype)
    return flask.jsonify(res) 

# 上传比对数据进行blast的路由
@app.route('/api/start_blast', methods=['POST'])
def start_blast():   
    # ?seqs=dsd&evalue=0.001&hit-num=10&dbtype=nucl&db-select=tmp
    keys = ["seqs","evalue","hit-num","dbtype","db-select"]
    # check
    for k in keys:
        v = request.form.get(k, None)
        if not v:
            return flask.jsonify({"success":0,"mes":"Param is not correct"}) 
    args = {k:request.form.get(k, None) for k in keys}
    # --------------------
    # valid seq
    if args["dbtype"]=="nucl":
        if not utils.isFastaDNA(args["seqs"]):
            res = {"success":0,"mes":"Input seq is not suitable for dbtype"}
            return flask.jsonify(res)
    elif args["dbtype"]=="prot":
        if not utils.isFastaProt(args["seqs"]):
            res = {"success":0,"mes":"Input seq and dbtype are inconsistent"}
            return flask.jsonify(res)
    # --------------------
    # save seq and blast it
    res = BLAST_DB.startBlast(args)
    return flask.jsonify({"success":1,"mes":"Blast success","data":res}) 

if __name__ == '__main__':  
    # 运行 Flask 应用，监听本地地址上的 5000 端口 
    # blast页面：http://127.0.0.1:5000/static/html/blast.html 
    app.run(host='0.0.0.0', port=5000, debug=True)