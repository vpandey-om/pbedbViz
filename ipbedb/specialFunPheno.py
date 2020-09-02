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
from flask import jsonify
from ipbedb import malaria_atlas_list
# pd.options.display.float_format = '{:,.2f}'.format

### color setting
change_color_fertility={'Reduced':'#fc8d59','Not Reduced':'#91bfdb','No Power':'#ffffbf','Increased':'#91bfdb'}
change_color_gam={'reduced':'#fc8d59','notreduced':'#91bfdb','nopower':'#ffffbf'}
change_label_liver={'reduced':'Reduced','notreduced':'Not Reduced','nopower':'No Power'}
change_color_liver={'Reduced':'#fc8d59','Not Reduced':'#91bfdb','No Power':'#ffffbf'}
change_color_blood={'Slow':'#fdae61', 'Dispensable':'#abd9e9', 'Fast':'#2c7bb6', 'Essential':'#d7191c', 'Insufficient data':'#ffffbf'}
change_color_all_pheno={'Slow':'#fdae61', 'Dispensable':'#abd9e9', 'Fast':'#2c7bb6', 'Essential':'#d7191c', 'Insufficient data':'#ffffbf','Reduced':'#fc8d59','Not Reduced':'#91bfdb','No Power':'#ffffbf'}


###
engine = create_engine(DATABASE_URI)
psqldb = scoped_session(sessionmaker(bind=engine))

phenodata_df = pd.read_sql_query('select * from "phenodata"',con=engine)

genes=[ ]
description=[]
for item in phenodata_df['name']:
    gene=Geneanot.query.filter_by(pbankaNewID=item).first()
    try:
        description.append(gene.description)
    except:
        description.append(item)


phenodata_df['description']=description

pheno_tmp=phenodata_df.copy()
phenodf_all=phenodata_df.copy()
pheno_tmp=pheno_tmp.drop(['id'], axis=1)

pheno_tmp.set_index('name',inplace=True)

for col in pheno_tmp.columns:
    try:
        pheno_tmp[col]=pheno_tmp[col].map(u"{:,.3f}".format)
    except:
        pass


###

def separate_df():
    ''' We are going to sperate dataframe  '''

    ### Fertility
    female_idx=phenodata_df.loc[~phenodata_df['female_fertility_SD'].isna()].index.values
    male_idx=phenodata_df.loc[~phenodata_df['male_fertility_SD'].isna()].index.values

    if (female_idx==male_idx).all():

        columns=['name','female_fertility_SD','female_fertility_RGR','female_fertility_pheno','male_fertility_SD','male_fertility_RGR','male_fertility_pheno']
        pheno_fertility_df=phenodata_df.loc[female_idx,columns]
    else:
        print('why mutants in male and female are not equal. fix')


    ### Gametocyte

    female_idx=phenodata_df.loc[~phenodata_df['female_gam_SD'].isna()].index.values
    male_idx=phenodata_df.loc[~phenodata_df['male_gam_SD'].isna()].index.values

    if (female_idx==male_idx).all():

        columns=['name','female_gam_SD','female_gam_RGR','female_gam_pheno','male_gam_SD','male_gam_RGR','male_gam_pheno']
        pheno_gam_df=phenodata_df.loc[female_idx,columns]


    else:
        print('please check why number of male and female are diffrent')

    ### Liver

    liver_idx=phenodata_df.loc[~phenodata_df['SGtoB2_RGR'].isna()].index.values

    columns=['name','SGtoB2_SD','SGtoB2_RGR','SGtoB2_pheno']
    pheno_liver_df=phenodata_df.loc[liver_idx,columns]
    pheno_liver_df["SGtoB2_pheno"]=pheno_liver_df["SGtoB2_pheno"].replace(change_label_liver)
    pheno_liver_df['confidence']=-np.log2(pheno_liver_df['SGtoB2_SD'])

    ## blood

    blood_idx=phenodata_df.loc[~phenodata_df['blood_RGR'].isna()].index
    blood_idx_sd=phenodata_df.loc[~phenodata_df['blood_SD'].isna()].index
    no_sd_idx=set(blood_idx)-set(blood_idx_sd)

    columns=['name','blood_SD','blood_RGR','blood_pheno']
    pheno_blood_df=phenodata_df.loc[blood_idx,columns]

    ### change on log 2 scale
    pheno_blood_df['blood_SD']=pheno_blood_df['blood_SD'].fillna(pheno_blood_df['blood_SD'].max())
    pheno_blood_df['blood_SD_log2']=(1/np.log(2))*pheno_blood_df['blood_SD']/pheno_blood_df['blood_RGR']
    pheno_blood_df['blood_RGR_log']=np.log2(pheno_blood_df['blood_RGR'])
    pheno_blood_df['confidence']=-np.log2(pheno_blood_df['blood_SD'])

    return pheno_fertility_df,pheno_gam_df,pheno_liver_df,pheno_blood_df


