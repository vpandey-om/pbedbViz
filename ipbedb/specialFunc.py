import plotly
import plotly.graph_objs as go

import pandas as pd
import numpy as np
import json
from ipbedb import db,DATABASE_URI
from ipbedb.db_model import Cluster,Geneanot,Ap2time,Ap2timemanifest,Phenodata

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
import plotly.figure_factory as ff
from plotly.subplots import make_subplots
import plotly.graph_objs as go
import plotly.express as px

from ipbedb import malaria_atlas_list



engine = create_engine(DATABASE_URI)
psqldb = scoped_session(sessionmaker(bind=engine))




def create_plot():
    fig,cluster_gene_logfc,cluster_gene_rapa_yes,cluster_gene_rapa_no,cluster_name=getCluster()
    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

    return graphJSON

def create_dendrogram_for_cluster(clust_name):
    '''Cluster name is comming from the click event'''
    # get index
    try:
        cluster=Cluster.query.filter_by(name=clust_name.split('(')[0].strip()).first()
    except:
        print ('We cannot find clusters')

    # get genes of cluster
    ap2timemanifest_df, ap2time_df,dict_index=create_time_dataframe()

    genes=Geneanot.query.filter_by(cluster=cluster).all()
    if len(genes)>0:
        pbankaids=[item.pbankaNewID for item in genes]
        descriptions=[item.description[:40] for item in genes]
        labels = [i + '|'+j for i, j in zip(pbankaids, descriptions)]
        t_df_yes=pd.DataFrame(index=pbankaids)
        t_df_no=pd.DataFrame(index=pbankaids)
        time=['0h','2h','4h','6h','12h','18h','24h','30h']

        for t in time:
            t_df_yes[t]=np.nan
            t_df_yes.loc[:,t]=ap2time_df.loc[pbankaids,ap2timemanifest_df['name'][dict_index[('YES',t)]].to_list()].mean(axis=1)
            t_df_no[t]=np.nan
            t_df_no.loc[:,t]=ap2time_df.loc[pbankaids,ap2timemanifest_df['name'][dict_index[('NO',t)]].to_list()].mean(axis=1)
        logfc_df=t_df_yes-t_df_no

        X=logfc_df.to_numpy()

        fig = ff.create_dendrogram(X, orientation='right', labels=labels )
        fig['layout']['yaxis']['side']='right'

        # import pdb;pdb.set_trace()
        # add marker
        y=list(fig['layout']['yaxis']['tickvals'])
        new_labels=list(fig['layout']['yaxis']['ticktext'])
        x=np.full((1, len(y)), .1)[0]
        size=np.full((1, len(y)), 12    )[0]
        symbol=np.full((1, len(y)),  'circle')[0]
        color=np.full((1, len(y)),  '#AED6F1')[0]
        # symbol[tid]='circle'
        # fig2.add_trace(go.Scatter(mode='markers',x=x,y=y,opacity=1,name='male',text=new_labels,hoverinfo='text',marker=dict(size=size,color=color,symbol=symbol)))
        fig.add_trace(go.Scatter(mode='markers',x=x,y=y,opacity=1,text=new_labels,hoverinfo='text',
        marker=dict(size=size,color=color,symbol=symbol)))
        height=1500
        if len(y)>50:
            height=int((len(y)/50)*1500)

        fig.update_layout(width=800, height=height,title={'text':clust_name,'x':0.5})




        graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
        return graphJSON



def create_time_dataframe():
    ''' we are going to make dataFrame from sql '''
    ap2timemanifest_df = pd.read_sql_query('select * from "ap2timemanifest"',con=engine)
    ap2time_df = pd.read_sql_query('select * from "ap2time"',con=engine)
    ap2time_df.set_index('name',inplace=True)
    dict_index=ap2timemanifest_df.groupby(['rapamycin','time']).indices

    return ap2timemanifest_df, ap2time_df,dict_index



