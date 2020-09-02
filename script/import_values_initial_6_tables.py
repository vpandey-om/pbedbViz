#  With this script we are going to import values for tables
# 1) ap2time  ## This is AP2 overexpression data form Kent et al. Rapamycin treatment
# 2) ap2timemanifest ## This is the manifest for AP2 overexpression data
# 3)ap2koexp ## This is the data which is taken form diffrent type of Ap2 ko. kasia paepr.
# 4) ap2komanifest # This is the manifest for Ap2 ko.
# 5) Cluster # This is the cluster data
# 6) geneanot # this is the geneAnot



from external_df import *
# import pickle

[time_rpkm_df,plan_df,ap2_rpkm_df, ap2_manifest,cluster_df,geneAnot]=explore_expression_data()

# pickle.dump(plan_df,open('/Users/vikash/git-hub/pbeDB/data/ap2_time_manifest.pickle','wb'))

err1=time_rpkm_df.index[time_rpkm_df.index.str.contains('.1%')]
err2=time_rpkm_df.index[time_rpkm_df.index.str.contains('.2%')]




rename_cols={}
ap2_rpkm_df_filter=ap2_rpkm_df[~ap2_rpkm_df.isnull().all(1)]
for col in ap2_rpkm_df_filter.columns:
    if col[0].isdigit():
        rename_cols[col]='t'+col

ap2_rpkm_df_filter=ap2_rpkm_df_filter.rename(columns=rename_cols)
ap2_manifest['id']=ap2_manifest['id'].replace(rename_cols)
ap2_manifest['shortName']=ap2_manifest['id'].str[:-2]



### add values in cluster table

from ipbedb import app,db


from ipbedb.db_model import User,Cluster,Geneanot,Ap2koexp,Ap2komanifest,Ap2time,Ap2timemanifest

# import pdb;pdb.set_trace()



# we are going to create table for ap2 time  manifests
ap2_time_manifest=plan_df.set_index('sample')
for idx in ap2_time_manifest.index:
    ga=Ap2timemanifest(name=idx,file=ap2_time_manifest.loc[idx,'file'],
    rapamycin=ap2_time_manifest.loc[idx,'rapamycin'],time=ap2_time_manifest.loc[idx,'time'])
    try:
        db.session.add(ga)
        print(ga.name)
    except:
        import pdb;pdb.set_trace()

db.session.commit()

### insert  into AP2 time gene expression data
##
# import pdb;pdb.set_trace()



time_rpkm_df=time_rpkm_df.drop(err1)
time_rpkm_df=time_rpkm_df.drop(err2)
time_rpkm_df = time_rpkm_df.loc[~time_rpkm_df.index.duplicated(keep='first')]


for idx in time_rpkm_df.index:
    values=time_rpkm_df.loc[idx,:].copy()

    data=dict(zip(values.index,values.values))
    data['name']=idx

    ap2t=Ap2time(**data)
    db.session.add(ap2t)

db.session.commit()





### we are going to create table for ap2koexp manifests
# import pdb;pdb.set_trace()
for idx in ap2_manifest.index:
    ga=Ap2komanifest(name=ap2_manifest.loc[idx,'id'],description=ap2_manifest.loc[idx,'description'],
    shortName=ap2_manifest.loc[idx,'shortName'],geoid=ap2_manifest.loc[idx,'geoid'])
    try:
        db.session.add(ga)
        print(ga.name)
    except:
        import pdb;pdb.set_trace()

db.session.commit()



# import pdb;pdb.set_trace()

for cluster in cluster_df['Cluster'].unique():

    clust=Cluster(name='c_'+str(cluster))
    try:
        db.session.add(clust)
        print(cluster)
    except:
        import pdb;pdb.set_trace()

db.session.commit()


### insert  into AP2KO gene expression data
##


# ap2_rpkm_df_filter = ap2_rpkm_df_filter.loc[~ap2_rpkm_df_filter.index.duplicated(keep='first')]