### assign global dataframe
pheno_fertility_df,pheno_gam_df,pheno_liver_df,pheno_blood_df=separate_df()


### get a combined figure for a gene


def getCombinedPhenoFig(geneid='PBANKA_0407500'):
    ''' We are going to combine all phenotypic data for a gene'''

    ##
    tmp_fertility=pheno_fertility_df[pheno_fertility_df['name']==geneid].copy()
    tmp_gam=pheno_gam_df[pheno_gam_df['name']==geneid].copy()
    tmp_liver=pheno_liver_df[pheno_liver_df['name']==geneid].copy()
    tmp_blood=pheno_blood_df[pheno_blood_df['name']==geneid].copy()
    ### initialize
    rgr, rgr_err, stages, phenoCall = ([] for i in range(4))
    ### for fertility
    if not tmp_fertility.empty:
        rgr.append(tmp_fertility['female_fertility_RGR'].to_list()[0])
        rgr.append(tmp_fertility['male_fertility_RGR'].to_list()[0])
        rgr_err.append(tmp_fertility['female_fertility_SD'].to_list()[0])
        rgr_err.append(tmp_fertility['male_fertility_SD'].to_list()[0])
        stages.append('Female Fertility')
        stages.append('Male Fertility')
        phenoCall.append(tmp_fertility['female_fertility_pheno'].to_list()[0])
        phenoCall.append(tmp_fertility['male_fertility_pheno'].to_list()[0])
    ### for gametocytes
    if not tmp_gam.empty:
        rgr.append(tmp_gam['female_gam_RGR'].to_list()[0])
        rgr.append(tmp_gam['male_gam_RGR'].to_list()[0])
        rgr_err.append(tmp_gam['female_gam_SD'].to_list()[0])
        rgr_err.append(tmp_gam['male_gam_SD'].to_list()[0])
        stages.append('Female Gametocyte')
        stages.append('Male Gametocyte')
        phenoCall.append(tmp_gam['female_gam_pheno'].to_list()[0])
        phenoCall.append(tmp_gam['male_gam_pheno'].to_list()[0])
    if not tmp_liver.empty:
        rgr.append(tmp_liver['SGtoB2_RGR'].to_list()[0])
        rgr_err.append(tmp_liver['SGtoB2_SD'].to_list()[0])
        stages.append('Liver phenoype')
        phenoCall.append(tmp_liver['SGtoB2_pheno'].to_list()[0])

    if not tmp_blood.empty:
        rgr.append(tmp_blood['blood_RGR_log'].to_list()[0])
        rgr_err.append(tmp_blood['blood_SD_log2'].to_list()[0])
        stages.append('Blood phenoype')
        phenoCall.append(tmp_blood['blood_pheno'].to_list()[0])

    ## now we need to plot

    df=pd.DataFrame()
    df['rgr']=rgr
    df['err']=rgr_err
    df['stages']=stages
    df['call']=phenoCall
    df['call']=df['call'].replace(change_label_liver)

    fig= px.scatter(df, x='rgr', y='stages', color='call',
                labels={
                     'rgr': 'RGR',
                     'stages': 'Stages',
                     "call": "Phenoype",
                 },color_discrete_map=change_color_all_pheno,
                 hover_name="call",error_x='err')
    ####
    fig.update_traces(marker=dict(size=20),selector=dict(mode='markers'))
    fig.update_layout(title="%s"%geneid, width=1000, height=500)
    fig['layout']['xaxis'].update( range=[-16, 16])
    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    # graphJSON = json.dumps(table, cls=plotly.utils.PlotlyJSONEncoder)
    return graphJSON