def getCluster():
    ''' We are going to get clusters from the database pbe_db'''
    # get all clusters

    try:
        clusters=Cluster.query.all()
    except:
        print ('We cannot find clusters')
    if len(clusters)>0: # we found clusters
        ## all samples of time series data
        ap2timemanifest_df, ap2time_df,dict_index=create_time_dataframe()
        time=['0h','2h','4h','6h','12h','18h','24h','30h'] ### we need to plot on this time
        ## store cluster_wise_informations

        cluster_name=[]
        cluster_short_name=[]
        cluster_gene_logfc=[] ## This is the the log fold change for gene wise
        cluster_gene_rapa_yes=[] ## This is dataFrame for rapamycin YES
        cluster_gene_rapa_no=[] ## This is dataFrame rapamycin no
        cluster_dist=[] ## with this we will compute distance between clusters

        for cluster in clusters:
            genes=Geneanot.query.filter_by(cluster=cluster).all()
            if len(genes)>0:

                pbankaids=[item.pbankaNewID for item in genes]
                cluster_name.append(cluster.name+' ( %d )'%len(pbankaids))
                cluster_short_name.append(cluster.name)
                ## get mean of rapamycin treatment
                t_df_yes=pd.DataFrame(index=pbankaids)
                t_df_no=pd.DataFrame(index=pbankaids)
                for t in time:

                    t_df_yes[t]=np.nan
                    t_df_yes.loc[:,t]=ap2time_df.loc[pbankaids,ap2timemanifest_df['name'][dict_index[('YES',t)]].to_list()].mean(axis=1)
                    t_df_no[t]=np.nan
                    t_df_no.loc[:,t]=ap2time_df.loc[pbankaids,ap2timemanifest_df['name'][dict_index[('NO',t)]].to_list()].mean(axis=1)

                ## average Expressio of the cluster
                avg_yes=t_df_yes.mean(axis=0)
                cluster_gene_rapa_yes.append(avg_yes)
                avg_no=t_df_no.mean(axis=0)
                cluster_gene_rapa_no.append(avg_no)
                ## log2 fold chnage
                logfc=avg_yes-avg_no

                ## genewise fold change
                logfc_gene=t_df_yes-t_df_no
                cluster_gene_logfc.append(logfc_gene)
                cluster_dist.append(logfc.to_list())
            else:
                print('There is not any genes in the cluster')
            ## now we are going to plot

        fig = make_subplots(rows=8, cols=8,subplot_titles=tuple(cluster_short_name))
        counter=0
        x=[0,2,4,6,12,18,24,30]
        for i in range(8):
            for j in range(8):
                trace=go.Scatter(mode='markers+lines',x=x,y=cluster_dist[counter],name='',marker=dict(size=3,color='black'))

                fig.append_trace(trace,row=i+1, col=j+1)
                trace1=go.Scatter(mode='markers',x=[3],y=[7],name='',marker=dict(size=15,color='#79443b'),hoverinfo='text',text=cluster_name[counter])
                counter=counter+1
                fig.append_trace(trace1,row=i+1, col=j+1)
                fig.update_yaxes(row=i+1, col=j+1,range=[-9,9])
                fig.update_xaxes(row=i+1, col=j+1,range=[0,30])
        fig.update_yaxes(title_text="logFC",row=1, col=1,)
        fig.update_xaxes(title_text="hour",row=1, col=1)
        # import pdb;pdb.set_trace()

        # fig.append_trace(trace_d0_female,row=1, col=1)
        # fig.append_trace(trace_d0_male,row=1, col=2)
        # fig.append_trace(trace_d13_female,row=2, col=1)
        #
        # fig.append_trace(trace_d13_male,row=2, col=2)

        # X = np.array(cluster_dist) # 15 samples, with 10 dimensions each
        # fig = ff.create_dendrogram(X, orientation='right', labels=cluster_name )
        # fig['layout']['yaxis']['side']='right'
        # fig.update_layout(width=800, height=1500)
        # # import pdb;pdb.set_trace()
        # # add marker
        # y=list(fig['layout']['yaxis']['tickvals'])
        # new_labels=list(fig['layout']['yaxis']['ticktext'])
        # x=np.full((1, len(y)), .1)[0]
        # size=np.full((1, len(y)), 12    )[0]
        # symbol=np.full((1, len(y)),  'circle')[0]
        # color=np.full((1, len(y)),  '#AED6F1')[0]
        # # symbol[tid]='circle'
        # # fig2.add_trace(go.Scatter(mode='markers',x=x,y=y,opacity=1,name='male',text=new_labels,hoverinfo='text',marker=dict(size=size,color=color,symbol=symbol)))
        # fig.add_trace(go.Scatter(mode='markers',x=x,y=y,opacity=1,text=new_labels,hoverinfo='text',
        # marker=dict(size=size,color=color,symbol=symbol)))
        # import pdb;pdb.set_trace()
        # fig.show()
        # import pdb;pdb.set_trace()
        fig.update_layout(width=1000, height=1200,showlegend=False)
        # fig.update_layout(showlegend=False)
        print('results')
        return fig,cluster_gene_logfc,cluster_gene_rapa_yes,cluster_gene_rapa_no,cluster_name


