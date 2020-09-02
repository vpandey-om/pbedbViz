import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns;
fig_save='/Users/vikash/Documents/Projects/Claire/Plots/'




def error_liver():
    # read dataframe from theo analysis
    df=pd.read_csv("/Users/vikash/Documents/Projects/mosquitostagescreen-master/df_narrow_line_112.csv")

    # we group by Pool, Condition (Blood1/MG/SG/Blood2), Mouse (bio replicate) and Replicate (tech replicate) to calculate the proportion within each replicate of each sample.
    # technical varaiance

    # grp1=['Pool','Condition','Mouse','Replicate']
    # grp2=['Pool','Condition','Mouse']
    # tech_pair=get_tech_pair(df,grp1,grp2)
    #
    # tech_df_dict=get_df_m_sd(df,grp1,tech_pair) # this is the dictionary of technical replicates

    # for biological variance
    grp1=['Pool','Condition','Mouse','Replicate']
    # grp2=['Pool','Condition','Mouse']
    grp2=['Pool','Condition']
    bio_pair=get_bio_pair(df,grp1,grp2)
    bio_df_dict=get_df_m_sd(df,grp1,bio_pair)
# read phenotypes
    pheno=pd.read_csv("/Users/vikash/Documents/Projects/mosquitostagescreen-master/phenotype.csv")


    conditions=['Passage','SG', 'MG', 'Rec'] # these are conditions

    cond_df,cond_info=getConditionValues(df, bio_df_dict,conditions)

    # common genes in the input
    genes=set(cond_df[1].index.to_list()) & set(pheno["Gene.ID"])

    # get phenodataframe
    pheno.set_index("Gene.ID",  inplace=True)

    pheno_subset=pheno.loc[list(genes),:]
    # input dataframe
    pheno_data=cond_df[0].loc[pheno_subset.index,['mean']] # taking mean from input
    pheno_data['MG_SD']= cond_df[2].loc[pheno_subset.index,['std']] # taking variance from MG
    pheno_data['MG_rel']= cond_df[2].loc[pheno_subset.index,['rel']] # taking variance from MG
    pheno_data['MG_rel_abundance']= cond_df[2].loc[pheno_subset.index,['mean']] # taking variance from MG
    pheno_data['B1_rel_abundance']= cond_df[0].loc[pheno_subset.index,['mean']]

    # we are going to plot figures
    folder="/Users/vikash/Documents/Projects/mosquitostagescreen-master/Figures/"


    cmb_df=pheno_data.join(pheno_subset, how='outer')

    plt.figure(figsize=(8, 8))
    ax = sns.scatterplot(x="MG_rel_abundance", y="B1_rel_abundance", hue="Phenotypes", data=cmb_df, legend='brief',s=10)
    # ax = sns.scatterplot(x="145480GOMO_d14_RGR", y="GCKO#2GOMO_d14_RGR", hue="Published_cross_phenotype", data=viz_df,legend='brief', \
    #                      palette=dict(female="#66c2a5", NA="#8da0cb", male="#fc8d62"))




    fig = ax.get_figure()
    fig.savefig(folder+ "rel_abundance_MG_B1.pdf")
    import pdb;pdb.set_trace()
    plt.figure(figsize=(8, 8))
    ax = sns.scatterplot(x="mean", y="MG_SD", hue="Phenotypes", data=cmb_df, legend='brief',s=10)
    # ax = sns.scatterplot(x="145480GOMO_d14_RGR", y="GCKO#2GOMO_d14_RGR", hue="Published_cross_phenotype", data=viz_df,legend='brief', \
    #                      palette=dict(female="#66c2a5", NA="#8da0cb", male="#fc8d62"))




    fig = ax.get_figure()
    fig.savefig(folder+ "phenotype_MG.pdf")

    plt.figure(figsize=(8, 8))
    ax = sns.scatterplot(x="mean", y="MG_rel", hue="Phenotypes", data=cmb_df, legend='brief',s=10)
    # ax = sns.scatterplot(x="145480GOMO_d14_RGR", y="GCKO#2GOMO_d14_RGR", hue="Published_cross_phenotype", data=viz_df,legend='brief', \
    #                      palette=dict(female="#66c2a5", NA="#8da0cb", male="#fc8d62"))

    # # we are going to plot figures
    # folder="/Users/vikash/Documents/Projects/mosquitostagescreen-master/Figures/"

    fig = ax.get_figure()
    fig.savefig(folder+ "phenotype_MG_rel.pdf")





    plt.figure(figsize=(8, 8))
    g=sns.catplot(x="Phenotypes", y="mean", kind="violin", dodge=False,data=cmb_df)
    ax=sns.swarmplot("Phenotypes", y="mean", color="k", size=3, data=cmb_df, ax=g.ax)

    # plt.show()
    # fig = ax.get_figure()
    fig = ax.get_figure()
    fig.savefig(folder+ "dist_MG.pdf")
    import pdb;pdb.set_trace()
    # plot for SG
    pdf=folder+"SG.pdf"
    plotfitScatter(cond_info[0][0],cond_info[1][1],'log2(relative_abundance)','SD',pdf,'SG')

    pdf=folder+"MG.pdf"
    plotfitScatter(cond_info[0][0],cond_info[2][1],'log2(relative_abundance)','SD',pdf,'MG')

    pdf=folder+"blood2.pdf"
    plotfitScatter(cond_info[0][0],cond_info[3][1],'log2(relative_abundance)','SD',pdf,'blood2')

    # plot for SG
    pdf=folder+"SG_rel.pdf"
    plotfitScatter(cond_info[0][0],cond_info[1][2],'log2(relative_abundance)','relative variance',pdf,'SG')

    pdf=folder+"MG_rel.pdf"
    plotfitScatter(cond_info[0][0],cond_info[2][2],'log2(relative_abundance)','relative variance',pdf,'MG')

    pdf=folder+"blood2_rel.pdf"
    plotfitScatter(cond_info[0][0],cond_info[3][2],'log2(relative_abundance)','relative variance',pdf,'blood2')

    ##
    pdf=folder+"passage_input_distribution.pdf"
    plothistNew(cond_info[0][0],'rel abundance_Passage',"Frequency",pdf,30,xlim=[-20,0])