def getPhenoTable(gneList):
    ''' get phenotype pie chart and table'''
    ### colors
    ## 'Dispensable'          'Essential',
    ## 'Slow'                  'Fast',
    ## 'Insufficient data'    'reduced'   'nopower'  'notreduced'
    ###

    genes=[Geneanot.query.filter_by(pbankaNewID=item).first() for item in gneList]

    specs =  [[ {"type": "table"}]]
    fig= make_subplots(rows=1, cols=1,specs=specs)
    colors_dict={'Dispensable':'#31a354','Essential':'#de2d26','Fast':'#dd1c77','Slow':'#2c7fb8',
    'Insufficient data':'#636363','reduced':'#de2d26','nopower':'#2c7fb8','notreduced':'#31a354','other':'#f0f0f0'}
    gene_cols=['geneID','old_geneID','Description','shortName']
    pheno_cols=['blood_pheno','B2toMG_pheno','MGtoSG_pheno','SGtoB2_pheno']
    RGR_cols=['blood_RGR','B2toMG_RGR','MGtoSG_RGR','SGtoB2_RGR']
    SD_cols=['blood_SD','B2toMG_SD','MGtoSG_SD','SGtoB2_SD']
    allcols=[gene_cols,pheno_cols,RGR_cols,SD_cols]
    all_columns = [item for sublist in allcols for item in sublist]
    phenotype_df=pd.DataFrame(columns=all_columns)
    labels = ['Blood','B2 to MG','MG to SG','SG to B2']
    for g in genes:
        gene_anotation=[g.pbankaNewID,g.pbankaOldID,g.description,g.shortName]
        if g.phenodata_id == None:
            colors=['#f0f0f0','#f0f0f0','#f0f0f0','#f0f0f0']
            pheno_calls=['NA','NA','NA','NA']
            RGRs=[np.nan,np.nan,np.nan,np.nan]
            SDs=[np.nan,np.nan,np.nan,np.nan]
        else:

            pheno=Phenodata.query.filter_by(id=g.phenodata_id).first()

            colors=[]
            pheno_calls=[]
            RGRs=[]
            SDs=[]

            for i, col in enumerate(pheno_cols):
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
        tmp=[gene_anotation,pheno_calls,RGRs,SDs]
        tmp_data = [item for sublist in tmp for item in sublist]

        phenotype_df.loc[g.pbankaNewID,:]=tmp_data

    # phenotype_df=pd.DataFrame(columns=['Experiment','RGR','SD','Phenocall'])
    # phenotype_df['Experiment']= labels
    # phenotype_df['RGR']= RGRs
    # phenotype_df['SD']= SDs
    # phenotype_df['Phenocall']= pheno_calls

    # phenotype_df[RGR_cols] = phenotype_df[RGR_cols].map(u"{:,.2f}".format)
    # phenotype_df['SD'] = phenotype_df['SD'].map(u"{:,.2f}".format)
    ## now make table with phenotype dataframe

    data_columns = [item for sublist in [RGR_cols,SD_cols] for item in sublist]
    for col in data_columns:
        phenotype_df[col]=phenotype_df[col].map(u"{:,.2f}".format)
    table_df=phenotype_df.T.copy()
    table_df=table_df.reset_index()
    table=go.Table(
    header=dict(values=list(table_df.columns),
                line_color='darkslategray',
                fill_color='royalblue',
                align=['left','center'],
                font=dict(color='white', size=12),
                height=40
                ),
    cells=dict(values=[table_df[col].values for col in table_df.columns],
            line_color='darkslategray',
            fill=dict(color=['paleturquoise', 'white']),
            align=['left', 'center'],
            font_size=12,
            height=30
            ))
    fig.add_trace(table,row=1,col=1)

    fig.update_layout(title='Phenotype table',width=500,showlegend=True)
    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    # graphJSON = json.dumps(table, cls=plotly.utils.PlotlyJSONEncoder)
    return graphJSON