def create_plots_for_gene_old(gene):
    ''' This function will plot timegraph of each genes and phenotypes'''
    print(gene)
    ### plot time graph for this gene
    g=Geneanot.query.filter_by(pbankaNewID=gene).first()

    ap2timemanifest_df = pd.read_sql_query('select * from "ap2timemanifest"',con=engine)
    dict_index=ap2timemanifest_df.groupby(['rapamycin','time']).indices
    gene_df=pd.DataFrame(columns=['time','exp_data','rapamycin'])
    time=['0h','2h','4h','6h','12h','18h','24h','30h']
    filtered_df=ap2timemanifest_df.loc[ap2timemanifest_df.time.isin(time),:].copy().reset_index()

    data=[]
    for sample in filtered_df['name'].to_list():
        data.append(getattr(g.ap2time, "%s"%sample))


    gene_df['exp_data']=data
    gene_df['time']=filtered_df['time'].copy()
    gene_df['rapamycin']=filtered_df['rapamycin'].copy()
    yes_idx=gene_df.groupby(['rapamycin']).indices['YES']
    no_idx=gene_df.groupby(['rapamycin']).indices['NO']
    specs = [[{}, {}], [{'type':'domain'}, {"type": "table"}],[{}, {}]]
    fig= make_subplots(rows=3, cols=2,subplot_titles=tuple([gene,gene,gene,gene,'Malaria Life Cycle',gene]),specs=specs)
    fig.add_trace(go.Box(
    y=gene_df['exp_data'][yes_idx],
    x=gene_df['time'][yes_idx],
    name='rapamycin +',
    marker_color='#3D9970'
    ),row=1,col=1)

    fig.add_trace(go.Box(
    y=gene_df['exp_data'][no_idx],
    x=gene_df['time'][no_idx],
    name='rapamycin -',
    marker_color='#FF4136'
    ),row=1,col=1)

    # fig = px.box(gene_df,
    # y='exp_data',
    # x='time',
    # color='rapamycin',
    # )
    fig.update_yaxes(title_text="log2 (expression)",row=1, col=1)
    fig.update_xaxes(title_text="hour",row=1, col=1)


    ## now we are going to plot AP2KO
    ap2komanifest = pd.read_sql_query('select * from "ap2komanifest"',con=engine)
    KOs=['wt_S','ap2_g_S','ap2_g2_S','ap2_o_S', 'ap2_o2_S', 'ap2_o3_S', 'ap2_o4_S','ap2_sp_S','ap2_sp2_S', 'ap2_sp3_S', 'ap2_l_S','t131970_S','wt_G','ap2_o_G','ap2_o3_G','ap2_o2_G', 'wt_O','ap2_o_O','ap2_o2_O', 'ap2_o3_O' ]
    for ko in KOs:
        tmp=ap2komanifest.loc[ap2komanifest['shortName']==ko,:].copy()

        if not tmp.empty:
            data=[]
            for sample in tmp['name'].to_list():
                data.append(getattr(g.ap2koexp, "%s"%sample))

            ## add trace

            fig.add_trace(go.Box(
            y=np.log2(np.array(data)),
            x=tmp['shortName'].to_list(),
            name=tmp['shortName'].to_list()[0],
            marker_color='#FF851B',
            showlegend=False
            ),row=1,col=2)
        else:

            print('There is no data ')
            fig.add_trace(go.Box(),row=1,col=2)
    fig.update_yaxes(title_text="log2 (expression)",row=1, col=2)
    fig.update_xaxes(title_text="ApiAP2 KOs at Different Life Cycle Stages",row=1, col=2)


    ### make pie chart and table for phenotype data

    ### colors
    ## 'Dispensable'          'Essential',
    ## 'Slow'                  'Fast',
    ## 'Insufficient data'    'reduced'   'nopower'  'notreduced'
    ###

    colors_dict={'Dispensable':'#31a354','Essential':'#de2d26','Fast':'#dd1c77','Slow':'#2c7fb8',
    'Insufficient data':'#636363','reduced':'#de2d26','nopower':'#2c7fb8','notreduced':'#31a354','other':'#f0f0f0'}
    ## if data is not avaialable then we make pie chart default
    labels = ['B2 to MG','MG to SG','SG to B2','Blood']
    values = [25, 25, 25, 25]
    # g.phenodata_id=1142
    if g.phenodata_id == None:
        colors=['#f0f0f0','#f0f0f0','#f0f0f0','#f0f0f0']
        pheno_calls=['NA','NA','NA','NA']
        RGRs=[np.nan,np.nan,np.nan,np.nan]
        SDs=[np.nan,np.nan,np.nan,np.nan]
    else:

        pheno=Phenodata.query.filter_by(id=g.phenodata_id).first()
        cols=['blood_pheno','B2toMG_pheno','MGtoSG_pheno','SGtoB2_pheno']
        RGR_cols=['blood_RGR','B2toMG_RGR','MGtoSG_RGR','SGtoB2_RGR']
        SD_cols=['blood_SD','B2toMG_SD','MGtoSG_SD','SGtoB2_SD']
        colors=[]
        pheno_calls=[]
        RGRs=[]
        SDs=[]

        for i, col in enumerate(cols):
            pheno_call=getattr(pheno,col)
            if pheno_call in colors_dict.keys():
                colors.append(colors_dict[pheno_call])
                pheno_calls.append(pheno_call)
                RGRs.append(getattr(pheno,RGR_cols[i]))
                SDs.append(getattr(pheno,SD_cols[i]))
            else:
                colors.append(colors_dict['other'])
                pheno_calls.append('NA')
                RGRs.append(np.nan)
                SDs.append(np.nan)
    # import pdb;pdb.set_trace()
    hovertext=[ i+':'+ j for i,j in zip(labels,pheno_calls)]
    print(hovertext)
    fig.add_trace(go.Pie(labels=hovertext,values=values,marker_colors=colors,marker_line_width=2),2,1)
    # fig.update_traces(textinfo='none')

    ## make table on 2 2 position
    phenotype_df=pd.DataFrame(columns=['Experiment','RGR','SD','Phenocall'])
    phenotype_df['Experiment']= labels
    phenotype_df['RGR']= RGRs
    phenotype_df['SD']= SDs
    phenotype_df['Phenocall']= pheno_calls
    phenotype_df['RGR'] = phenotype_df['RGR'].map(u"{:,.2f}".format)
    phenotype_df['SD'] = phenotype_df['SD'].map(u"{:,.2f}".format)
    ## now make table with phenotype dataframe
    fig.add_trace(go.Table(
    header=dict(values=list(phenotype_df.columns),
                line_color='darkslategray',
                fill_color='royalblue',
                align=['left','center'],
                font=dict(color='white', size=12),
                height=40
                ),
    cells=dict(values=[phenotype_df.Experiment, phenotype_df.RGR, phenotype_df.SD, phenotype_df.Phenocall],
            line_color='darkslategray',
            fill=dict(color=['paleturquoise', 'white']),
            align=['left', 'center'],
            font_size=12,
            height=30
            )),row=2,col=2)

    ### add single cell data

    umap_df['stage']=pheno_df.loc[umap_df.index,'ShortenedLifeStage3'].astype('category')
    umap_df['color'] = umap_df.stage.cat.codes
    fig.add_trace(go.Scatter(x=umap_df['umap0'],
               y=umap_df['umap1'],
               mode='markers',
               marker=dict(
               size=5,
               color=umap_df['color'], #set color equal to a variable
               # colorscale='Viridis', # one of plotly colorscales
               # showscale=True
                ),
               text=pheno_df.loc[umap_df.index,'ShortenedLifeStage3']),row=3,col=1)

    fig.update_layout(width=1000, height=1500,showlegend=True)
    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    return graphJSON


