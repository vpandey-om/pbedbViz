
from ipbedb import db,login_manager
from flask_login import UserMixin




@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model,UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)


    def __repr__(self):
        return f"User('{self.username}', '{self.email}')"



class Cluster(db.Model):
    ''' This table is the cluster table which is the output of Kasia analysis'''

    ### Table
    # pbankaNewID  pbankaOldID shortName description
    # FK (ForeignKey)  clusterID
    ####
    __tablename__ = "cluster"
    id=db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    geneAnots = db.relationship('Geneanot',backref='cluster',lazy=True)



class Geneanot(db.Model):
    ''' This is the table for gene anotation file'''
    ### Table
    # pbankaNewID  pbankaOldID shortName description
    # FK (ForeignKey)  clusterID
    ####
    __tablename__ = "geneanot"
    id=db.Column(db.Integer, primary_key=True)
    pbankaNewID = db.Column(db.String(20))
    pbankaOldID = db.Column(db.String(20))
    description = db.Column(db.String(200))
    shortName = db.Column(db.String(20))
    cluster_id = db.Column(db.Integer, db.ForeignKey('cluster.id'))
    ap2koexp_id = db.Column(db.Integer, db.ForeignKey('ap2koexp.id'))
    ap2time_id = db.Column(db.Integer, db.ForeignKey('ap2time.id'))
    phenodata_id = db.Column(db.Integer, db.ForeignKey('phenodata.id'))

class Ap2komanifest(db.Model):
    __tablename__ = "ap2komanifest"
    id=db.Column(db.Integer, primary_key=True)
    name=db.Column(db.String(20),unique=True)
    description=db.Column(db.String(200))
    geoid=db.Column(db.String(20),unique=True)
    shortName=db.Column(db.String(20))


class Ap2timemanifest(db.Model):
    __tablename__ = "ap2timemanifest"
    id=db.Column(db.Integer, primary_key=True)
    name=db.Column(db.String(20),unique=True)
    file=db.Column(db.String(100))
    time=db.Column(db.String(20))
    rapamycin=db.Column(db.String(20))






# Class AP2KO_exp(db.Model):
#     ''' Modrzynska K, Pfander C, Chappell L, Yu L, Suarez C, Dundas K, Gomes AR, Goulding D, Rayner J, Choudhary J,
#     Billker O (2017) A knockout screen of ApiAP2 genes reveals networks of interacting transcriptional
#     regulators controlling the Plasmodium life cycle. Cell Host Microbe 21 (1) 11-22, doi: 1016/j.chom.2016.12.003. '''
#     __tablename__ = "ap2ko_exp"
#     ## we are building gene expression data for AP2KO
#     id=db.Column(db.Integer, primary_key=True)