def plot_x_y_scatter(df,geneList=[]):
    ''' This data frame contains RGR, SD and pheno_call '''

    # fig = px.scatter(df, x='male_fertility_RGR', y='female_fertility_RGR', color="female_fertility_pheno",
    #              error_x='male_fertility_SD', error_y='female_fertility_SD')
    df['error']=0
    df['symbol_male']='circle'
    df['symbol_female']='circle-open'
    # df['size1']=5
    # df['size2']=10

    fig = go.Figure()
    # legend_df=df["female_fertility_pheno"].copy()
    df["female_fertility_pheno_color"]=df["female_fertility_pheno"].replace(change_color_fertility)
    df["male_fertility_pheno_color"]=df["male_fertility_pheno"].replace(change_color_fertility)
    # df['text']=df['name'].map(str) + '- Male(' + df["male_fertility_pheno"].map(str) + ') - Female (' + df["female_fertility_pheno"].map(str) + ')'
    # fig3= px.scatter(df, x='male_fertility_RGR', y='female_fertility_RGR', color="female_fertility_pheno",
    #             labels={
    #                  "male_fertility_RGR": "RGR (male)",
    #                  "female_fertility_RGR": "RGR (female)",
    #                  "female_fertility_pheno": "Fertility phenoype"
    #              },color_discrete_sequence=['#cb181d','#018571','#dfc27d','#80cdc1'],
    #              error_x='error', error_y='error',
    #              size='size1',
    #              hover_name="name")
    #
    # fig2= px.scatter(df, x='male_fertility_RGR', y='female_fertility_RGR', color="male_fertility_pheno",
    #             labels={
    #                  "male_fertility_RGR": "RGR (male)",
    #                  "female_fertility_RGR": "RGR (female)",
    #                  "female_fertility_pheno": "Fertility phenoype"
    #              },color_discrete_sequence=['#cb181d','#018571','#dfc27d','#80cdc1'],
    #              error_x='error', error_y='error',
    #              size='size2',
    #              symbol='symbol_female',
    #              hover_name="name")
    # fig.add_trace(fig3.data[0])
    # fig.add_trace(fig2.data[0])



    # Add traces
    marker_size_female=5
    marker_size_male=10
    marker_size_color=10

    t3=go.Scatter(mode="markers", x=[0], y=[0],marker_symbol='square',marker_size=10,name='Reduced',marker_color='#fc8d59')
    t4=go.Scatter(mode="markers", x=[0], y=[0],marker_symbol='square',marker_size=10,name='Not Reduced',marker_color='#91bfdb')
    t5=go.Scatter(mode="markers", x=[0], y=[0],marker_symbol='square',marker_size=10,name='No Power',marker_color='#ffffbf')
    fig.add_trace(t3)
    fig.add_trace(t4)
    fig.add_trace(t5)
    flag=0
    for g in geneList:
        tmp=df[df['name']==g]
        if not tmp.empty:
            df["female_fertility_pheno_color"]='#f7f7f7'
            df["male_fertility_pheno_color"]='#f7f7f7'
            flag=1
            break
    for g in geneList:
        tmp=df[df['name']==g]
        if not tmp.empty:
            df.loc[tmp.index,"female_fertility_pheno_color"]='#252525' ### green color
            df.loc[tmp.index,"male_fertility_pheno_color"]='#252525'
    if flag==0:
        t1=go.Scatter(mode="markers", x=df['male_fertility_RGR'], y=df['female_fertility_RGR'],
        marker_symbol=df['symbol_male'], marker_color=df["female_fertility_pheno_color"], marker_size=marker_size_female,name='Female',text= df['name'])
        t2=go.Scatter(mode="markers", x=df['male_fertility_RGR'], y=df['female_fertility_RGR'],
        marker_symbol=df['symbol_female'], marker_color=df["male_fertility_pheno_color"], marker_size=marker_size_male,
                           text= df['name'],name='Male',error_y=dict(
                                   type='data', # value of error bar given in data coordinates
                                   array=df['male_fertility_SD'],
                                   color='purple',
                                   visible=False),error_x=dict(
                                           type='data', # value of error bar given in data coordinates
                                           array=df['male_fertility_SD'],
                                           color='purple',
                                           visible=False))
    else:
        ### select white one
        black_df=df[df["male_fertility_pheno_color"]=='#252525'].copy()
        t1=go.Scatter(mode="markers", x=df['male_fertility_RGR'], y=df['female_fertility_RGR'],
        marker_symbol=df['symbol_male'], marker_color=df["female_fertility_pheno_color"], marker_size=5,name='Other',text= df['name'])
        t2=go.Scatter(mode="markers", x=black_df['male_fertility_RGR'], y=black_df['female_fertility_RGR'],
        marker_symbol=black_df['symbol_male'], marker_color=black_df["male_fertility_pheno_color"], marker_size=marker_size_color,
                           text= black_df['name'],name='found',error_y=dict(
                                   type='data', # value of error bar given in data coordinates
                                   array=black_df['male_fertility_SD'],
                                   color='purple',
                                   visible=False),error_x=dict(
                                           type='data', # value of error bar given in data coordinates
                                           array=black_df['male_fertility_SD'],
                                           color='purple',
                                           visible=False))

    fig.add_trace(t1)
    fig.add_trace(t2)




    fig.update_xaxes(title="Male (RGR)")
    fig.update_yaxes(title="Female (RGR)")

    fig.update_layout(title="Fertility phenoype", width=1000, height=1000)

    # error_x=df['error'], error_y=df['error']
    # fig.show()
    return fig