def getFigureAp2OverExp(g,gene):
    ''' get box plot with rapamycin + and - and Ap2 over expression'''
    time=['0h','2h','4h','6h','12h','18h','24h','30h']
    ap2timemanifest_df = pd.read_sql_query('select * from "ap2timemanifest"',con=engine)
    dict_index=ap2timemanifest_df.groupby(['rapamycin','time']).indices
    gene_df=pd.DataFrame(columns=['time','exp_data','rapamycin'])

    filtered_df=ap2timemanifest_df.loc[ap2timemanifest_df.time.isin(time),:].copy().reset_index()

    data=[]
    for sample in filtered_df['name'].to_list():
        if not (g.ap2time==None):
            data.append(getattr(g.ap2time, "%s"%sample))
        else:
            data.append(np.nan)



    gene_df['exp_data']=data
    gene_df['time']=filtered_df['time'].copy()
    gene_df['rapamycin']=filtered_df['rapamycin'].copy()
    yes_idx=gene_df.groupby(['rapamycin']).indices['YES']
    no_idx=gene_df.groupby(['rapamycin']).indices['NO']

    specs=[[{}]]
    fig= make_subplots(rows=1, cols=1,subplot_titles=tuple([gene]),specs=specs)
    fig.add_trace(go.Box(
    y=gene_df['exp_data'][yes_idx],
    x=gene_df['time'][yes_idx],
    name='rapamycin +',
    marker_color='#3D9970'
    ),row=1,col=1)

    fig.add_trace(go.Box(
    y=gene_df['exp_data'][no_idx],
    x=gene_df['time'][no_idx],
    name='rapamycin -',
    marker_color='#FF4136'
    ),row=1,col=1)

    # fig = px.box(gene_df,
    # y='exp_data',
    # x='time',
    # color='rapamycin',
    # )
    fig.update_yaxes(title_text="log2 (expression)",row=1, col=1)
    fig.update_xaxes(title_text="hour",row=1, col=1)
    fig.update_layout(title='Ap2G overexpression',width=500, height=500,showlegend=True)
    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    return graphJSON

