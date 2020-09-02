import pickle
import pandas as pd
import numpy as np
def explore_expression_data():
    ''' we are going to check expression data from two publications from Oliver'''
    print ('hi')

    time_rpkm_df,plan_df=pickle.load(open('/Users/vikash/Documents/GeneRegulatory/Files/rpkm_and_plan_final.pickle','rb'))

    ap2_rpkm_df, sample_df = pickle.load(open('/Users/vikash/Documents/GeneRegulatory/Files/Ap2_data_KO.pkl', 'rb'))

    kasia_cluster=pd.read_csv('/Users/vikash/Documents/GeneRegulatory/Files/RobKas_cluster.txt','\t')
    time_rpkm_df.index=time_rpkm_df.index.str[:-2]
    ap2_rpkm_df.index = ap2_rpkm_df.index.str[:-2]
    #####
    pickdata=pickle.load(open('/Users/vikash/Documents/GeneRegulatory/Files/prevTonew_PBANKA.pickle','rb'))
    df=pd.read_csv('/Users/vikash/Documents/GeneRegulatory/Files/PBANK_ID_conversion.txt','\t')
    geneAnot=pd.DataFrame(index=df['Gene ID'],columns=['description','old_id','gene_name'])
    new_to_prev = {value : key for (key, value) in pickdata.items()}

    oldIds=[]
    for g in geneAnot.index:
        if g in new_to_prev.keys():
            oldIds.append(new_to_prev[g])
        else:
            oldIds.append(g)
    geneAnot['description']=df['Product Description'].to_list()
    geneAnot['gene_name']=df['Gene Name or Symbol'].to_list()
    geneAnot['old_id']=oldIds
    ##
    ap2_manifest=sample_df.copy()
    ap2_manifest=ap2_manifest.rename(columns={"Sample_title": "id", "Sample_source_name_ch1": "description",'Sample_geo_accession':'geoid'})

    ap2_manifest['shortName']=ap2_manifest['id'].str[:-2]
    ap2_manifest['id']=ap2_manifest['id'].str.replace('-','_')
    ap2_rpkm_df.columns=ap2_rpkm_df.columns.str.replace('-','_')
    pickle.dump(ap2_manifest,open('/Users/vikash/git-hub/pbeDB/data/table_header_exp.pkl','wb'))
    cluster_df=kasia_cluster.loc[:,['GeneId','Cluster']].copy()

    ### explore time df

    time_rpkm_df=time_rpkm_df.rename(columns=dict(zip(plan_df['file'],plan_df['sample'])))
    time_rpkm_df.columns=time_rpkm_df.columns.str.lower()
    plan_df['sample']=plan_df['sample'].str.lower()
    return [time_rpkm_df,plan_df,ap2_rpkm_df, ap2_manifest,cluster_df,geneAnot]

def merge_phenotype_data():
    ''' We are going to combine blood and liver satge screening data '''
    df=pd.read_csv('/Users/vikash/git-hub/pbeDB/data/Phenotype_oliver.txt',sep='\t')
    df.set_index('Gene.ID_new',inplace=True)
    red_df=df.loc[:,['MG_quart_diff 30.01','MG_quart_SD 30.01','MG_quart_power 30.01','SG_quart_diff 30.01',
                'SG_quart_SD 30.01','SG_quart_power 30.01','REC_Q-B_diff 31.01','REC_Q-B_SD 31.01',
                'REC_Q-B_power 31.01','Relative.Growth.Rate','blood_SD','phenotype']]

    rename_cols={'MG_quart_diff 30.01':'B2toMG_RGR','MG_quart_SD 30.01':'B2toMG_SD','MG_quart_power 30.01':'B2toMG_pheno',
                'SG_quart_diff 30.01':'MGtoSG_RGR','SG_quart_SD 30.01':'MGtoSG_SD','SG_quart_power 30.01':'MGtoSG_pheno',
                'REC_Q-B_diff 31.01':'SGtoB2_RGR','REC_Q-B_SD 31.01':'SGtoB2_SD','REC_Q-B_power 31.01':'SGtoB2_pheno',
                'Relative.Growth.Rate':'blood_RGR','blood_SD':'blood_SD','phenotype':'blood_pheno'
                }
    red_df=red_df.rename(columns=rename_cols)
    red_df2_index= red_df.index.dropna()
    red_df2=red_df.loc[red_df2_index,:].copy()
    red_df2=red_df2.replace({'#VALUE!': np.nan})
    pickle.dump(red_df2.columns,open('/Users/vikash/git-hub/pbeDB/data/phenotype_table_header.pkl','wb'))
    return red_df2

# if  __name__=="__main__":
#     #explore_expression_data()
#
#     merge_phenotype_data()
