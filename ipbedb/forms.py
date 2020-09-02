from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField,TextAreaField,SelectMultipleField,widgets
from wtforms.validators import DataRequired, Length, Email, EqualTo,ValidationError
from ipbedb.db_model import User
from flask_wtf.file import FileField,FileRequired


class RegistrationForm(FlaskForm):
    username = StringField('Username',
                           validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password',
                                     validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')

    ### check custom validate
    def validate_username(self,username):
        user=User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('That username is taken. Please choose a new one')

            ### check custom validate

    def validate_email(self, email):
        email = User.query.filter_by(email=email.data).first()
        if email:
            raise ValidationError('That email is taken. Please choose a new one')


class LoginForm(FlaskForm):
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')

class MultiCheckboxField(SelectMultipleField):
    """
    A multiple-select, except displays a list of checkboxes.

    Iterating the field will produce subfields, allowing custom rendering of
    the enclosed checkbox fields.
    """
    widget = widgets.ListWidget(prefix_label=False)
    option_widget = widgets.CheckboxInput()



class PhenotypeForm(FlaskForm):
    geneid = StringField('geneid',render_kw={"placeholder": "geneid"})
    genelist = TextAreaField('genelist')
    submit = SubmitField('Search')
    genefile = FileField('upload genelist')
    pheno_choice=[('1','Blood'),('2','Liver'),('3','Gametocyte'),('4','Fertility')]
    choices = MultiCheckboxField('Routes', choices = pheno_choice,coerce=int,default = ['1', '2','3','4'])

class PhenotypeFilterForm(FlaskForm):
    male_ferti_gr= StringField('Male Fertility',render_kw={"placeholder": ">"})
    female_ferti_gr= StringField('Female Fertility',render_kw={"placeholder": ">"})
    male_gam_gr= StringField('Male Gametocyte',render_kw={"placeholder": ">"})
    female_gam_gr= StringField('Female Gametocyte',render_kw={"placeholder": ">"})
    blood_gr= StringField('Blood Phenotype',render_kw={"placeholder": ">"})
    liver_gr= StringField('Liver Phenotype',render_kw={"placeholder": ">"})
    male_ferti_le= StringField('Male Fertility',render_kw={"placeholder": "<"})
    female_ferti_le= StringField('Female Fertility',render_kw={"placeholder": "<"})
    male_gam_le= StringField('Male Fertility',render_kw={"placeholder": "<"})
    female_gam_le= StringField('Female Fertility',render_kw={"placeholder": "<"})
    blood_le= StringField('Blood Phenotype',render_kw={"placeholder": "<"})
    liver_le= StringField('Liver Phenotype',render_kw={"placeholder": "<"})
    filter = SubmitField('Execute')