def getFigureAp2KOs(g,gene):
    ''' get box plot for AP2KOs'''
    ap2komanifest = pd.read_sql_query('select * from "ap2komanifest"',con=engine)
    KOs=['wt_S','ap2_g_S','ap2_g2_S','ap2_o_S', 'ap2_o2_S', 'ap2_o3_S', 'ap2_o4_S','ap2_sp_S','ap2_sp2_S', 'ap2_sp3_S', 'ap2_l_S','t131970_S','wt_G','ap2_o_G','ap2_o3_G','ap2_o2_G', 'wt_O','ap2_o_O','ap2_o2_O', 'ap2_o3_O' ]
    specs=[[{}]]
    fig= make_subplots(rows=1, cols=1,subplot_titles=tuple([gene]),specs=specs)
    for ko in KOs:
        tmp=ap2komanifest.loc[ap2komanifest['shortName']==ko,:].copy()
        # if gene=='PBANKA_1410950':
        #     import pdb;pdb.set_trace()
        if not tmp.empty:
            data=[]
            for sample in tmp['name'].to_list():
                if not (g.ap2koexp==None):
                    data.append(getattr(g.ap2koexp, "%s"%sample))
                else:
                    data.append(np.nan)

            ## add trace

            fig.add_trace(go.Box(
            y=np.log2(np.array(data)),
            x=tmp['shortName'].to_list(),
            name=tmp['shortName'].to_list()[0],
            marker_color='#FF851B',
            showlegend=False
            ),row=1,col=1)
        else:

            print('There is no data ')
            fig.add_trace(go.Box(),row=1,col=2)
    fig.update_yaxes(title_text="log2 (expression)",row=1, col=1)
    fig.update_xaxes(title_text="ApiAP2 KOs at Different Life Cycle Stages",row=1, col=1)
    fig.update_layout(width=500, height=500,showlegend=False)
    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    return graphJSON