def getGamFigure(geneList=[]):
    ''' scatter plot with two markers '''
    ### step take phenotable
    # all without nan data
    #
    female_idx=phenodata_df.loc[~phenodata_df['female_gam_SD'].isna()].index.values
    male_idx=phenodata_df.loc[~phenodata_df['male_gam_SD'].isna()].index.values

    if (female_idx==male_idx).all():
        # print ('equal')
        # columns=['name','female_gam_SD','female_gam_RGR','female_gam_pheno','male_gam_SD','male_gam_RGR','male_gam_pheno']
        # pheno_gam_df=phenodata_df.loc[female_idx,columns]
        if len(geneList)>0:
            fig=plot_x_y_scatter_gam(pheno_gam_df,geneList)
        else:
            fig=plot_x_y_scatter_gam(pheno_gam_df)


    else:
        print('please check why number of male and female are diffrent')
        fig = go.Figure()
    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    # graphJSON = json.dumps(table, cls=plotly.utils.PlotlyJSONEncoder)
    return graphJSON


### for gametocytes

def plot_x_y_scatter_gam(df,geneList=[]):
    ''' This data frame contains RGR, SD and pheno_call '''


    df['error']=0
    df['symbol_male']='circle'
    df['symbol_female']='circle-open'


    fig = go.Figure()
    # legend_df=df["female_fertility_pheno"].copy()
    df["female_gam_pheno_color"]=df["female_gam_pheno"].replace(change_color_gam)
    df["male_gam_pheno_color"]=df["male_gam_pheno"].replace(change_color_gam)

    flag=0
    for g in geneList:
        tmp=df[df['name']==g]
        if not tmp.empty:
            df["female_gam_pheno_color"]='#f7f7f7'
            df["male_gam_pheno_color"]='#f7f7f7'
            flag=1
            break
    for g in geneList:
        tmp=df[df['name']==g]
        if not tmp.empty:
            df.loc[tmp.index,"female_gam_pheno_color"]='#252525' ### green color
            df.loc[tmp.index,"male_gam_pheno_color"]='#252525'


    # Add traces

    t3=go.Scatter(mode="markers", x=[0], y=[0],marker_symbol='square',marker_size=10,name='Reduced',marker_color='#fc8d59')
    t4=go.Scatter(mode="markers", x=[0], y=[0],marker_symbol='square',marker_size=10,name='Not Reduced',marker_color='#91bfdb')
    t5=go.Scatter(mode="markers", x=[0], y=[0],marker_symbol='square',marker_size=10,name='No Power',marker_color='#ffffbf')
    fig.add_trace(t3)
    fig.add_trace(t4)
    fig.add_trace(t5)
    if flag==0:
        t1=go.Scatter(mode="markers", x=df['male_gam_RGR'], y=df['female_gam_RGR'],
        marker_symbol=df['symbol_male'], marker_color=df["female_gam_pheno_color"], marker_size=5,name='Female',text= df['name'])
        t2=go.Scatter(mode="markers", x=df['male_gam_RGR'], y=df['female_gam_RGR'],
        marker_symbol=df['symbol_female'], marker_color=df["male_gam_pheno_color"], marker_size=10,
                               text= df['name'],name='Male',error_y=dict(
                                       type='data', # value of error bar given in data coordinates
                                       array=df['male_gam_SD'],
                                       color='purple',
                                       visible=False),error_x=dict(
                                               type='data', # value of error bar given in data coordinates
                                               array=df['male_gam_SD'],
                                               color='purple',
                                               visible=False))
    else:
        black_df=df[df["male_gam_pheno_color"]=='#252525'].copy()
        t1=go.Scatter(mode="markers", x=df['male_gam_RGR'], y=df['female_gam_RGR'],
        marker_symbol=df['symbol_male'], marker_color=df["female_gam_pheno_color"], marker_size=10,name='Other',text= df['name'])
        t2=go.Scatter(mode="markers", x=black_df['male_gam_RGR'], y=df['female_gam_RGR'],
        marker_symbol=black_df['symbol_male'], marker_color=black_df["male_gam_pheno_color"], marker_size=10,
                               text= black_df['name'],name='Found',error_y=dict(
                                       type='data', # value of error bar given in data coordinates
                                       array=black_df['male_gam_SD'],
                                       color='purple',
                                       visible=False),error_x=dict(
                                               type='data', # value of error bar given in data coordinates
                                               array=black_df['male_gam_SD'],
                                               color='purple',
                                               visible=False))


    fig.add_trace(t1)
    fig.add_trace(t2)




    fig.update_xaxes(title="Male (RGR)")
    fig.update_yaxes(title="Female (RGR)")

    fig.update_layout(title="Gametocyte phenoype", width=1000, height=1000)

    # error_x=df['error'], error_y=df['error']
    # fig.show()
    return fig