def plotfitScatter(x,y,xlab,ylab,pdf,title):
    fig= plt.figure(figsize=(10,8))
    ax = plt.gca()

    p1=ax.scatter(x, y, color='black', marker='.')




    plt.xlabel(xlab,fontsize=20)
    plt.ylabel(ylab,fontsize=20)
    plt.xticks(fontsize=20)
    plt.yticks(fontsize=20)
    plt.title(title)
#     plt.legend(lines,['d0','d7','d14'],fontsize=15);
    plt.xlim([-20,0])
    plt.savefig(pdf,format="pdf")
    plt.close()
    # plt.show()


def plothistNew(values,xlab,ylab,pdf,bins,xlim):
    ## get relative abundance
    data = np.array(values)
    # remove nans
    data = data[~np.isnan(data)]
    fig= plt.figure(figsize=(10,8))
# ax = plt.gca()
    kwargs = dict(histtype='step', alpha=1, normed=True, bins=bins,facecolor='blue', linewidth=2)

    plt.hist(data, **kwargs)
    # plt.grid(True)
    plt.xlim(xlim)
    plt.xlabel(xlab,fontsize=20)
    plt.ylabel(ylab,fontsize=20)
    plt.xticks(fontsize=20)
    plt.yticks(fontsize=20)
    plt.savefig(pdf,format="pdf")


def getConditionValues(df,bio_df_dict,conditions):
    my_list=[k[1] for k in  bio_df_dict.keys()]
    my_list2=[k for k in  bio_df_dict.keys()]
    cond_info=[]
    cond_df=[]
    pool=df["Pool"].unique()

    for cond in conditions:
        c_mvals=[] # store mean value
        c_sd=[] # store sd value
        c_rel=[] # store rel sd value
        cmd_tmp=pd.DataFrame(columns=['mean', 'std', 'rel'])
        test_repeat=[]
        for p in pool:
            # import pdb;pdb.set_trace()
            tmp=bio_df_dict[(p,cond)]
            cmd_tmp=cmd_tmp.append(tmp[['mean', 'std', 'rel']])
            # for item in tmp.index:
            #     if item not in test_repeat:
            #         test_repeat.append(item)
            #     else:
            #         import pdb;pdb.set_trace()

            for item in tmp['mean']:
                c_mvals.append(item)

            for item in tmp['std']:
                c_sd.append(item)

            for item in tmp['rel']:
                c_rel.append(item)
        cond_df.append(cmd_tmp)
        cond_info.append([c_mvals,c_sd,c_rel])

    return cond_df,cond_info