def getFigurePhenoPieTable(g,gene):
    ''' get phenotype pie chart and table'''
    ### colors
    ## 'Dispensable'          'Essential',
    ## 'Slow'                  'Fast',
    ## 'Insufficient data'    'reduced'   'nopower'  'notreduced'
    ###
    specs =  [[{'type':'domain'}, {"type": "table"}]]
    fig= make_subplots(rows=1, cols=2,subplot_titles=tuple([gene]),specs=specs,column_widths=[0.3, 0.7])
    colors_dict={'Dispensable':'#31a354','Essential':'#de2d26','Fast':'#dd1c77','Slow':'#2c7fb8',
    'Insufficient data':'#636363','reduced':'#de2d26','nopower':'#2c7fb8','notreduced':'#31a354','other':'#f0f0f0'}
    ## if data is not avaialable then we make pie chart default
    labels = ['B2 to MG','MG to SG','SG to B2','Blood']
    values = [25, 25, 25, 25]
    # g.phenodata_id=1142
    if g.phenodata_id == None:
        colors=['#f0f0f0','#f0f0f0','#f0f0f0','#f0f0f0']
        pheno_calls=['NA','NA','NA','NA']
        RGRs=[np.nan,np.nan,np.nan,np.nan]
        SDs=[np.nan,np.nan,np.nan,np.nan]
    else:

        pheno=Phenodata.query.filter_by(id=g.phenodata_id).first()
        cols=['blood_pheno','B2toMG_pheno','MGtoSG_pheno','SGtoB2_pheno']
        RGR_cols=['blood_RGR','B2toMG_RGR','MGtoSG_RGR','SGtoB2_RGR']
        SD_cols=['blood_SD','B2toMG_SD','MGtoSG_SD','SGtoB2_SD']
        colors=[]
        pheno_calls=[]
        RGRs=[]
        SDs=[]

        for i, col in enumerate(cols):
            pheno_call=getattr(pheno,col)
            if pheno_call in colors_dict.keys():
                colors.append(colors_dict[pheno_call])
                pheno_calls.append(pheno_call)
                RGRs.append(getattr(pheno,RGR_cols[i]))
                SDs.append(getattr(pheno,SD_cols[i]))
            else:
                colors.append(colors_dict['other'])
                pheno_calls.append('NA')
                RGRs.append(np.nan)
                SDs.append(np.nan)
    # import pdb;pdb.set_trace()
    hovertext=[ i+':'+ j for i,j in zip(labels,pheno_calls)]
    print(hovertext)
    fig.add_trace(go.Pie(labels=hovertext,values=values,marker_colors=colors,hole=.3,marker_line_width=2),1,1)
    # fig.update_traces(textinfo='none')

    ## make table on 2 2 position
    phenotype_df=pd.DataFrame(columns=['Experiment','RGR','SD','Phenocall'])
    phenotype_df['Experiment']= labels
    phenotype_df['RGR']= RGRs
    phenotype_df['SD']= SDs
    phenotype_df['Phenocall']= pheno_calls
    phenotype_df['RGR'] = phenotype_df['RGR'].map(u"{:,.2f}".format)
    phenotype_df['SD'] = phenotype_df['SD'].map(u"{:,.2f}".format)
    ## now make table with phenotype dataframe
    fig.add_trace(go.Table(
    header=dict(values=list(phenotype_df.columns),
                line_color='darkslategray',
                fill_color='royalblue',
                align=['left','center'],
                font=dict(color='white', size=12),
                height=40
                ),
    cells=dict(values=[phenotype_df.Experiment, phenotype_df.RGR, phenotype_df.SD, phenotype_df.Phenocall],
            line_color='darkslategray',
            fill=dict(color=['paleturquoise', 'white']),
            align=['left', 'center'],
            font_size=12,
            height=30
            )),row=1,col=2)


    fig.update_layout(title="Phenotype data", width=1000, height=500,showlegend=True)
    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    return graphJSON