def getFertilityFigure(geneList=[]):
    ''' scatter plot with two markers  '''
    ### step take phenotable
    # all without nan data
    #
    female_idx=phenodata_df.loc[~phenodata_df['female_fertility_SD'].isna()].index.values
    male_idx=phenodata_df.loc[~phenodata_df['male_fertility_SD'].isna()].index.values

    if (female_idx==male_idx).all():
        # print ('equal')
        # columns=['name','female_fertility_SD','female_fertility_RGR','female_fertility_pheno','male_fertility_SD','male_fertility_RGR','male_fertility_pheno']
        # pheno_fertility_df=phenodata_df.loc[female_idx,columns]
        if len(geneList)>0:
            fig=plot_x_y_scatter(pheno_fertility_df,geneList)
        else:
            fig=plot_x_y_scatter(pheno_fertility_df)


    else:
        print('please check why number of male and female are diffrent')
        fig = go.Figure()

    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    # graphJSON = json.dumps(table, cls=plotly.utils.PlotlyJSONEncoder)
    return graphJSON


# def getGamFigure():
#     ''' scatter plot with two markers '''
#     ### step take phenotable
#     # all without nan data
#     #
#     female_idx=phenodata_df.loc[~phenodata_df['female_gam_SD'].isna()].index.values
#     male_idx=phenodata_df.loc[~phenodata_df['male_gam_SD'].isna()].index.values
#
#     if (female_idx==male_idx).all():
#         print ('equal')
#         columns=['name','female_gam_SD','female_gam_RGR','female_gam_pheno','male_gam_SD','male_gam_RGR','male_gam_pheno']
#         pheno_gam_df=phenodata_df.loc[female_idx,columns]
#         fig=plot_x_y_scatter_gam(pheno_gam_df)
#
#
#     else:
#         print('please check why number of male and female are diffrent')
#         fig = go.Figure()
#     graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
#     # graphJSON = json.dumps(table, cls=plotly.utils.PlotlyJSONEncoder)
#     return graphJSON


def getLiverFigure(geneList=[]):
    ''' scatter plot with two markers '''
    ### step take phenotable
    # all without nan data
    #
    # liver_idx=phenodata_df.loc[~phenodata_df['SGtoB2_RGR'].isna()].index.values
    #
    # columns=['name','SGtoB2_SD','SGtoB2_RGR','SGtoB2_pheno']
    # pheno_liver_df=phenodata_df.loc[liver_idx,columns]
    # pheno_liver_df["SGtoB2_pheno"]=pheno_liver_df["SGtoB2_pheno"].replace(change_label_liver)
    # pheno_liver_df['confidence']=-np.log2(pheno_liver_df['SGtoB2_SD'])

    # fig= px.scatter(pheno_liver_df, x='SGtoB2_RGR', y='confidence', color="SGtoB2_pheno",
    #             labels={
    #                  'SGtoB2_RGR': 'RGR',
    #                  'confidence': 'Confidence',
    #                  "SGtoB2_pheno": "Liver phenoype",
    #              },color_discrete_map=change_color_liver,
    #              hover_name="name")
    # fig.update_traces(marker=dict(size=5),selector=dict(mode='markers'))
    fig = go.Figure()
    t3=go.Scatter(mode="markers", x=[0], y=[0],marker_symbol='circle',marker_size=10,name='Reduced',marker_color='#fc8d59')
    t4=go.Scatter(mode="markers", x=[0], y=[0],marker_symbol='circle',marker_size=10,name='Not Reduced',marker_color='#91bfdb')
    t5=go.Scatter(mode="markers", x=[0], y=[0],marker_symbol='circle',marker_size=10,name='No Power',marker_color='#ffffbf')
    fig.add_trace(t3)
    fig.add_trace(t4)
    fig.add_trace(t5)



    pheno_liver_df["SGtoB2_pheno_color"]=pheno_liver_df["SGtoB2_pheno"].replace(change_label_liver)
    pheno_liver_df["SGtoB2_pheno_color"]=pheno_liver_df["SGtoB2_pheno_color"].replace(change_color_liver)

    flag=0
    for g in geneList:
        tmp=pheno_liver_df[pheno_liver_df['name']==g]
        if not tmp.empty:
            pheno_liver_df["SGtoB2_pheno_color"]='#f7f7f7'

            flag=1
            break
    for g in geneList:
        tmp=pheno_liver_df[pheno_liver_df['name']==g]
        if not tmp.empty:
            pheno_liver_df.loc[tmp.index,"SGtoB2_pheno_color"]='#252525' ### green color


    if flag==0:
        t1=go.Scatter(mode="markers", x=pheno_liver_df['SGtoB2_RGR'], y=pheno_liver_df['confidence'],
        marker_color=pheno_liver_df["SGtoB2_pheno_color"], marker_size=5,text= pheno_liver_df['name'])
        fig.add_trace(t1)
        fig['data'][3]['showlegend']=False
    else:
        black_df=pheno_liver_df[pheno_liver_df["SGtoB2_pheno_color"]=='#252525'].copy()
        t1=go.Scatter(mode="markers", x=pheno_liver_df['SGtoB2_RGR'], y=pheno_liver_df['confidence'],
        marker_color=pheno_liver_df["SGtoB2_pheno_color"], marker_size=5,text= pheno_liver_df['name'])
        t2=go.Scatter(mode="markers", x=black_df['SGtoB2_RGR'], y=black_df['confidence'],
        marker_color=black_df["SGtoB2_pheno_color"], marker_size=5,text= black_df['name'])
        fig.add_trace(t1)
        fig.add_trace(t2)
        fig['data'][3]['showlegend']=False
        fig['data'][4]['showlegend']=False

    # pheno_liver_df["SGtoB2_pheno"]=pheno_liver_df["SGtoB2_pheno"].replace(change_label_liver)

    fig['data'][3]['showlegend']=False
    fig.update_layout(title="Liver phenoype", width=1000, height=500)
    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    # graphJSON = json.dumps(table, cls=plotly.utils.PlotlyJSONEncoder)
    return graphJSON