class Ap2koexp(db.Model):
	# Modrzynska K, Pfander C, Chappell L, Yu L, Suarez C, Dundas K, Gomes AR, Goulding D, Rayner J, Choudhary J, Billker O (2017) A knockout screen of ApiAP2 genes reveals networks of interacting transcriptional regulators controlling the Plasmodium life cycle. Cell Host Microbe 21 (1) 11-22, doi: 1016/j.chom.2016.12.003.
	__tablename__ = "ap2koexp"
	id=db.Column(db.Integer, primary_key=True)
	name=db.Column(db.String(20), unique=True)
	wt_S_1=db.Column(db.Float,nullable=True)
	ap2_o2_S_1=db.Column(db.Float,nullable=True)
	ap2_g_S_1=db.Column(db.Float,nullable=True)
	ap2_o_S_1=db.Column(db.Float,nullable=True)
	ap2_g2_S_1=db.Column(db.Float,nullable=True)
	ap2_o3_S_1=db.Column(db.Float,nullable=True)
	ap2_sp3_S_1=db.Column(db.Float,nullable=True)
	ap2_l_S_1=db.Column(db.Float,nullable=True)
	ap2_sp_S_1=db.Column(db.Float,nullable=True)
	ap2_o4_S_1=db.Column(db.Float,nullable=True)
	t131970_S_1=db.Column(db.Float,nullable=True)
	ap2_sp2_S_1=db.Column(db.Float,nullable=True)
	wt_S_2=db.Column(db.Float,nullable=True)
	ap2_o2_S_2=db.Column(db.Float,nullable=True)
	ap2_g_S_2=db.Column(db.Float,nullable=True)
	ap2_o_S_2=db.Column(db.Float,nullable=True)
	ap2_g2_S_2=db.Column(db.Float,nullable=True)
	ap2_o3_S_2=db.Column(db.Float,nullable=True)
	wt_S_3=db.Column(db.Float,nullable=True)
	ap2_o2_S_3=db.Column(db.Float,nullable=True)
	ap2_g_S_3=db.Column(db.Float,nullable=True)
	ap2_o_S_3=db.Column(db.Float,nullable=True)
	ap2_g2_S_3=db.Column(db.Float,nullable=True)
	ap2_o3_S_3=db.Column(db.Float,nullable=True)
	wt_O_1=db.Column(db.Float,nullable=True)
	wt_G_1=db.Column(db.Float,nullable=True)
	ap2_o2_G_1=db.Column(db.Float,nullable=True)
	ap2_o_O_1=db.Column(db.Float,nullable=True)
	ap2_o_G_1=db.Column(db.Float,nullable=True)
	ap2_o3_O_1=db.Column(db.Float,nullable=True)
	ap2_o3_G_1=db.Column(db.Float,nullable=True)
	wt_O_2=db.Column(db.Float,nullable=True)
	wt_G_2=db.Column(db.Float,nullable=True)
	ap2_o2_O_2=db.Column(db.Float,nullable=True)
	ap2_o2_G_2=db.Column(db.Float,nullable=True)
	ap2_o_O_2=db.Column(db.Float,nullable=True)
	ap2_o_G_2=db.Column(db.Float,nullable=True)
	ap2_o3_O_2=db.Column(db.Float,nullable=True)
	ap2_o3_G_2=db.Column(db.Float,nullable=True)
	wt_O_3=db.Column(db.Float,nullable=True)
	wt_G_3=db.Column(db.Float,nullable=True)
	ap2_o2_O_3=db.Column(db.Float,nullable=True)
	ap2_o2_G_3=db.Column(db.Float,nullable=True)
	ap2_o_O_3=db.Column(db.Float,nullable=True)
	ap2_o_G_3=db.Column(db.Float,nullable=True)
	ap2_o3_O_3=db.Column(db.Float,nullable=True)
	ap2_o3_G_3=db.Column(db.Float,nullable=True)
	wt_S_4=db.Column(db.Float,nullable=True)
	ap2_sp3_S_2=db.Column(db.Float,nullable=True)
	ap2_l_S_2=db.Column(db.Float,nullable=True)
	ap2_sp_S_2=db.Column(db.Float,nullable=True)
	ap2_o4_S_2=db.Column(db.Float,nullable=True)
	t131970_S_2=db.Column(db.Float,nullable=True)
	ap2_sp2_S_2=db.Column(db.Float,nullable=True)
	wt_S_5=db.Column(db.Float,nullable=True)
	ap2_sp3_S_3=db.Column(db.Float,nullable=True)
	ap2_l_S_3=db.Column(db.Float,nullable=True)
	ap2_sp_S_3=db.Column(db.Float,nullable=True)
	ap2_o4_S_3=db.Column(db.Float,nullable=True)
	t131970_S_3=db.Column(db.Float,nullable=True)
	ap2_sp2_S_3=db.Column(db.Float,nullable=True)
	wt_S_6=db.Column(db.Float,nullable=True)
	geneAnots=db.relationship('Geneanot',backref='ap2koexp',uselist=False,lazy=True)
	# ap2Manifest=db.relationship('Ap2komanifest',backref='ap2koexp_mani',uselist=False,lazy=True)