for idx in ap2_rpkm_df_filter.index:
    values=ap2_rpkm_df_filter.loc[idx,:].copy()

    data=dict(zip(values.index,values.values))
    data['name']=idx
    ap2ko=Ap2koexp(**data)
    db.session.add(ap2ko)
db.session.commit()

#import pdb;pdb.set_trace()




### add in gene anotation table
geneAnot = geneAnot.loc[~geneAnot.index.duplicated(keep='first')]
for new_id in geneAnot.index:

    # get cluster id
    tmp_clust=cluster_df[cluster_df['GeneId']==new_id]
    tmp_ap2ko=ap2_rpkm_df_filter[ap2_rpkm_df_filter.index==new_id]
    tmp_ap2time=time_rpkm_df[time_rpkm_df.index==new_id]

    case1= (tmp_clust.empty) and (tmp_ap2ko.empty) and (tmp_ap2time.empty)
    case2= (not tmp_clust.empty) and (tmp_ap2ko.empty) and (tmp_ap2time.empty)
    case3= (tmp_clust.empty) and (not tmp_ap2ko.empty) and (tmp_ap2time.empty)
    case4= (tmp_clust.empty) and (tmp_ap2ko.empty) and (not tmp_ap2time.empty)
    case5= (not tmp_clust.empty) and (not tmp_ap2ko.empty) and (tmp_ap2time.empty)
    case6= (tmp_clust.empty) and (not tmp_ap2ko.empty) and (not tmp_ap2time.empty)
    case7= (not tmp_clust.empty) and (tmp_ap2ko.empty) and (not tmp_ap2time.empty)
    case8= (not tmp_clust.empty) and (not tmp_ap2ko.empty) and (not tmp_ap2time.empty)

    if case1:
         ga=Geneanot(pbankaNewID=new_id,pbankaOldID=geneAnot.loc[new_id,'old_id'],description=geneAnot.loc[new_id,'description'],
         shortName=geneAnot.loc[new_id,'gene_name'])
    elif case3:
         gene=tmp_ap2ko.index[0] ### hard coded
         ap2ko = Ap2koexp.query.filter_by(name=gene).first()
         ga=Geneanot(pbankaNewID=new_id,pbankaOldID=geneAnot.loc[new_id,'old_id'],description=geneAnot.loc[new_id,'description'],
         shortName=geneAnot.loc[new_id,'gene_name'],ap2koexp=ap2ko)
    elif case2:
        first_clust=tmp_clust.iloc[0,1] ### hard coded
        clust = Cluster.query.filter_by(name='c_'+str(first_clust)).first()
        ga=Geneanot(pbankaNewID=new_id,pbankaOldID=geneAnot.loc[new_id,'old_id'],description=geneAnot.loc[new_id,'description'],
         shortName=geneAnot.loc[new_id,'gene_name'],cluster=clust)
    elif case4:
        gene=tmp_ap2time.index[0] ### hard coded
        ap2t = Ap2time.query.filter_by(name=gene).first()
        ga=Geneanot(pbankaNewID=new_id,pbankaOldID=geneAnot.loc[new_id,'old_id'],description=geneAnot.loc[new_id,'description'],
        shortName=geneAnot.loc[new_id,'gene_name'],ap2time=ap2t)
    elif case5:
        first_clust=tmp_clust.iloc[0,1] ### hard coded
        clust = Cluster.query.filter_by(name='c_'+str(first_clust)).first()
        gene=tmp_ap2ko.index[0] ### hard coded
        ap2ko = Ap2koexp.query.filter_by(name=gene).first()
        ga=Geneanot(pbankaNewID=new_id,pbankaOldID=geneAnot.loc[new_id,'old_id'],description=geneAnot.loc[new_id,'description'],
        shortName=geneAnot.loc[new_id,'gene_name'],cluster=clust,ap2koexp=ap2ko)
    elif case6:
        gene=tmp_ap2ko.index[0] ### hard coded
        ap2ko = Ap2koexp.query.filter_by(name=gene).first()
        gene=tmp_ap2time.index[0] ### hard coded
        ap2t = Ap2time.query.filter_by(name=gene).first()
        ga=Geneanot(pbankaNewID=new_id,pbankaOldID=geneAnot.loc[new_id,'old_id'],description=geneAnot.loc[new_id,'description'],
        shortName=geneAnot.loc[new_id,'gene_name'],ap2time=ap2t,ap2koexp=ap2ko)
    elif case7:
        first_clust=tmp_clust.iloc[0,1] ### hard coded
        clust = Cluster.query.filter_by(name='c_'+str(first_clust)).first()
        gene=tmp_ap2time.index[0] ### hard coded
        ap2t = Ap2time.query.filter_by(name=gene).first()
        ga=Geneanot(pbankaNewID=new_id,pbankaOldID=geneAnot.loc[new_id,'old_id'],description=geneAnot.loc[new_id,'description'],
        shortName=geneAnot.loc[new_id,'gene_name'],cluster=clust,ap2time=ap2t)
    elif case8:
        first_clust=tmp_clust.iloc[0,1] ### hard coded
        clust = Cluster.query.filter_by(name='c_'+str(first_clust)).first()
        gene=tmp_ap2time.index[0] ### hard coded
        ap2t = Ap2time.query.filter_by(name=gene).first()
        gene=tmp_ap2ko.index[0] ### hard coded
        ap2ko = Ap2koexp.query.filter_by(name=gene).first()
        ga=Geneanot(pbankaNewID=new_id,pbankaOldID=geneAnot.loc[new_id,'old_id'],description=geneAnot.loc[new_id,'description'],
        shortName=geneAnot.loc[new_id,'gene_name'],cluster=clust,ap2time=ap2t,ap2koexp=ap2ko)

    else:
        print('This case can not be occur ')








    # if tmp_clust.empty and tmp_ap2ko.empty:
    #     ga=Geneanot(pbankaNewID=new_id,pbankaOldID=geneAnot.loc[new_id,'old_id'],description=geneAnot.loc[new_id,'description'],
    #     shortName=geneAnot.loc[new_id,'gene_name'])
    # elif tmp_clust.empty and (not tmp_ap2ko.empty):
    #
    #     gene=tmp_ap2ko.index[0] ### hard coded
    #     ap2ko = Ap2koexp.query.filter_by(name=gene).first()
    #     ga=Geneanot(pbankaNewID=new_id,pbankaOldID=geneAnot.loc[new_id,'old_id'],description=geneAnot.loc[new_id,'description'],
    #     shortName=geneAnot.loc[new_id,'gene_name'],ap2koexp=ap2ko)
    # elif (not tmp_clust.empty) and tmp_ap2ko.empty:
    #
    #     first_clust=tmp_clust.iloc[0,1] ### hard coded
    #     clust = Cluster.query.filter_by(name='c_'+str(first_clust)).first()
    #     ga=Geneanot(pbankaNewID=new_id,pbankaOldID=geneAnot.loc[new_id,'old_id'],description=geneAnot.loc[new_id,'description'],
    #     shortName=geneAnot.loc[new_id,'gene_name'],cluster=clust)
    #
    # else:
    #
    #     gene=tmp_ap2ko.index[0] ### hard coded
    #     ap2ko = Ap2koexp.query.filter_by(name=gene).first()
    #     first_clust=tmp_clust.iloc[0,1] ### hard coded
    #     clust = Cluster.query.filter_by(name='c_'+str(first_clust)).first()
    #     ga=Geneanot(pbankaNewID=new_id,pbankaOldID=geneAnot.loc[new_id,'old_id'],description=geneAnot.loc[new_id,'description'],
    #     shortName=geneAnot.loc[new_id,'gene_name'],cluster=clust,ap2koexp_id=ap2ko.id)
        db.session.add(ga)
db.session.commit()










# def main():
#     f = open("flights.csv")
#     reader = csv.reader(f)
#     for origin, destination, duration in reader:
#         flight = Flight(origin=origin, destination=destination, duration=duration)
#         db.session.add(flight)
#         print(f"Added flight from {origin} to {destination} lasting {duration} minutes.")
#     db.session.commit()
