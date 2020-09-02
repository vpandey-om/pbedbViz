from external_df import *
import pickle

pheno_df_old=merge_phenotype_data()

### get big table for phenotype
new_pheno_df=pd.read_csv('/Users/vikash/git-hub/pbeDB/data/all_screening_data_without_nan.txt','\t')
new_pheno_df.set_index('pbanka_id',inplace=True)
rename_columns={'GCKO2_RGR':'female_fertility_RGR','GCKO2_sd':'female_fertility_SD','GCKO2_pheno':'female_fertility_pheno',
'g145480_RGR':'male_fertility_RGR','g145480_sd':'male_fertility_SD','g145480_pheno':'male_fertility_pheno',
'Female gametocytes':'female_gam_RGR','differencesd.y':'female_gam_SD','power.y':'female_gam_pheno',
'difference.x':'male_gam_RGR','differencesd.x':'male_gam_SD','phenotype.x':'male_gam_pheno'}
new_pheno_df=new_pheno_df.rename(columns=rename_columns)
all_columns=[]
columns=['female_fertility_RGR','female_fertility_SD','female_fertility_pheno',
'male_fertility_RGR','male_fertility_SD','male_fertility_pheno',
'female_gam_RGR','female_gam_SD','female_gam_pheno',
'male_gam_RGR','male_gam_SD','male_gam_pheno']

for col in pheno_df_old.columns.to_list()+columns:
    all_columns.append(col)

## geamtocyte and fertility screen data
pheno_df=new_pheno_df.loc[:,all_columns].copy()

# pickle.dump(pheno_df.columns,open('/Users/vikash/git-hub/pbeDB/data/phenotype_table_header.pkl','wb'))


[time_rpkm_df,plan_df,ap2_rpkm_df, ap2_manifest,cluster_df,geneAnot]=explore_expression_data()

from ipbedb import app,db
from ipbedb.db_model import Geneanot,Phenodata
import numpy as np

## drop certain table with flask-sqlalchemy
# import pdb;pdb.set_trace()

pheno_df = pheno_df.loc[~pheno_df.index.duplicated(keep='first')]

for idx in pheno_df.index:
    values=pheno_df.loc[idx,:].copy()
    data={}
    for k,v  in enumerate(values):
        if not ('_pheno' in values.index[k]):
            try:
                data[values.index[k]]=float(v)
            except:
                data[values.index[k]]=np.nan
        else:
            data[values.index[k]]=v

    data['name']=idx
    pdata=Phenodata(**data)
    db.session.add(pdata)
db.session.commit()

# update 'SD'


pheno_df = pheno_df.loc[~pheno_df.index.duplicated(keep='first')]

for idx in pheno_df.index:

    sd_val=float(pheno_df.loc[idx,'blood_SD'])

    pdata = Phenodata.query.filter_by(name=idx).first()
    pdata.blood_SD=sd_val
    db.session.commit()





## update Genotype
### add in gene anotation table
geneAnot = geneAnot.loc[~geneAnot.index.duplicated(keep='first')]
for new_id in geneAnot.index:

    # get cluster id
    tmp_pheno=pheno_df[pheno_df.index==new_id]
    if not tmp_pheno.empty:
        gene=tmp_pheno.index[0] ### hard coded
        pdata = Phenodata.query.filter_by(name=gene).first()
        ga = Geneanot.query.filter_by(pbankaNewID=new_id).first()
        ga.phenodata_id = pdata.id
        db.session.commit()