class Ap2time(db.Model):
	# Kent RS, Modrzynska KK, Cameron R, Philip N, Billker O, Waters AP. Inducible developmental reprogramming redefines commitment to sexual development in the malaria parasite Plasmodium berghei. Nat Microbiol. 2018 Nov;3(11):1206-1213. doi: 10.1038/s41564-018-0223-6. PMID: 30177743
	__tablename__ = "ap2time"
	id=db.Column(db.Integer, primary_key=True)
	name=db.Column(db.String(20), unique=True)
	sample_1=db.Column(db.Float,nullable=True)
	sample_10=db.Column(db.Float,nullable=True)
	sample_11=db.Column(db.Float,nullable=True)
	sample_12=db.Column(db.Float,nullable=True)
	sample_13=db.Column(db.Float,nullable=True)
	sample_14=db.Column(db.Float,nullable=True)
	sample_15=db.Column(db.Float,nullable=True)
	sample_16=db.Column(db.Float,nullable=True)
	sample_17=db.Column(db.Float,nullable=True)
	sample_18=db.Column(db.Float,nullable=True)
	sample_19=db.Column(db.Float,nullable=True)
	sample_2=db.Column(db.Float,nullable=True)
	sample_20=db.Column(db.Float,nullable=True)
	sample_21=db.Column(db.Float,nullable=True)
	sample_22=db.Column(db.Float,nullable=True)
	sample_23=db.Column(db.Float,nullable=True)
	sample_24=db.Column(db.Float,nullable=True)
	sample_25=db.Column(db.Float,nullable=True)
	sample_26=db.Column(db.Float,nullable=True)
	sample_27=db.Column(db.Float,nullable=True)
	sample_28=db.Column(db.Float,nullable=True)
	sample_29=db.Column(db.Float,nullable=True)
	sample_3=db.Column(db.Float,nullable=True)
	sample_30=db.Column(db.Float,nullable=True)
	sample_31=db.Column(db.Float,nullable=True)
	sample_32=db.Column(db.Float,nullable=True)
	sample_33=db.Column(db.Float,nullable=True)
	sample_34=db.Column(db.Float,nullable=True)
	sample_35=db.Column(db.Float,nullable=True)
	sample_36=db.Column(db.Float,nullable=True)
	sample_37=db.Column(db.Float,nullable=True)
	sample_38=db.Column(db.Float,nullable=True)
	sample_39=db.Column(db.Float,nullable=True)
	sample_4=db.Column(db.Float,nullable=True)
	sample_40=db.Column(db.Float,nullable=True)
	sample_41=db.Column(db.Float,nullable=True)
	sample_42=db.Column(db.Float,nullable=True)
	sample_43=db.Column(db.Float,nullable=True)
	sample_44=db.Column(db.Float,nullable=True)
	sample_45=db.Column(db.Float,nullable=True)
	sample_46=db.Column(db.Float,nullable=True)
	sample_47=db.Column(db.Float,nullable=True)
	sample_48=db.Column(db.Float,nullable=True)
	sample_49=db.Column(db.Float,nullable=True)
	sample_5=db.Column(db.Float,nullable=True)
	sample_50=db.Column(db.Float,nullable=True)
	sample_51=db.Column(db.Float,nullable=True)
	sample_52=db.Column(db.Float,nullable=True)
	sample_53=db.Column(db.Float,nullable=True)
	sample_54=db.Column(db.Float,nullable=True)
	sample_55=db.Column(db.Float,nullable=True)
	sample_56=db.Column(db.Float,nullable=True)
	sample_57=db.Column(db.Float,nullable=True)
	sample_58=db.Column(db.Float,nullable=True)
	sample_59=db.Column(db.Float,nullable=True)
	sample_6=db.Column(db.Float,nullable=True)
	sample_60=db.Column(db.Float,nullable=True)
	sample_61=db.Column(db.Float,nullable=True)
	sample_62=db.Column(db.Float,nullable=True)
	sample_63=db.Column(db.Float,nullable=True)
	sample_64=db.Column(db.Float,nullable=True)
	sample_65=db.Column(db.Float,nullable=True)
	sample_66=db.Column(db.Float,nullable=True)
	sample_67=db.Column(db.Float,nullable=True)
	sample_68=db.Column(db.Float,nullable=True)
	sample_69=db.Column(db.Float,nullable=True)
	sample_7=db.Column(db.Float,nullable=True)
	sample_70=db.Column(db.Float,nullable=True)
	sample_71=db.Column(db.Float,nullable=True)
	sample_72=db.Column(db.Float,nullable=True)
	sample_73=db.Column(db.Float,nullable=True)
	sample_74=db.Column(db.Float,nullable=True)
	sample_75=db.Column(db.Float,nullable=True)
	sample_76=db.Column(db.Float,nullable=True)
	sample_77=db.Column(db.Float,nullable=True)
	sample_78=db.Column(db.Float,nullable=True)
	sample_79=db.Column(db.Float,nullable=True)
	sample_8=db.Column(db.Float,nullable=True)
	sample_80=db.Column(db.Float,nullable=True)
	sample_81=db.Column(db.Float,nullable=True)
	sample_82=db.Column(db.Float,nullable=True)
	sample_83=db.Column(db.Float,nullable=True)
	sample_84=db.Column(db.Float,nullable=True)
	sample_85=db.Column(db.Float,nullable=True)
	sample_86=db.Column(db.Float,nullable=True)
	sample_87=db.Column(db.Float,nullable=True)
	sample_88=db.Column(db.Float,nullable=True)
	sample_89=db.Column(db.Float,nullable=True)
	sample_9=db.Column(db.Float,nullable=True)
	sample_90=db.Column(db.Float,nullable=True)
	sample_91=db.Column(db.Float,nullable=True)
	geneAnots=db.relationship('Geneanot',backref='ap2time',uselist=False,lazy=True)


