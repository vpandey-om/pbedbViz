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