def getdf_values(df):
    df_values=[]
    for t_values in df.values:
        for val in t_values:
            df_values.append(val)
    return df_values

def get_bio_pair(df,grp1,grp2):

    df_grp1=df.groupby(grp1)
    df_grp1_dict=df_grp1.indices # this is the dictionary
    my_list=[(k[0],k[1]) for k in  df_grp1_dict.keys()]
    my_list2=[k for k in  df_grp1_dict.keys()]

    # df_grp2=df.groupby(grp2)
    # df_grp2_dict=df_grp2.indices # this is the dictionary
    # my2_list=[(k[0],k[1]) for k in  df_grp2_dict.keys()]
    # my2_list2=[k for k in  df_grp2_dict.keys()]

    df_grp=df.groupby(grp2)
    df_tech_dict=df_grp.indices # this is the dictionary


    # replicates=df.Replicate.unique() # technical replicates
    # mouse=df.Mouse.unique() # mouse replicates
    new_dict={}
    for k in df_tech_dict.keys():
        vals = [my_list2[i] for i, x in enumerate(my_list) if x == k]
        new_dict[k]=vals
    return new_dict




def get_tech_pair(df,grp1,grp2):
    df_grp=df.groupby(grp1)
    df_grp_dict=df_grp.indices # this is the dictionary
    my_list=[(k[0],k[1],k[2]) for k in  df_grp_dict.keys()]
    my_list2=[k for k in  df_grp_dict.keys()]
    df_grp=df.groupby(grp2)
    df_tech_dict=df_grp.indices # this is the dictionary

    # replicates=df.Replicate.unique() # technical replicates
    # mouse=df.Mouse.unique() # mouse replicates
    new_dict={}
    for k in df_tech_dict.keys():
        vals = [my_list2[i] for i, x in enumerate(my_list) if x == k]
        new_dict[k]=vals
    return new_dict

def get_df_m_sd(df,grp1,tech_pair):
    df_grp=df.groupby(grp1)
    df_grp_dict=df_grp.indices # this is the dictionary
    dict_df={} # this is the dictionary of dataframe

    cols=[]
    for k,item in tech_pair.items():
        tmp=df.iloc[df_grp_dict[item[0]],:].copy()

        tmp.set_index("gene",  inplace=True)

        for it in item:
            tmp1=df.iloc[df_grp_dict[it],:].copy()
            tmp1.set_index("gene",  inplace=True)
            if it==('F', 'Rec', 2, 2):
                xx=tmp1.loc[:,['log_proportion']].copy()
                index1=[i for i in range(0, xx.shape[0], 2)]
                index2=[i for i in range(1, xx.shape[0], 2)]
                # import pdb;pdb.set_trace()
                tmp[it]=xx.iloc[index1,:].copy()
                cols.append(it)
            else:

                # tmp[it]=tmp.loc[:,'log_proportion'].copy() # this has a problem [('F', 'Rec', 2, 2)]
                tmp[it]=tmp1.loc[:,['log_proportion']].copy()




        tmp["mean"]=tmp[item].mean(axis=1).copy()
        tmp["std"]=tmp[item].std(axis=1).copy()
        tmp["rel"]=abs(tmp["std"].div(tmp["mean"]))
        # import pdb;pdb.set_trace()
        dict_df[k]=tmp
    # we will calculate mean and standered deviation
    print (cols)
    return dict_df

if __name__ == "__main__":
    #calRelAbundanceRedo() #This script is to cal culate relative abundances
    #testDist()
    #weightedMeanAnalysis()
    error_liver()