class Phenodata(db.Model):
	# Kent RS, Modrzynska KK, Cameron R, Philip N, Billker O, Waters AP. Inducible developmental reprogramming redefines commitment to sexual development in the malaria parasite Plasmodium berghei. Nat Microbiol. 2018 Nov;3(11):1206-1213. doi: 10.1038/s41564-018-0223-6. PMID: 30177743
	__tablename__ = "phenodata"
	id=db.Column(db.Integer, primary_key=True)
	name=db.Column(db.String(20), unique=True)
	B2toMG_RGR=db.Column(db.Float,nullable=True)
	B2toMG_SD=db.Column(db.Float,nullable=True)
	B2toMG_pheno=db.Column(db.String(20),nullable=True)
	MGtoSG_RGR=db.Column(db.Float,nullable=True)
	MGtoSG_SD=db.Column(db.Float,nullable=True)
	MGtoSG_pheno=db.Column(db.String(20),nullable=True)
	SGtoB2_RGR=db.Column(db.Float,nullable=True)
	SGtoB2_SD=db.Column(db.Float,nullable=True)
	SGtoB2_pheno=db.Column(db.String(20),nullable=True)
	blood_RGR=db.Column(db.Float,nullable=True)
	blood_SD=db.Column(db.Float,nullable=True)
	blood_pheno=db.Column(db.String(20),nullable=True)
	female_fertility_RGR=db.Column(db.Float,nullable=True)
	female_fertility_SD=db.Column(db.Float,nullable=True)
	female_fertility_pheno=db.Column(db.String(20),nullable=True)
	male_fertility_RGR=db.Column(db.Float,nullable=True)
	male_fertility_SD=db.Column(db.Float,nullable=True)
	male_fertility_pheno=db.Column(db.String(20),nullable=True)
	female_gam_RGR=db.Column(db.Float,nullable=True)
	female_gam_SD=db.Column(db.Float,nullable=True)
	female_gam_pheno=db.Column(db.String(20),nullable=True)
	male_gam_RGR=db.Column(db.Float,nullable=True)
	male_gam_SD=db.Column(db.Float,nullable=True)
	male_gam_pheno=db.Column(db.String(20),nullable=True)
	geneAnots=db.relationship('Geneanot',backref='phenodata',uselist=False,lazy=True)
