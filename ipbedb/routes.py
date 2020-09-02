from flask import render_template,url_for,flash,redirect,request,jsonify, make_response
from ipbedb.forms import RegistrationForm,LoginForm,PhenotypeForm,PhenotypeFilterForm
from ipbedb import app,db,bcrypt
from ipbedb.db_model import User,Geneanot
from flask_login import login_user,current_user,logout_user,login_required
# from db_model import User
from ipbedb.specialFunc import create_plot,create_dendrogram_for_cluster,create_plots_for_gene
from ipbedb.specialFunPheno import (getPhenoTable,getFertilityFigure,getGamFigure,
    getLiverFigure,getBloodFigure,getCombinedPhenoFig,getPhenodf,filterTablebyRGR,phenodf_all)
import json
import pandas as pd
from flask import Response
from io import StringIO


PREFIX='/pbedb'
@app.route(PREFIX+"/")
@app.route(PREFIX+"/home")
def home():
    return render_template('home.html')


# @app.route("/about")
# def about():
#     return "<h1>About Page</h1>"


@app.route(PREFIX+"/register",methods=['GET','POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form=RegistrationForm()

    if form.validate_on_submit():
        hashed_password=bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user=User(username=form.username.data,email=form.email.data,password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash(f'Your account has been created ! Now you can log in!', 'success')
        return redirect(url_for('login'))

    return render_template('register.html',title='Register',form=form)


@app.route(PREFIX+"/login",methods=['GET','POST'])
def login():

    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form=LoginForm()
    if form.validate_on_submit():
        user=User.query.filter_by(email=form.email.data).first()

        if user and bcrypt.check_password_hash(user.password,form.password.data):
            login_user(user,remember=form.remember.data)
            next_page=request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('home'))
        else:
            flash('Login unsuccessful and please check email and password','danger')

    return render_template('login.html',title='Login',form=form)

@app.route(PREFIX+"/logout")
def logout():
    logout_user()
    return redirect(url_for('home'))


@app.route(PREFIX+"/modeling")
@login_required
def modeling():
    return render_template('modeling.html',title='Modeling')


@app.route(PREFIX+"/cluster",methods=['GET', 'POST'])
def cluster():
    graphJSON= create_plot()
    return render_template('cluster.html',plot=graphJSON,title='Cluster')

@app.route(PREFIX+"/dendogram",methods=['POST'])
def dendogram():
    req= request.get_json()
    if 'name' in req:
        clust_name=req['name']
        print(req)
        graphJSON=create_dendrogram_for_cluster(clust_name)
    else:
        graphJSON='{}'

    return graphJSON


@app.route(PREFIX+"/clustergeneClick",methods=['POST'])
def clustergeneClick():
    req= request.get_json()
    if 'name' in req:
        gene=req['name'].split('|')[0]
        print(req)
        # res = make_response(jsonify({"message": "OK"}), 200)
        # return res
        fig_ap2time,fig_ap2KO,fig_pheno,fig_atlas_stage,fig_atlas_gene=create_plots_for_gene(gene)
    else:
        fig_ap2time,fig_ap2KO,fig_pheno,fig_atlas_stage,fig_atlas_gene='{}'
    result={'data1':fig_ap2time,'data2':fig_ap2KO,'data3':fig_pheno,'data4':fig_atlas_stage,'data5':fig_atlas_gene}
    # return fig_ap2time,fig_ap2KO,fig_pheno,fig_atlas_stage
    return jsonify(result)



@app.route(PREFIX+"/phenotype",methods=['GET', 'POST'])
def phenotype():
    form=PhenotypeForm()
    filter_form=PhenotypeFilterForm()
    fertility_fig=getFertilityFigure()
    gam_fig=getGamFigure()
    liver_fig=getLiverFigure()
    blood_fig=getBloodFigure()
    all_pheno_fig=getCombinedPhenoFig()
    # if request.method == "POST":
    #     print('we will do something')
    return render_template('phenotype.html',form=form,form2=filter_form,all_pheno_fig=all_pheno_fig,
    fertility_fig=fertility_fig,gam_fig=gam_fig,liver_fig=liver_fig,blood_fig=blood_fig,title='Phenotype')


## load pbanka_ids
@app.route(PREFIX+'/get_pbanka_ids')
def get_pbanka_ids():
    gene_names=[item.pbankaNewID for item in Geneanot.query.all()]
    # suggestions=[{'value':item,'data':item} for item in gene_names]
    # return jsonify({'"suggestions"':suggestions})
    return jsonify(gene_names)

# # to process genelist
# @app.route(PREFIX+'/process_genelist', methods=['POST'])
# def process_genelist():
#     data= request.get_json()
#     data= json.dumps(data, indent = 4)
#
#     if (not bool(data)):
#         data='{}'
#     result={'gene':data}
#     print(result)
#     return jsonify(result)

### to process single gene search
@app.route(PREFIX+'/process', methods=['GET','POST'])
def process():
    data= request.get_json()
    # import pdb; pdb.set_trace()
    # identify gene of gene list
    ## priroity gene
    print(data[3]['choices'])

    final_gene=[]
    if ('gene' in data[0].keys()) and data[0]['gene']:
        geneid=data[0]['gene']
        final_gene=[geneid]
    elif ('genelist' in data[1].keys()) and data[1]['genelist']:
        all_gene=data[1]['genelist']
        final_gene=list(set([item.strip() for item in all_gene.split('\n')]))
    else:
        print('Need gene as input')

    if len(final_gene)>0:
        table_pheno=getPhenoTable(final_gene)
        table,columns=getPhenodf(final_gene)
    else:
        table_pheno='{}'
        table,columns='{}'

    print(final_gene)


    ## get the file
    # print(result)
    ### get all graphs


    if len(final_gene)>0:
        all_pheno_fig=getCombinedPhenoFig(final_gene[0])
        fertility_fig=getFertilityFigure(final_gene)
        gam_fig=getGamFigure(final_gene)
        liver_fig=getLiverFigure(final_gene)
        blood_fig=getBloodFigure(final_gene)
    else:
        all_pheno_fig=getCombinedPhenoFig()
        fertility_fig=getFertilityFigure()
        gam_fig=getGamFigure()
        liver_fig=getLiverFigure()
        blood_fig=getBloodFigure()

    result={'data':table_pheno,'all_pheno_fig':all_pheno_fig,'fertility_fig':fertility_fig,
     'gam_fig':gam_fig,'blood_fig':blood_fig,'liver_fig':liver_fig,'table':table,'columns':columns}

    return jsonify(result)

### to process single gene search
@app.route(PREFIX+'/getfiles', methods=['GET','POST'])
def getfiles():
    data= request.get_json()
    data= json.dumps(data, indent = 4)
    if (not bool(data)):
        data='{}'
    result={'gene':data}
    ## get the file
    print(result)

    return jsonify(result)

## dash app


## load pbanka_ids
@app.route(PREFIX+'/get_clicked_gene',methods=['GET','POST'])
def get_clicked_gene():
    data= request.get_json()
    ### get plot for that gene
    if 'name' in data.keys():
        gene=data['name'].strip()
        all_pheno_fig=getCombinedPhenoFig(gene)
    else:
        all_pheno_fig='{}'


    result={'data':all_pheno_fig}
    ## get the file

    return jsonify(result)

## load data from filter form
@app.route(PREFIX+'/get_filter_form_values',methods=['GET','POST'])
def get_filter_form_values():
    data=request.get_json()

    values=[item['val'] for item in data ]

    final_gene,filter_table,filter_columns=filterTablebyRGR(values)
    # import pdb; pdb.set_trace()

    if len(final_gene)>0:
        all_pheno_fig=getCombinedPhenoFig(final_gene[0])
        fertility_fig=getFertilityFigure(final_gene)
        gam_fig=getGamFigure(final_gene)
        liver_fig=getLiverFigure(final_gene)
        blood_fig=getBloodFigure(final_gene)
    else:
        all_pheno_fig=getCombinedPhenoFig()
        fertility_fig=getFertilityFigure()
        gam_fig=getGamFigure()
        liver_fig=getLiverFigure()
        blood_fig=getBloodFigure()

    result={'all_pheno_fig':all_pheno_fig,'fertility_fig':fertility_fig,
     'gam_fig':gam_fig,'blood_fig':blood_fig,'liver_fig':liver_fig,'table':filter_table,'columns':filter_columns}
    return jsonify(result)



@app.route(PREFIX+'/dash')
def render_dashboard():
    return redirect('/pheno')



@app.route(PREFIX+'/download_data',methods=['GET','POST'])
def download_data():
    result={'page': PREFIX+"/file/table"}
    return jsonify(result)

@app.route(PREFIX+"/file/<file_name>",methods=['GET','POST'])
def get_table_file(file_name):
    ## get table data
    generated_file = generate_csv_file(phenodf_all)
    response = Response(generated_file, mimetype="text/csv")
    # add a filename
    response.headers.set(
        "Content-Disposition", "attachment", filename="{0}.csv".format(file_name)
    )
    return response

def generate_csv_file(file_df):
    # Create an o/p buffer
    file_buffer = StringIO()

    # Write the dataframe to the buffer
    file_df.to_csv(file_buffer, encoding="utf-8", index=False, sep=",")

    # Seek to the beginning of the stream
    file_buffer.seek(0)
    return file_buffer
