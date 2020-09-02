import pickle
#### set some of the header tables hard coded



def create_AP2KO_exp(ap2ko_manifest):
    str= "class Ap2koexp(db.Model):"+"\n\t"+"# Modrzynska K, Pfander C, Chappell L, Yu L, Suarez C, Dundas K, Gomes AR, Goulding D, Rayner J, Choudhary J, Billker O (2017) A knockout screen of ApiAP2 genes reveals networks of interacting transcriptional regulators controlling the Plasmodium life cycle. Cell Host Microbe 21 (1) 11-22, doi: 1016/j.chom.2016.12.003." + \
    "\n\t"+ '__tablename__ = "ap2koexp"'+"\n\t"+ 'id=db.Column(db.Integer, primary_key=True)'+"\n\t"+ 'name=db.Column(db.String(20), unique=True)'

    for id in ap2ko_manifest['id'] :
        if id[0].isdigit():
            str=str+"\n\t"+"t%s=db.Column(db.Float,nullable=True)"%id

        else:
            str=str+"\n\t"+"%s=db.Column(db.Float,nullable=True)"%id
    str=str+"\n\t"+ "geneAnots=db.relationship('Geneanot',backref='ap2koexp',uselist=False,lazy=True)"
    # str=str+"\n\t"+"ap2Manifest=db.relationship('Ap2komanifest',backref='ap2koexp',uselist=False,lazy=True)"
    out=open('/Users/vikash/git-hub/pbeDB/data/exp_class.py','w')
    out.write("%s"%str)




def create_phenotype_class(headers):
    ''' We are going to create Phenotype table '''
    str= "class Phenodata(db.Model):"+"\n\t"+"# Kent RS, Modrzynska KK, Cameron R, Philip N, Billker O, Waters AP. Inducible developmental reprogramming redefines commitment to sexual development in the malaria parasite Plasmodium berghei. Nat Microbiol. 2018 Nov;3(11):1206-1213. doi: 10.1038/s41564-018-0223-6. PMID: 30177743" + \
    "\n\t"+ '__tablename__ = "phenodata"'+"\n\t"+ 'id=db.Column(db.Integer, primary_key=True)'+"\n\t"+ 'name=db.Column(db.String(20), unique=True)'

    for id in headers:
        if '_pheno' in id:
            str=str+"\n\t"+"%s=db.Column(db.String(20),nullable=True)"%id
        else:
            str=str+"\n\t"+"%s=db.Column(db.Float,nullable=True)"%id
    str=str+"\n\t"+ "geneAnots=db.relationship('Geneanot',backref='phenodata',uselist=False,lazy=True)"
    # str=str+"\n\t"+"ap2Manifest=db.relationship('Ap2komanifest',backref='ap2koexp',uselist=False,lazy=True)"
    out=open('/Users/vikash/git-hub/pbeDB/data/pheno_class.py','w')
    out.write("%s"%str)

def create_classes_for_expression_data():
    # ap2ko_manifest=pickle.load(open('/Users/vikash/git-hub/pbeDB/data/table_header_exp.pkl','rb')) ## this is a dataframe
    # create_AP2KO_exp(ap2ko_manifest)

    # ap2time_manifest=pickle.load(open('/Users/vikash/git-hub/pbeDB/data/ap2_time_manifest.pickle','rb')) ## this is a dataframe
    # create_AP2time(ap2time_manifest)

    ## create phenotype data
    headers=pickle.load(open('/Users/vikash/git-hub/pbeDB/data/phenotype_table_header.pkl','rb'))
    
    create_phenotype_class(headers)

def create_AP2time(ap2time_manifest):
    str= "class Ap2time(db.Model):"+"\n\t"+"# Kent RS, Modrzynska KK, Cameron R, Philip N, Billker O, Waters AP. Inducible developmental reprogramming redefines commitment to sexual development in the malaria parasite Plasmodium berghei. Nat Microbiol. 2018 Nov;3(11):1206-1213. doi: 10.1038/s41564-018-0223-6. PMID: 30177743" + \
    "\n\t"+ '__tablename__ = "ap2time"'+"\n\t"+ 'id=db.Column(db.Integer, primary_key=True)'+"\n\t"+ 'name=db.Column(db.String(20), unique=True)'

    for id in ap2time_manifest['sample'] :
        str=str+"\n\t"+"%s=db.Column(db.Float,nullable=True)"%id
    str=str+"\n\t"+ "geneAnots=db.relationship('Geneanot',backref='ap2time',uselist=False,lazy=True)"
    # str=str+"\n\t"+"ap2Manifest=db.relationship('Ap2komanifest',backref='ap2koexp',uselist=False,lazy=True)"
    out=open('/Users/vikash/git-hub/pbeDB/data/exp_class_time.py','w')
    out.write("%s"%str)


if  __name__=="__main__":
    create_classes_for_expression_data()