def getBloodFigure(geneList=[]):
    ''' scatter plot with two markers '''
    ### step take phenotable
    # all without nan data
    #
    # blood_idx=phenodata_df.loc[~phenodata_df['blood_RGR'].isna()].index
    # blood_idx_sd=phenodata_df.loc[~phenodata_df['blood_SD'].isna()].index
    # no_sd_idx=set(blood_idx)-set(blood_idx_sd)
    # print(len(no_sd_idx))
    #
    # columns=['name','blood_SD','blood_RGR','blood_pheno']
    # pheno_blood_df=phenodata_df.loc[blood_idx,columns]
    #
    # ### change on log 2 scale
    # pheno_blood_df['blood_SD']=pheno_blood_df['blood_SD'].fillna(pheno_blood_df['blood_SD'].max())
    # pheno_blood_df['blood_SD_log2']=(1/np.log(2))*pheno_blood_df['blood_SD']/pheno_blood_df['blood_RGR']
    # pheno_blood_df['blood_RGR_log']=np.log2(pheno_blood_df['blood_RGR'])
    # pheno_blood_df['confidence']=-np.log2(pheno_blood_df['blood_SD'])
    # pheno_blood_df['size']=1.0
    ###


    # pheno_liver_df["blood_pheno"]=pheno_liver_df["blood_pheno"].replace(change_label_liver)
    # fig= px.scatter(pheno_blood_df, x='blood_RGR_log', y='confidence', color="blood_pheno",
    #             labels={
    #                  'blood_RGR_log': 'RGR',
    #                  'confidence': 'Confidence',
    #                  "blood_pheno": "Blood phenoype",
    #              },color_discrete_map=change_color_blood,
    #              hover_name="name")
    # fig.update_traces(marker=dict(size=5),selector=dict(mode='markers'))

    fig = go.Figure()
    t3=go.Scatter(mode="markers", x=[0], y=[0],marker_symbol='circle',marker_size=10,name='Reduced',marker_color='#fc8d59')
    t4=go.Scatter(mode="markers", x=[0], y=[0],marker_symbol='circle',marker_size=10,name='Not Reduced',marker_color='#91bfdb')
    t5=go.Scatter(mode="markers", x=[0], y=[0],marker_symbol='circle',marker_size=10,name='No Power',marker_color='#ffffbf')
    fig.add_trace(t3)
    fig.add_trace(t4)
    fig.add_trace(t5)

    pheno_blood_df["blood_pheno_color"]=pheno_blood_df["blood_pheno"].replace(change_color_blood)

    flag=0
    for g in geneList:
        tmp=pheno_blood_df[pheno_blood_df['name']==g]
        if not tmp.empty:
            pheno_blood_df["blood_pheno_color"]='#f7f7f7'

            flag=1
            break
    for g in geneList:
        tmp=pheno_blood_df[pheno_blood_df['name']==g]
        if not tmp.empty:
            pheno_blood_df.loc[tmp.index,"blood_pheno_color"]='#252525' ### green color

    if flag==0:
        t1=go.Scatter(mode="markers", x=pheno_blood_df['blood_RGR_log'], y=pheno_blood_df['confidence'],
        marker_color=pheno_blood_df["blood_pheno_color"], marker_size=5,text= pheno_blood_df['name'])
        fig.add_trace(t1)
        fig['data'][3]['showlegend']=False
    else:
        black_df=pheno_blood_df[pheno_blood_df["blood_pheno_color"]=='#252525'].copy()
        t1=go.Scatter(mode="markers", x=pheno_blood_df['blood_RGR_log'], y=pheno_blood_df['confidence'],
        marker_color=pheno_blood_df["blood_pheno_color"], marker_size=5,text= pheno_blood_df['name'])

        t2=go.Scatter(mode="markers", x=black_df['blood_RGR_log'], y=black_df['confidence'],
        marker_color=black_df["blood_pheno_color"], marker_size=5,text= black_df['name'])
        fig.add_trace(t1)
        fig.add_trace(t2)
        fig['data'][3]['showlegend']=False
        fig['data'][4]['showlegend']=False


    fig.update_layout(title="Blood phenoype", width=1000, height=500)
    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    # graphJSON = json.dumps(table, cls=plotly.utils.PlotlyJSONEncoder)

    return graphJSON