def getfigMalariaAtlasSatge():

    ## this data is for malaria cell atlas visualizations
    umap_df=malaria_atlas_list[0] # umap_df
    pheno_df=malaria_atlas_list[1] ## pheno_df
    # atals_sparse_data=malaria_atlas_list[2] ### sparse numpy array
    # atlas_genes=malaria_atlas_list[3]
    ###

    ### add single cell data
    # specs=[[{}]]
    # fig= make_subplots(rows=1, cols=1,subplot_titles=tuple(['Malaria Life Cycle']),specs=specs)

    umap_df['stage']=pheno_df.loc[umap_df.index,'ShortenedLifeStage3'].copy()
    # fig.add_trace(go.Scatter(x=umap_df['umap0'],
    #            y=umap_df['umap1'],
    #            mode='markers',
    #            marker=dict(
    #            size=5,
    #            color=umap_df['color'], #set color equal to a variable
    #            # colorscale='Viridis', # one of plotly colorscales
    #            # showscale=True
    #             ),
    #            text=pheno_df.loc[umap_df.index,'ShortenedLifeStage3']),row=1,col=1)
    umap_df=umap_df.replace({'Male':'Male_gametocyte'})
    fig = px.scatter(umap_df, x='umap0', y='umap1', color='stage')
    fig.update_traces(marker=dict(size=4))
    fig.update_layout(title="Malaria Cell Atlas",width=500, height=400,showlegend=True)
    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    return graphJSON


def getfigMalariaAtlasGene(gene):

    ## this data is for malaria cell atlas visualizations
    umap_df=malaria_atlas_list[0] # umap_df
    pheno_df=malaria_atlas_list[1] ## pheno_df
    atlas_sparse_data=malaria_atlas_list[2] ### sparse numpy array
    atlas_genes=malaria_atlas_list[3]
    ### find index for a gene
    umap_df=umap_df.replace({'Male':'Male_gametocyte'})
    if len(atlas_genes[atlas_genes==gene].to_list())>0:
        umap_df['expression']=np.nan
        arr=atlas_sparse_data.todense()
        umap_df['expression']=arr[atlas_genes==gene,:].tolist()[0]
        fig = px.scatter(umap_df, x='umap0', y='umap1', color='expression')
        fig.update_traces(marker=dict(size=4))
        fig.update_layout(title=gene,width=500, height=400,showlegend=True)

    else:
        umap_df['expression']=1
        fig = px.scatter(umap_df, x='umap0', y='umap1', color='expression')
        fig.update_traces(marker=dict(size=4))
        fig.update_layout(title='Not found',width=500, height=400,showlegend=True)





    ### add single cell data
    # specs=[[{}]]
    # fig= make_subplots(rows=1, cols=1,subplot_titles=tuple(['Malaria Life Cycle']),specs=specs)

    # umap_df['stage']=pheno_df.loc[umap_df.index,'ShortenedLifeStage3'].copy()
    # fig.add_trace(go.Scatter(x=umap_df['umap0'],
    #            y=umap_df['umap1'],
    #            mode='markers',
    #            marker=dict(
    #            size=5,
    #            color=umap_df['color'], #set color equal to a variable
    #            # colorscale='Viridis', # one of plotly colorscales
    #            # showscale=True
    #             ),
    #            text=pheno_df.loc[umap_df.index,'ShortenedLifeStage3']),row=1,col=1)
    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    return graphJSON



def create_plots_for_gene(gene):
    ''' This function will plot timegraph of each genes and phenotypes'''
    print(gene)
    ### plot time graph for this gene
    g=Geneanot.query.filter_by(pbankaNewID=gene).first()

    fig_ap2time=getFigureAp2OverExp(g,gene)
    ## now we are going to plot AP2KO
    fig_ap2KO=getFigureAp2KOs(g,gene)

    ### make pie chart and table for phenotype data
    fig_pheno=getFigurePhenoPieTable(g,gene)

    # for malaria cell atlas
    fig_atlas_stage=getfigMalariaAtlasSatge()

    fig_atlas_gene=getfigMalariaAtlasGene(gene)

    return fig_ap2time,fig_ap2KO,fig_pheno,fig_atlas_stage,fig_atlas_gene





            ## get time data