def getPhenodf(geneList):
    ''' get phenotype pie chart and table'''
    # get common genes
    comm_genes=list(set(geneList) & set(pheno_tmp.index.to_list()))
    phenotype_df=pd.DataFrame(index=comm_genes,columns=pheno_tmp.columns)
    if len(comm_genes)>0:
        phenotype_df.loc[comm_genes,:]=pheno_tmp.loc[comm_genes,:].copy()
    phenotype_df=phenotype_df.reset_index()
    phenotype_df=phenotype_df.rename(columns={"index": "Gene"})
    phenotype_df['Gene']='<a href='+'https://plasmodb.org/plasmo/app/record/gene/'+phenotype_df['Gene'] +'>' + phenotype_df['Gene']+ '</a>'
    my_table=json.loads(phenotype_df.to_json(orient="split"))["data"]
    columns=[{"title": str(col),"sortable": True} for col in json.loads(phenotype_df.to_json(orient="split"))["columns"]]

    # graphJSON = json.dumps(table, cls=plotly.utils.PlotlyJSONEncoder)
    return my_table,columns


def filter_df_rgr(df,colname,value,sym='>'):
    ''' filter by relative growth rate '''
    if sym=='>':
        new_df=df[df[colname]>value].copy()
    elif sym=='<':
        new_df=df[df[colname]<value].copy()

    return new_df



def filterTablebyRGR(values):
    ''' values are the list of string '''
    list_of_floats_or_none = []

    for item in values:
        if item:
            try:
                list_of_floats_or_none.append(np.log2(float(item)))
            except:
                list_of_floats_or_none.append(None)

        else:
            list_of_floats_or_none.append(None)

    # [male_ferti_gr,male_ferti_le,female_ferti_gr,
    # female_ferti_le,male_gam_gr,male_gam_le,female_gam_gr,
    # female_gam_le,blood_gr,blood_le,liver_gr,liver_le]=list_of_floats_or_none
    ## slect RGR
    RGR_cols=['male_fertility_RGR','male_fertility_RGR','female_fertility_RGR',
    'female_fertility_RGR','male_gam_RGR','male_gam_RGR','female_gam_RGR',
    'female_gam_RGR','blood_RGR','blood_RGR','SGtoB2_RGR','SGtoB2_RGR']

    symbols=['>','<','>','<','>','<','>','<','>','<','>','<']
    tmp=phenodata_df.copy()
    tmp=tmp.drop(['id'],axis=1)
    tmp=tmp.rename(columns={"name": "Gene"})
    for i,col in enumerate(RGR_cols):
        if (not (list_of_floats_or_none[i] ==None)) and not(tmp.empty):
            tmp=filter_df_rgr(tmp,col,list_of_floats_or_none[i],symbols[i])
    #### get data colum and genes
    ## get columns for the data
    ### we can polish columns
    genes=tmp['Gene'].to_list()
    if not tmp.empty:
        tmp['Gene']='<a href='+'https://plasmodb.org/plasmo/app/record/gene/'+tmp['Gene'] +'>' + tmp['Gene']+ '</a>'

    for col in tmp.columns:
        try:
            tmp[col]=tmp[col].map(u"{:,.3f}".format)
        except:
            pass

    my_table=json.loads(tmp.to_json(orient="split"))["data"]
    columns=[{"title": str(col),"sortable": True} for col in json.loads(tmp.to_json(orient="split"))["columns"]]


    return genes,my_table,columns

    ####
