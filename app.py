from flask import Flask, render_template, url_for, request, redirect, flash, session
import mysql.connector
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import yaml
import os
from flask_recaptcha import ReCaptcha
from functools import wraps
import uuid
from flask_mail import Message, Mail

con = mysql.connector.MySQLConnection(
		host='localhost',
		port='3306',
		user='root',
		passwd='',
		database='ticketing_system'
	)

mycursor = con.cursor(dictionary=True, buffered=True)

app = Flask(__name__)

app.secret_key='tajni_kljuc'

recaptcha = ReCaptcha(app=app)

app.config.update(dict(
    RECAPTCHA_ENABLED = True,
    RECAPTCHA_SITE_KEY = "6LdSR74ZAAAAAIuV9J4LrlJ3N6U-h0Gug0v9e8AV",
    RECAPTCHA_SECRET_KEY = "6LdSR74ZAAAAAPu0JW-UFvFKFezK3GGJz82C4lUr",
))
 
recaptcha = ReCaptcha()
recaptcha.init_app(app)

UPLOAD_FOLDER = 'static/img/zahtevi'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

app.config['MAIL_SERVER'] = 'smtp.googlemail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = 'ticketing.sistem@gmail.com'
app.config['MAIL_PASSWORD'] = '@Ticketing_1'
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True

mail = Mail(app)

#-----------------------------------------------> Funkcije <------------------------------------------------------------------------

def allowed_file(filename):
	return '.' in filename and \
			filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def is_not_blank(s):
    return bool(s and s.strip())

#-----------------------------------------------> POČETNA STRANA http://localhost:5000/ <------------------------------------------------------------------------

@app.route('/', methods=['GET', 'POST'])
def Home():
	return render_template('login.html')

#-----------------------------------------------> LOGIN <------------------------------------------------------------------------

@app.route('/login', methods=['GET', 'POST'])
def Login():
	if request.method=='GET':
		return render_template('login.html')
	elif request.method=='POST':
		forma=request.form
		upit="SELECT korisnici.*, role.naziv_role as rola FROM korisnici INNER JOIN role ON korisnici.rola = role.id_role WHERE korisnicko_ime=%s"
		vrednost=(forma['korisnicko_ime'],)
		mycursor.execute(upit, vrednost)
		korisnik=mycursor.fetchone()
		if recaptcha.verify():
			if (korisnik is not None):
				if check_password_hash(korisnik['lozinka'], forma['lozinka']):
					if korisnik['rola'] == 'Administrator kompanije':
						session['logged_ak']=str(korisnik)
						return redirect(url_for('Ak_Zahtevi'))
					elif korisnik['rola'] == 'Zaposleni kompanije':
						session['logged_zk']=str(korisnik)
						return redirect(url_for('Zk_Zahtevi'))
					elif korisnik['rola'] == 'Administrator klijentske kompanije':
						session['logged_akk']=str(korisnik)
						return redirect(url_for('Akk_Zahtevi'))
					elif korisnik['rola'] == 'Zaposleni klijentske kompanije':
						session['logged_zkk']=str(korisnik)
						return redirect(url_for('Zkk_Zahtevi'))
				else:
					flash("Pogrešna lozinka!", 'danger')
					return redirect(request.referrer)
			else:
				flash("Korisnik sa navedenim korisičkim imenom ne postoji.", 'danger')
				return redirect(request.referrer)
		else:
			flash('Sigurnosno polje nije popunjeno!', 'danger')
			return redirect(request.referrer)

def isLogged_Ak():
	if 'logged_ak' in session:
		return True
	else:
		return False

def isLogged_Zk():
	if 'logged_zk' in session:
		return True
	else:
		return False

def isLogged_Akk():
	if 'logged_akk' in session:
		return True
	else:
		return False

def isLogged_Zkk():
	if 'logged_zkk' in session:
		return True
	else:
		return False

@app.route('/logout_ak')
def Logout_Ak():
	session.pop('logged_ak', None)
	session.clear()
	return redirect(url_for('Login'))

@app.route('/logout_zk')
def Logout_Zk():
	session.pop('logged_zk', None)
	session.clear()
	return redirect(url_for('Login'))

@app.route('/logout_akk')
def Logout_Akk():
	session.pop('logged_akk', None)
	session.clear()
	return redirect(url_for('Login'))

@app.route('/logout_zkk')
def Logout_Zkk():
	session.pop('logged_zkk', None)
	session.clear()
	return redirect(url_for('Login'))

def login_required_ak(f):
	@wraps(f)
	def decorated_function(*args, **kwargs):
		user = isLogged_Ak()
		if user == False:
			return redirect(url_for('Login'))
		return f(*args, **kwargs)
	return decorated_function

def login_required_zk(f):
	@wraps(f)
	def decorated_function(*args, **kwargs):
		user = isLogged_Zk()
		if user == False:
			return redirect(url_for('Login'))
		return f(*args, **kwargs)
	return decorated_function

def login_required_akk(f):
	@wraps(f)
	def decorated_function(*args, **kwargs):
		user = isLogged_Akk()
		if user == False:
			return redirect(url_for('Login'))
		return f(*args, **kwargs)
	return decorated_function

def login_required_zkk(f):
	@wraps(f)
	def decorated_function(*args, **kwargs):
		user = isLogged_Zkk()
		if user == False:
			return redirect(url_for('Login'))
		return f(*args, **kwargs)
	return decorated_function
#-----------------------------------------------> ADMINISTRATOR KOMPANIJE <-------------------------------------------------------

#-----> ZAHTEVI <-----

@app.route('/ak_zahtev/<string:id_data>', methods=['GET', 'POST'])
@login_required_ak
def Ak_Zahtev(id_data):


	upit= "SELECT *,  nazivStatusa(status) AS naziv_statusa, nazivKompanije(kompanija) AS kompanija_naziv, nazivKompanije(za_kompaniju) AS za_kompaniju_naziv, imePodnosioca(ime_prezime_podnosioca) AS ime, prezimePodnosioca(ime_prezime_podnosioca) AS prezime, nazivTipa(tip_zahteva) AS naziv_tipa FROM zahtevi WHERE id_zahteva = %s"
	vrednost = (id_data,)
	mycursor.execute(upit, vrednost)
	zahtevi = mycursor.fetchone()

	mycursor.execute("SELECT * FROM status")
	status = mycursor.fetchone()

	mycursor.execute("SELECT * FROM tip_zahteva")
	tip_zahteva = mycursor.fetchone()

	return render_template('ak_zahtev.html', zahtevi = zahtevi, status = status, tip_zahteva = tip_zahteva)



@app.route('/ak_zahtevi', methods=['GET', 'POST'])
@login_required_ak
def Ak_Zahtevi():


	if request.method == 'GET':

		upit = "SELECT *, nazivKompanije(kompanija) AS naziv_kompanije, nazivKompanije(za_kompaniju) AS za_kompaniju, nazivStatusa(status) AS naziv_statusa, nazivTipa(tip_zahteva) AS naziv_tipa, imePodnosioca(ime_prezime_podnosioca) AS ime, prezimePodnosioca(ime_prezime_podnosioca) AS prezime FROM zahtevi"
		mycursor.execute(upit)
		zahtevi = mycursor.fetchall()

		mycursor.execute("SELECT * FROM status")
		status = mycursor.fetchall()

		mycursor.execute("SELECT *, nazivKompanije(kompanija) AS kompanija_naziv FROM korisnici")
		podnosilac = mycursor.fetchall()

		mycursor.execute("SELECT * FROM tip_zahteva")
		tip_zahteva = mycursor.fetchall()
		
		return render_template('ak_zahtevi.html', zahtevi = zahtevi, status = status, podnosilac = podnosilac, tip_zahteva = tip_zahteva)


@app.route('/ak_zahtev_izmena/<string:id_data>', methods=['GET', 'POST'])
@login_required_ak
def Ak_Zahtev_Izmena(id_data):


	if request.method == "GET":

		upit= "SELECT *,  nazivStatusa(status) AS naziv_statusa, nazivKompanije(kompanija) AS kompanija_naziv, nazivKompanije(za_kompaniju) AS za_kompaniju_naziv, imePodnosioca(ime_prezime_podnosioca) AS ime, prezimePodnosioca(ime_prezime_podnosioca) AS prezime, nazivTipa(tip_zahteva) AS naziv_tipa FROM zahtevi WHERE id_zahteva = %s"
		vrednost = (id_data,)
		mycursor.execute(upit, vrednost)
		zahtevi = mycursor.fetchone()

		upit2="SELECT * FROM status WHERE tip_statusa NOT IN (SELECT nazivStatusa(status) as naziv_statusa FROM zahtevi WHERE id_zahteva = %s)"
		mycursor.execute(upit2, vrednost)
		status = mycursor.fetchall()

		mycursor.execute("SELECT * FROM tip_zahteva")
		tip_zahteva = mycursor.fetchall()

		a = session['logged_ak']
		res=yaml.full_load(a)
		korisnik_id=res['id_korisnika']

		upit = "SELECT *, nazivKompanije(kompanija) AS kompanija_naziv, nazivRole(rola) AS naziv_role FROM korisnici WHERE id_korisnika=%s"
		vrednosti=(korisnik_id, )
		mycursor.execute(upit, vrednosti)
		korisnik = mycursor.fetchone()

		return render_template("ak_zahtev_izmena.html", zahtevi = zahtevi, status = status, tip_zahteva=tip_zahteva, korisnik = korisnik)

	elif request.method == "POST":

		a = session['logged_ak']
		res=yaml.full_load(a)
		korisnik_id=res['id_korisnika']
		ime=res['ime']
		prezime=res['prezime']
		email = res['email']
		rola = res['rola']
			
		upit = "SELECT *, nazivKompanije(kompanija) AS kompanija_naziv, nazivRole(rola) AS naziv_role FROM korisnici WHERE id_korisnika=%s"
		vrednosti=(korisnik_id, )
		mycursor.execute(upit, vrednosti)
		korisnik = mycursor.fetchone()

		kompanija = korisnik['kompanija_naziv']

		ime_prezime_kompanija = ime + " " + prezime + " - " + kompanija

		poruka = Message(subject='Promena statusa zahteva', sender=(ime_prezime_kompanija, email), recipients=['ticketing.sistem@gmail.com'])
		poruka.body = render_template('mejl_za_slanje_4.html')
		mail.send(poruka)


		upit = """UPDATE zahtevi SET 
			    zahtev = %s,
			    napomena = %s,
			    tip_zahteva = %s,
			    ocekivani_datum = %s,
			    status = %s,
			    komentar = %s,
			    broj_utrosenih_sati = %s
			    WHERE id_zahteva = %s"""
		forma = request.form
		vrednosti = (
			forma['zahtev'],
			forma['napomena'],
			forma['tip_zahteva'],
			forma['ocekivani_datum'],
			forma['status'],
			forma['komentar'],
			forma['broj_utrosenih_sati'],
			id_data
		)
		mycursor.execute(upit, vrednosti)
		con.commit()
		flash("Izmena je uspešno izvršena.")

		return redirect(url_for('Ak_Zahtevi'))


@app.route('/ak_promena_slike/<string:id_data>', methods=['GET', 'POST'])
@login_required_ak
def Ak_Promena_Slike(id_data):

	if request.method == 'GET':

		upit = "SELECT * FROM zahtevi WHERE id_zahteva = %s"
		vrednost = (id_data,)
		mycursor.execute(upit, vrednost)
		zahtevi = mycursor.fetchone()

		return render_template('ak_promena_slike.html', zahtevi = zahtevi)

	elif request.method == 'POST':

		file = request.files['file']

		if file.filename == '':
			flash('Slika nije dodata.')
			return redirect(request.url)

		elif allowed_file(file.filename) is False:
			flash('Izabrani tip fajla nije podržan.')
			return redirect(request.url)

		else:
			filename = secure_filename(file.filename)
			file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

			putanja = (os.path.join(app.config['UPLOAD_FOLDER'], filename))

			upit = """UPDATE zahtevi SET 
			    	slika_kao_opis_zahteva = %s
			    	WHERE id_zahteva = %s"""
			vrednosti = (
				putanja,
				id_data
			)
			mycursor.execute(upit, vrednosti)
			con.commit()
			flash("Slika je uspešno izmenjena.")

			return redirect(url_for('Ak_Zahtevi'))

@app.route('/ak_zahtev_brisanje/<string:id_data>', methods=['GET', 'POST'])
@login_required_ak 
def Ak_Zahtev_Brisanje(id_data):


	mycursor = con.cursor()
	upit = "DELETE FROM zahtevi WHERE id_zahteva = %s"
	vrednost = (id_data,)
	mycursor.execute(upit, vrednost)
	flash("Zahtev je obrisan.")
	con.commit()

	return redirect(url_for('Ak_Zahtevi'))

	
#-----> KORISNICI <-----

@app.route('/ak_korisnici', methods=['GET', 'POST'])
@login_required_ak
def Ak_Korisnici():


	upit = "SELECT *, nazivKompanije(kompanija) AS naziv_kompanije, nazivRole(rola) AS naziv_role FROM korisnici"
	mycursor.execute(upit)
	korisnici = mycursor.fetchall()
	mycursor.execute("SELECT * FROM kompanije")
	kompanije = mycursor.fetchall()
	return render_template('ak_korisnici.html', korisnici = korisnici, kompanije = kompanije)


@app.route('/ak_novi_korisnik', methods=['GET', 'POST'])
@login_required_ak
def Ak_Novi_Korisnik():

	if request.method == "GET":

		mycursor.execute("SELECT * FROM kompanije")
		kompanije = mycursor.fetchall()
		mycursor.execute("SELECT * FROM role")
		rola = mycursor.fetchall()	
		return render_template('ak_novi_korisnik.html', kompanije=kompanije, rola=rola)
		
	elif request.method == 'POST':

		forma = request.form

		poruka = Message(subject='Korisnički nalog', sender=('Ticketing Sistem', 'ticketing.sistem@gmail.com'), recipients=[request.form['email']])
		poruka.body = render_template('mejl_za_slanje_2.html')
		mail.send(poruka)

		upit = "INSERT INTO korisnici (ime,	prezime, kompanija, rola, email, korisnicko_ime, lozinka) VALUES (%s, %s, %s, %s, %s, %s, %s)"
		hash_lozinka = generate_password_hash(forma['lozinka'])
		vrednosti = (forma['ime'], forma['prezime'], forma['kompanija'], forma['rola'], forma['email'], forma['korisnicko_ime'], hash_lozinka)
		mycursor.execute(upit, vrednosti)
		flash("Novi korisnik je uspešno dodat.")
		con.commit()
		return redirect(url_for('Ak_Korisnici'))	

@app.route('/ak_korisnik_izmena/<string:id_data>', methods=['GET', 'POST'])
@login_required_ak
def Ak_Korisnik_Izmena(id_data):


	if request.method == "GET":

		upit = "SELECT *, nazivKompanije(kompanija) AS naziv_kompanije, nazivRole(rola) AS naziv_role FROM korisnici WHERE id_korisnika = %s"
		vrednost = (id_data,)
		mycursor.execute(upit, vrednost)
		korisnici = mycursor.fetchone()

		upit1="SELECT * FROM kompanije WHERE naziv_kompanije NOT IN (SELECT nazivKompanije(kompanija) AS naziv_kompanije FROM korisnici WHERE id_korisnika = %s)"
		mycursor.execute(upit1, vrednost)
		kompanije = mycursor.fetchall()

		upit2="SELECT * FROM role WHERE naziv_role NOT IN (SELECT nazivRole(rola) AS naziv_role FROM korisnici WHERE id_korisnika = %s)"
			
		mycursor.execute(upit2, vrednost)
		rola = mycursor.fetchall()

		return render_template("ak_korisnik_izmena.html", korisnici = korisnici, kompanije = kompanije, rola=rola)

	elif request.method == "POST":

		forma = request.form

		upit = """UPDATE korisnici SET 
			    ime = %s,
			    prezime = %s,
			    kompanija = %s,
			    rola = %s,
			    email = %s,
			    korisnicko_ime = %s
			    WHERE id_korisnika=%s"""
		vrednosti = (
			forma['ime'], 
			forma['prezime'], 
			forma['kompanija'], 
			forma['rola'], 
			forma['email'], 
			forma['korisnicko_ime'],
			id_data
		)
		mycursor.execute(upit, vrednosti)
		con.commit()
		flash("Izmena je uspešno izvršena.")

		return redirect(url_for('Ak_Korisnici'))

@app.route('/ak_promena_lozinke/<string:id_data>', methods=['GET', 'POST'])
@login_required_ak
def Ak_Promena_Lozinke(id_data):

	if request.method == 'GET':

		upit = "SELECT * FROM korisnici WHERE id_korisnika = %s"
		vrednost = (id_data,)
		mycursor.execute(upit, vrednost)
		korisnik = mycursor.fetchone()

		return render_template('ak_promena_lozinke.html', korisnik = korisnik)

	elif request.method == 'POST':

		forma = request.form
		lozinka = forma['lozinka']
		potvrda_lozinke = forma['potvrda_lozinke']
	
		if lozinka == potvrda_lozinke:
			lozinka = generate_password_hash(lozinka)
			mycursor.execute("UPDATE korisnici SET lozinka=%s WHERE id_korisnika=%s", (lozinka, id_data))
			flash("Lozinka je uspešno promenjena.", "info")
			con.commit()
			return redirect(url_for('Ak_Korisnici'))
		else:
			flash('Lozinke se ne poklapaju!', 'danger')
			return redirect(request.referrer)

@app.route('/ak_korisnik_brisanje/<string:id_data>', methods = ['GET', 'POST'])
@login_required_ak
def Ak_Korisnik_Brisanje(id_data):


	mycursor = con.cursor()
	upit= "DELETE FROM korisnici WHERE id_korisnika = %s"
	vrednost = (id_data,)
	mycursor.execute(upit, vrednost)
	flash("Korisnik je obrisan.")
	con.commit()

	return redirect(url_for('Ak_Korisnici'))

#-----> KOMPANIJE <-----	

@app.route('/ak_kompanije')
@login_required_ak
def Ak_Kompanije():

	upit = "SELECT * FROM kompanije"
	mycursor.execute(upit)
	kompanije = mycursor.fetchall()

	return render_template("ak_kompanije.html", kompanije=kompanije)

@app.route('/ak_nova_kompanija', methods=['GET', 'POST'])
@login_required_ak
def Ak_Nova_Kompanija():


	if request.method == 'POST':

		forma = request.form
		upit = "INSERT INTO kompanije (naziv_kompanije, adresa, broj_telefona) VALUES (%s, %s, %s)"
		vrednosti = (forma['naziv_kompanije'], forma['adresa'], forma['broj_telefona'])
		mycursor.execute(upit, vrednosti)
		flash("Nova kompanija je uspešno dodata.")
		con.commit()
		return redirect(url_for('Ak_Kompanije'))
	else:
		return render_template('ak_nova_kompanija.html')
	
@app.route('/ak_kompanija_izmena/<string:id_data>', methods=['GET', 'POST'])
@login_required_ak
def Ak_Kompanija_Izmena(id_data):


	if request.method == "GET":

		upit= "SELECT * FROM kompanije WHERE id_kompanije = %s"
		vrednost = (id_data,)
		mycursor.execute(upit, vrednost)
		kompanije = mycursor.fetchone()
		return render_template("ak_kompanija_izmena.html", kompanije = kompanije)

	elif request.method == "POST":

		upit = """UPDATE kompanije SET 
				naziv_kompanije = %s,
				adresa = %s,
				broj_telefona = %s
				WHERE id_kompanije=%s"""
			
		forma = request.form
		vrednosti = (
			forma['naziv_kompanije'],
			forma['adresa'], 
			forma['broj_telefona'],
			id_data
			)
		mycursor.execute(upit, vrednosti)
		con.commit()
		flash("Izmena je uspešno izvršena.")

		return redirect(url_for("Ak_Kompanije"))

@app.route('/ak_kompanija_brisanje/<string:id_data>', methods = ['GET', 'POST'])
@login_required_ak
def Ak_Kompanija_Brisanje(id_data):


	mycursor = con.cursor()
	upit= "DELETE FROM kompanije WHERE id_kompanije = %s"
	vrednost = (id_data,)
	mycursor.execute(upit, vrednost)
	flash("Kompanija je obrisana.")
	con.commit()

	return redirect(url_for('Ak_Kompanije'))

#-----> TIP ZAHTEVA <-----

@app.route('/ak_tip_zahteva', methods=['GET', 'POST'])
@login_required_ak
def Ak_Tip_Zahteva():

	upit = "SELECT * FROM tip_zahteva"
	mycursor.execute(upit)
	tip_zahteva = mycursor.fetchall()
	return render_template('ak_tip_zahteva.html', tip_zahteva=tip_zahteva)

@app.route('/ak_novi_tip_zahteva', methods=['GET', 'POST'])
@login_required_ak
def Ak_Novi_Tip_Zahteva():

	if request.method == 'POST':
		forma = request.form
		upit = "INSERT INTO tip_zahteva (naziv_tipa_zahteva, skracena_oznaka) VALUES (%s, %s)"
		vrednosti = (forma['naziv_tipa_zahteva'], forma['skracena_oznaka'])
		mycursor.execute(upit, vrednosti)
		flash("Novi tip zahteva je uspešno dodat.")
		con.commit()
		return redirect(url_for('Ak_Tip_Zahteva'))
	else:
		return render_template('ak_novi_tip_zahteva.html')

@app.route('/ak_tip_zahteva_izmena/<string:id_data>', methods=['GET', 'POST'])
@login_required_ak
def Ak_Tip_Zahteva_Izmena(id_data):


	if request.method == "GET":

		   upit= "SELECT * FROM tip_zahteva WHERE id_tipa_zahteva = %s"
		   vrednost = (id_data,)
		   mycursor.execute(upit, vrednost)
		   tip_zahteva = mycursor.fetchone()

		   return render_template("ak_tip_zahteva_izmena.html", tip_zahteva = tip_zahteva)

	elif request.method == "POST":

		   upit = "UPDATE tip_zahteva SET naziv_tipa_zahteva = %s, skracena_oznaka = %s WHERE id_tipa_zahteva = %s"
		   forma = request.form
		   vrednosti = (forma['naziv_tipa_zahteva'], forma['skracena_oznaka'], id_data)
		   mycursor.execute(upit, vrednosti)
		   con.commit()
		   flash("Izmena je uspešno izvršena.")

		   return redirect(url_for("Ak_Tip_Zahteva"))


@app.route('/ak_tip_zahteva_brisanje/<string:id_data>', methods=['GET', 'POST'])
@login_required_ak 
def Ak_Tip_Zahteva_Brisanje(id_data):

	mycursor = con.cursor()
	upit = "DELETE FROM tip_zahteva WHERE id_tipa_zahteva = %s"
	vrednost = (id_data,)
	mycursor.execute(upit, vrednost)
	flash("Tip zahteva je obrisan.")
	con.commit()
	return redirect(url_for('Ak_Tip_Zahteva'))

#-----------------------------------------------> Zaposleni kompanije <--------------------------------------------------------------

#-----> Zahtevi <-----	

@app.route('/zk_zahtev/<string:id_data>', methods=['GET', 'POST'])
@login_required_zk
def Zk_Zahtev(id_data):

	
		upit = "SELECT *,  nazivStatusa(status) AS naziv_statusa, nazivKompanije(kompanija) AS kompanija_naziv, nazivKompanije(za_kompaniju) AS za_kompaniju_naziv, imePodnosioca(ime_prezime_podnosioca) AS ime, prezimePodnosioca(ime_prezime_podnosioca) AS prezime, nazivTipa(tip_zahteva) AS naziv_tipa FROM zahtevi WHERE id_zahteva = %s"
		vrednost = (id_data,)
		mycursor.execute(upit, vrednost)
		zahtevi = mycursor.fetchone()

		mycursor.execute("SELECT * FROM status")
		status = mycursor.fetchone()

		mycursor.execute("SELECT * FROM tip_zahteva")
		tip_zahteva = mycursor.fetchone()

		return render_template('zk_zahtev.html', zahtevi = zahtevi, status = status, tip_zahteva = tip_zahteva)

@app.route('/zk_zahtevi', methods=['GET', 'POST'])
@login_required_zk
def Zk_Zahtevi():

	if request.method == 'GET':

		upit = "SELECT *, nazivKompanije(kompanija) AS naziv_kompanije, nazivKompanije(za_kompaniju) AS za_kompaniju, nazivStatusa(status) AS naziv_statusa, nazivTipa(tip_zahteva) AS naziv_tipa, imePodnosioca(ime_prezime_podnosioca) AS ime, prezimePodnosioca(ime_prezime_podnosioca) AS prezime FROM zahtevi"
		mycursor.execute(upit)
		zahtevi = mycursor.fetchall()

		mycursor.execute("SELECT * FROM status")
		status = mycursor.fetchall()

		mycursor.execute("SELECT *, nazivKompanije(kompanija) AS kompanija_naziv FROM korisnici")
		podnosilac = mycursor.fetchall()

		mycursor.execute("SELECT * FROM tip_zahteva")
		tip_zahteva = mycursor.fetchall()
		
		return render_template('zk_zahtevi.html', zahtevi = zahtevi, status = status, podnosilac = podnosilac, tip_zahteva = tip_zahteva)



@app.route('/zk_zahtev_izmena/<string:id_data>', methods=['GET', 'POST'])
@login_required_zk
def Zk_Zahtev_Izmena(id_data):

	if request.method == "GET":

		upit= "SELECT *,  nazivStatusa(status) AS naziv_statusa, nazivKompanije(kompanija) AS kompanija_naziv, nazivKompanije(za_kompaniju) AS za_kompaniju_naziv, imePodnosioca(ime_prezime_podnosioca) AS ime, prezimePodnosioca(ime_prezime_podnosioca) AS prezime, nazivTipa(tip_zahteva) AS naziv_tipa FROM zahtevi WHERE id_zahteva = %s"
		vrednost = (id_data,)
		mycursor.execute(upit, vrednost)
		zahtevi = mycursor.fetchone()

		upit2="SELECT * FROM status WHERE tip_statusa NOT IN (SELECT nazivStatusa(status) as naziv_statusa FROM zahtevi WHERE id_zahteva = %s)"
		mycursor.execute(upit2, vrednost)
		status = mycursor.fetchall()

		mycursor.execute("SELECT * FROM tip_zahteva")
		tip_zahteva = mycursor.fetchall()

		a = session['logged_zk']
		res=yaml.full_load(a)
		korisnik_id=res['id_korisnika']

		upit = "SELECT *, nazivKompanije(kompanija) AS kompanija_naziv, nazivRole(rola) AS naziv_role FROM korisnici WHERE id_korisnika=%s"
		vrednosti=(korisnik_id, )
		mycursor.execute(upit, vrednosti)
		korisnik = mycursor.fetchone()

		return render_template("zk_zahtev_izmena.html", zahtevi = zahtevi, status = status, tip_zahteva=tip_zahteva, korisnik = korisnik)

	elif request.method == "POST":

		a = session['logged_zk']
		res=yaml.full_load(a)
		korisnik_id=res['id_korisnika']
		ime=res['ime']
		prezime=res['prezime']
		email = res['email']
		rola = res['rola']
			
		upit = "SELECT *, nazivKompanije(kompanija) AS kompanija_naziv, nazivRole(rola) AS naziv_role FROM korisnici WHERE id_korisnika=%s"
		vrednosti=(korisnik_id, )
		mycursor.execute(upit, vrednosti)
		korisnik = mycursor.fetchone()

		kompanija = korisnik['kompanija_naziv']

		ime_prezime_kompanija = ime + " " + prezime + " - " + kompanija

		poruka = Message(subject='Promena statusa zahteva', sender=(ime_prezime_kompanija, email), recipients=['ticketing.sistem@gmail.com'])
		poruka.body = render_template('mejl_za_slanje_4.html')
		mail.send(poruka)

		upit = """UPDATE zahtevi SET 
			    zahtev = %s,
			    napomena = %s,
			    tip_zahteva = %s,
			    ocekivani_datum = %s,
			    status = %s,
			    komentar = %s,
			    broj_utrosenih_sati = %s
			    WHERE id_zahteva = %s"""
		forma = request.form
		vrednosti = (
			forma['zahtev'],
			forma['napomena'],
			forma['tip_zahteva'],
			forma['ocekivani_datum'],
			forma['status'],
			forma['komentar'],
			forma['broj_utrosenih_sati'],
			id_data
		)
		mycursor.execute(upit, vrednosti)
		con.commit()
		flash("Izmena je uspešno izvršena.")

		return redirect(url_for('Zk_Zahtevi'))


@app.route('/zk_promena_slike/<string:id_data>', methods=['GET', 'POST'])
@login_required_zk
def Zk_Promena_Slike(id_data):

	if request.method == 'GET':

		upit = "SELECT * FROM zahtevi WHERE id_zahteva = %s"
		vrednost = (id_data,)
		mycursor.execute(upit, vrednost)
		zahtevi = mycursor.fetchone()

		return render_template('zk_promena_slike.html', zahtevi = zahtevi)

	elif request.method == 'POST':

		file = request.files['file']

		if file.filename == '':
			flash('Slika nije dodata.')
			return redirect(request.url)

		elif allowed_file(file.filename) is False:
			flash('Izabrani tip fajla nije podržan.')
			return redirect(request.url)

		else:
			filename = secure_filename(file.filename)
			file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

			putanja = (os.path.join(app.config['UPLOAD_FOLDER'], filename))

			upit = """UPDATE zahtevi SET 
			    	slika_kao_opis_zahteva = %s
			    	WHERE id_zahteva = %s"""
			vrednosti = (
				putanja,
				id_data
			)
			mycursor.execute(upit, vrednosti)
			con.commit()
			flash("Slika je uspešno izmenjena.")

			return redirect(url_for('Zk_Zahtevi'))

	

#-----> Nalog <-----	

@app.route('/zk_nalog', methods=['GET', 'POST'])
@login_required_zk
def Zk_Nalog():

	if request.method == 'GET':

		a = session['logged_zk']
		res=yaml.full_load(a)
		korisnik_id=res['id_korisnika']
		kompanija=res['kompanija']

		upit = "SELECT *, nazivKompanije(kompanija) AS kompanija_naziv, nazivRole(rola) AS naziv_role FROM korisnici WHERE id_korisnika=%s"
		vrednosti=(korisnik_id, )
		mycursor.execute(upit, vrednosti)
		korisnik = mycursor.fetchone()

		return render_template('zk_nalog.html', korisnik = korisnik)

	elif request.method == 'POST':

			forma = request.form

			id_data = forma['id_korisnika']
			ime = forma['ime']
			prezime = forma['prezime']
			email = forma['email']
			mycursor.execute("UPDATE korisnici SET ime=%s, prezime=%s, email=%s WHERE id_korisnika=%s", (ime, prezime, email, id_data))
			flash("Izmena je uspešno izvršena.")
			con.commit()

			return redirect(url_for('Zk_Nalog'))

@app.route('/zk_promena_lozinke/<string:id_data>', methods=['GET', 'POST'])
@login_required_zk
def Zk_Promena_Lozinke(id_data):

	if request.method == 'GET':

		upit = "SELECT * FROM korisnici WHERE id_korisnika = %s"
		vrednost = (id_data,)
		mycursor.execute(upit, vrednost)
		korisnik = mycursor.fetchone()

		return render_template('zk_promena_lozinke.html', korisnik = korisnik)

	elif request.method == 'POST':

		forma = request.form
		stara_lozinka = forma['stara_lozinka']
		lozinka = forma['lozinka']
		potvrda_lozinke = forma['potvrda_lozinke']

		if lozinka != potvrda_lozinke:
			flash('Lozinke se ne poklapaju!', 'danger')
			return redirect(request.referrer)

		lozinka = generate_password_hash(lozinka)

		upit = "SELECT * FROM korisnici WHERE id_korisnika = %s"
		vrednost = (id_data,)
		mycursor.execute(upit, vrednost)
		korisnik = mycursor.fetchone()

		old_password = korisnik['lozinka']

		if check_password_hash(old_password, stara_lozinka):
			mycursor.execute("UPDATE korisnici SET lozinka=%s WHERE id_korisnika=%s", (lozinka, id_data))
			flash("Lozinka je uspešno promenjena.", "info")
			con.commit()
			return redirect(url_for('Zk_Nalog'))
		else:
			flash("Stara lozinka je pogrešna", 'danger')
			return redirect(request.referrer)
		

#-----------------------------------------------> Administrator klijentske kompanije <-------------------------------------------------

#-----> Zahtevi <-----

@app.route('/akk_zahtev/<string:id_data>', methods=['GET', 'POST'])
@login_required_akk
def Akk_Zahtev(id_data):

	
		upit = "SELECT *,  nazivStatusa(status) AS naziv_statusa, nazivKompanije(kompanija) AS kompanija_naziv, nazivKompanije(za_kompaniju) AS za_kompaniju_naziv, imePodnosioca(ime_prezime_podnosioca) AS ime, prezimePodnosioca(ime_prezime_podnosioca) AS prezime, nazivTipa(tip_zahteva) AS naziv_tipa FROM zahtevi WHERE id_zahteva = %s"
		vrednost = (id_data,)
		mycursor.execute(upit, vrednost)
		zahtevi = mycursor.fetchone()

		mycursor.execute("SELECT * FROM status")
		status = mycursor.fetchone()

		mycursor.execute("SELECT * FROM tip_zahteva")
		tip_zahteva = mycursor.fetchone()

		return render_template('akk_zahtev.html', zahtevi = zahtevi, status = status, tip_zahteva = tip_zahteva)

@app.route('/akk_zahtevi', methods=['GET', 'POST'])
@login_required_akk
def Akk_Zahtevi():

	a = session['logged_akk']
	res=yaml.full_load(a)
	korisnik_id=res['id_korisnika']

	if request.method == 'GET':
		
		upit = """
			SELECT 
				*,
				korisnici.*, 
				nazivKompanije(zahtevi.kompanija) AS naziv_kompanije, 
				nazivKompanije(za_kompaniju) AS za_kompaniju, 
				nazivStatusa(status) AS naziv_statusa, 
				nazivTipa(tip_zahteva) AS naziv_tipa, 
				imePodnosioca(ime_prezime_podnosioca) AS ime, 
				prezimePodnosioca(ime_prezime_podnosioca) AS prezime 
			FROM zahtevi
			JOIN korisnici
			ON korisnici.id_korisnika = zahtevi.ime_prezime_podnosioca
			WHERE korisnici.kompanija = 
			"""
		upit += "'" + str(res['kompanija']) + "'"
	
		mycursor.execute(upit)
		zahtevi = mycursor.fetchall()

		mycursor.execute("SELECT * FROM status")
		status = mycursor.fetchall()

		upit = """
			SELECT 
				korisnici.*,
				kompanije.*
			FROM korisnici
			JOIN kompanije
			ON korisnici.kompanija = kompanije.id_kompanije
			WHERE korisnici.kompanija = 
			"""
		upit += "'" + str(res['kompanija']) + "'"

		mycursor.execute(upit)
		podnosilac = mycursor.fetchall()

		mycursor.execute("SELECT * FROM tip_zahteva")
		tip_zahteva = mycursor.fetchall()
		
		return render_template('akk_zahtevi.html', zahtevi = zahtevi, status = status, podnosilac = podnosilac, tip_zahteva = tip_zahteva)


@app.route('/akk_novi_zahtev', methods=['GET', 'POST'])
@login_required_akk
def Akk_Novi_Zahtev():

	if request.method == "GET":

		mycursor.execute("SELECT * FROM kompanije WHERE naziv_kompanije = 'VTŠ Apps Team'")
		kompanije = mycursor.fetchone()

		a = session['logged_akk']
		res=yaml.full_load(a)
		korisnik_id=res['id_korisnika']
		kompanija=res['kompanija']

		upit = "SELECT *, nazivKompanije(kompanija) AS kompanija_naziv FROM korisnici WHERE id_korisnika=%s"
		vrednosti=(korisnik_id, )
		mycursor.execute(upit, vrednosti)
		korisnik = mycursor.fetchone()

		mycursor.execute("SELECT MAX(broj_zahteva) AS zahtev_broj FROM zahtevi")
		br = mycursor.fetchone()

		if br['zahtev_broj'] == None:
			br['zahtev_broj'] = 1
		else:
			br['zahtev_broj'] += 1

		return render_template('akk_novi_zahtev.html', kompanije = kompanije, korisnik = korisnik, br=br)
		
	elif request.method == 'POST':

		file = request.files['file']

		if file.filename == '':
			flash('Slika nije dodata.')
			return redirect(request.url)

		elif allowed_file(file.filename) is False:
			flash('Izabrani tip fajla nije podržan.')
			return redirect(request.url)

		else:
			filename = secure_filename(file.filename)
			file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

			putanja = (os.path.join(app.config['UPLOAD_FOLDER'], filename))

			a = session['logged_akk']
			res=yaml.full_load(a)
			korisnik_id=res['id_korisnika']
			ime=res['ime']
			prezime=res['prezime']
			email = res['email']
			
			upit = "SELECT *, nazivKompanije(kompanija) AS kompanija_naziv FROM korisnici WHERE id_korisnika=%s"
			vrednosti=(korisnik_id, )
			mycursor.execute(upit, vrednosti)
			korisnik = mycursor.fetchone()

			kompanija = korisnik['kompanija_naziv']

			ime_prezime_kompanija = ime + " " + prezime + " - " + kompanija

			poruka = Message(subject='Novi zahtev', sender=(ime_prezime_kompanija, email), recipients=['ticketing.sistem@gmail.com'])
			poruka.body = render_template('mejl_za_slanje_3.html')
			mail.send(poruka)

			mycursor.execute("SELECT * FROM status WHERE tip_statusa = 'Otvoren'")
			status = mycursor.fetchone()
			otvoren = status['id_status']

			forma = request.form
			upit = "INSERT INTO zahtevi (broj_zahteva, datum_podnosenja, kompanija, ime_prezime_podnosioca, za_kompaniju, zahtev, slika_kao_opis_zahteva, status) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
			vrednosti = (forma['broj_zahteva'], forma['datum_podnosenja'], forma['kompanija'], forma['ime_prezime_podnosioca'], forma['za_kompaniju'], forma['zahtev'], putanja, otvoren)
			mycursor.execute(upit, vrednosti)
			flash("Zahtev je uspešno kreiran.")
			con.commit()
			
		return redirect(url_for('Akk_Zahtevi'))

@app.route('/akk_zahtev_izmena/<string:id_data>', methods=['GET', 'POST'])
@login_required_akk
def Akk_Zahtev_Izmena(id_data):

	if request.method == "GET":

			upit= "SELECT *,  nazivStatusa(status) AS naziv_statusa, nazivKompanije(kompanija) AS kompanija_naziv, nazivKompanije(za_kompaniju) AS za_kompaniju_naziv, imePodnosioca(ime_prezime_podnosioca) AS ime, prezimePodnosioca(ime_prezime_podnosioca) AS prezime, nazivTipa(tip_zahteva) AS naziv_tipa FROM zahtevi WHERE id_zahteva = %s"
			vrednost = (id_data,)
			mycursor.execute(upit, vrednost)
			zahtevi = mycursor.fetchone()

			mycursor.execute("SELECT * FROM status")
			status = mycursor.fetchall()

			mycursor.execute("SELECT * FROM tip_zahteva")
			tip_zahteva = mycursor.fetchall()

			return render_template("akk_zahtev_izmena.html", zahtevi = zahtevi, status = status, tip_zahteva=tip_zahteva)

	elif request.method == "POST":

			upit = """UPDATE zahtevi SET 
			    	zahtev = %s
			    	WHERE id_zahteva = %s"""
			forma = request.form
			vrednosti = (
				forma['zahtev'],
				id_data
			)
			mycursor.execute(upit, vrednosti)
			con.commit()
			flash("Izmena je uspešno izvršena.")

			return redirect(url_for('Akk_Zahtevi'))

@app.route('/akk_promena_slike/<string:id_data>', methods=['GET', 'POST'])
@login_required_akk
def Akk_Promena_Slike(id_data):

	if request.method == 'GET':

		upit = "SELECT * FROM zahtevi WHERE id_zahteva = %s"
		vrednost = (id_data,)
		mycursor.execute(upit, vrednost)
		zahtevi = mycursor.fetchone()

		return render_template('akk_promena_slike.html', zahtevi = zahtevi)

	elif request.method == 'POST':

		file = request.files['file']

		if file.filename == '':
			flash('Slika nije dodata.')
			return redirect(request.url)

		elif allowed_file(file.filename) is False:
			flash('Izabrani tip fajla nije podržan.')
			return redirect(request.url)

		else:
			filename = secure_filename(file.filename)
			file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

			putanja = (os.path.join(app.config['UPLOAD_FOLDER'], filename))

			upit = """UPDATE zahtevi SET 
			    	slika_kao_opis_zahteva = %s
			    	WHERE id_zahteva = %s"""
			vrednosti = (
				putanja,
				id_data
			)
			mycursor.execute(upit, vrednosti)
			con.commit()
			flash("Slika je uspešno izmenjena.")

			return redirect(url_for('Akk_Zahtevi'))

#-----> Korisnici <-----

@app.route('/akk_korisnici', methods=['GET', 'POST'])
@login_required_akk
def Akk_Korisnici():


	a = session['logged_akk']
	res=yaml.full_load(a)

	upit = """
		SELECT 
			korisnici.*,
			kompanije.*, 
			nazivKompanije(korisnici.kompanija) AS naziv_kompanije, 
			nazivRole(rola) AS naziv_role  
		FROM korisnici
		JOIN kompanije
		ON korisnici.kompanija = kompanije.id_kompanije
		WHERE korisnici.kompanija = 
		"""
	upit += "'" + str(res['kompanija']) + "'"

	mycursor.execute(upit)
	korisnici = mycursor.fetchall()


	mycursor.execute("SELECT * FROM role WHERE naziv_role = 'Administrator klijentske kompanije' OR naziv_role = 'Zaposleni klijentske kompanije'")
	rola = mycursor.fetchall()
	return render_template('akk_korisnici.html', korisnici = korisnici, rola = rola)


@app.route('/akk_novi_korisnik', methods=['GET', 'POST'])
@login_required_akk
def Akk_Novi_Korisnik():

	if request.method == "GET":

		a = session['logged_akk']
		res=yaml.full_load(a)
		korisnik_id=res['id_korisnika']
		kompanija=res['kompanija']

		upit = "SELECT *, nazivKompanije(kompanija) AS kompanija_naziv FROM korisnici WHERE id_korisnika=%s"
		vrednosti=(korisnik_id, )
		mycursor.execute(upit, vrednosti)
		korisnik = mycursor.fetchone()

		kompanija=res['kompanija']

		mycursor.execute("SELECT * FROM kompanije")
		kompanije = mycursor.fetchall()

		mycursor.execute("SELECT * FROM role WHERE naziv_role = 'Administrator klijentske kompanije' OR naziv_role = 'Zaposleni klijentske kompanije'")
		rola = mycursor.fetchall()	
		return render_template('akk_novi_korisnik.html', kompanije=kompanije, rola=rola, korisnik = korisnik)
		
	elif request.method == 'POST':

		forma = request.form

		poruka = Message(subject='Korisnički nalog', sender=('Ticketing Sistem', 'ticketing.sistem@gmail.com'), recipients=[request.form['email']])
		poruka.body = render_template('mejl_za_slanje_2.html')
		mail.send(poruka)

		upit = "INSERT INTO korisnici (ime,	prezime, kompanija, rola, email, korisnicko_ime, lozinka) VALUES (%s, %s, %s, %s, %s, %s, %s)"
		hash_lozinka = generate_password_hash(forma['lozinka'])
		vrednosti = (forma['ime'], forma['prezime'], forma['kompanija'], forma['rola'], forma['email'], forma['korisnicko_ime'], hash_lozinka)
		mycursor.execute(upit, vrednosti)
		flash("Novi korisnik je uspešno dodat.")
		con.commit()
		return redirect(url_for('Akk_Korisnici'))	

@app.route('/akk_korisnik_izmena/<string:id_data>', methods=['GET', 'POST'])
@login_required_akk
def Akk_Korisnik_Izmena(id_data):


	if request.method == "GET":

		upit = "SELECT *, nazivKompanije(kompanija) AS naziv_kompanije, nazivRole(rola) AS naziv_role FROM korisnici WHERE id_korisnika = %s"
		vrednost = (id_data,)
		mycursor.execute(upit, vrednost)
		korisnici = mycursor.fetchone()

		mycursor.execute("SELECT * FROM role WHERE naziv_role = 'Administrator klijentske kompanije' OR naziv_role = 'Zaposleni klijentske kompanije'")
		rola = mycursor.fetchall()

		return render_template("akk_korisnik_izmena.html", korisnici = korisnici, rola=rola)

	elif request.method == "POST":

		lozinka = generate_password_hash(request.form['lozinka'])

		upit = """UPDATE korisnici SET 
			    ime = %s,
			    prezime = %s,
			    rola = %s,
			    email = %s,
			    korisnicko_ime = %s
			    WHERE id_korisnika=%s"""
		forma = request.form
		vrednosti = (
			forma['ime'], 
			forma['prezime'],  
			forma['rola'], 
			forma['email'], 
			forma['korisnicko_ime'],
			id_data
		)
		mycursor.execute(upit, vrednosti)
		con.commit()
		flash("Izmena je uspešno izvršena.")

		return redirect(url_for('Akk_Korisnici'))


@app.route('/akk_promena_lozinke/<string:id_data>', methods=['GET', 'POST'])
@login_required_akk
def Akk_Promena_Lozinke(id_data):

	if request.method == 'GET':

		upit = "SELECT * FROM korisnici WHERE id_korisnika = %s"
		vrednost = (id_data,)
		mycursor.execute(upit, vrednost)
		korisnik = mycursor.fetchone()

		return render_template('akk_promena_lozinke.html', korisnik = korisnik)

	elif request.method == 'POST':

		forma = request.form
		lozinka = forma['lozinka']
		potvrda_lozinke = forma['potvrda_lozinke']
	
		if lozinka == potvrda_lozinke:
			lozinka = generate_password_hash(lozinka)
			mycursor.execute("UPDATE korisnici SET lozinka=%s WHERE id_korisnika=%s", (lozinka, id_data))
			flash("Lozinka je uspešno promenjena.", "info")
			con.commit()
			return redirect(url_for('Akk_Korisnici'))
		else:
			flash('Lozinke se ne poklapaju!', 'danger')
			return redirect(request.referrer)


@app.route('/akk_korisnik_brisanje/<string:id_data>', methods = ['GET', 'POST'])
@login_required_akk
def Akk_Korisnik_Brisanje(id_data):


	mycursor = con.cursor()
	upit= "DELETE FROM korisnici WHERE id_korisnika = %s"
	vrednost = (id_data,)
	mycursor.execute(upit, vrednost)
	flash("Korisnik je obrisan.")
	con.commit()

	return redirect(url_for('Akk_Korisnici'))

#-----------------------------------------------> Zaposleni klijentske kompanije <------------------------------------------------

#-----> Zahtevi <-----	

@app.route('/zkk_zahtev/<string:id_data>', methods=['GET', 'POST'])
@login_required_zkk
def Zkk_Zahtev(id_data):

	
		upit = "SELECT *,  nazivStatusa(status) AS naziv_statusa, nazivKompanije(kompanija) AS kompanija_naziv, nazivKompanije(za_kompaniju) AS za_kompaniju_naziv, imePodnosioca(ime_prezime_podnosioca) AS ime, prezimePodnosioca(ime_prezime_podnosioca) AS prezime, nazivTipa(tip_zahteva) AS naziv_tipa FROM zahtevi WHERE id_zahteva = %s"
		vrednost = (id_data,)
		mycursor.execute(upit, vrednost)
		zahtevi = mycursor.fetchone()

		mycursor.execute("SELECT * FROM status")
		status = mycursor.fetchone()

		mycursor.execute("SELECT * FROM tip_zahteva")
		tip_zahteva = mycursor.fetchone()

		return render_template('zkk_zahtev.html', zahtevi = zahtevi, status = status, tip_zahteva = tip_zahteva)

@app.route('/zkk_zahtevi', methods=['GET', 'POST'])
@login_required_zkk
def Zkk_Zahtevi():

	a = session['logged_zkk']
	res=yaml.full_load(a)
	korisnik_id=res['id_korisnika']

	if request.method == 'GET':
		
		upit = """
			SELECT 
				*,
				korisnici.*, 
				nazivKompanije(zahtevi.kompanija) AS naziv_kompanije, 
				nazivKompanije(za_kompaniju) AS za_kompaniju, 
				nazivStatusa(status) AS naziv_statusa, 
				nazivTipa(tip_zahteva) AS naziv_tipa, 
				imePodnosioca(ime_prezime_podnosioca) AS ime, 
				prezimePodnosioca(ime_prezime_podnosioca) AS prezime 
			FROM zahtevi
			JOIN korisnici
			ON korisnici.id_korisnika = zahtevi.ime_prezime_podnosioca
			WHERE korisnici.kompanija = 
			"""
		upit += "'" + str(res['kompanija']) + "'"
	
		mycursor.execute(upit)
		zahtevi = mycursor.fetchall()

		mycursor.execute("SELECT * FROM status")
		status = mycursor.fetchall()

		upit = """
			SELECT 
				korisnici.*,
				kompanije.*
			FROM korisnici
			JOIN kompanije
			ON korisnici.kompanija = kompanije.id_kompanije
			WHERE korisnici.kompanija = 
			"""
		upit += "'" + str(res['kompanija']) + "'"

		mycursor.execute(upit)
		podnosilac = mycursor.fetchall()

		mycursor.execute("SELECT * FROM tip_zahteva")
		tip_zahteva = mycursor.fetchall()
		
		return render_template('zkk_zahtevi.html', zahtevi = zahtevi, status = status, podnosilac = podnosilac, tip_zahteva = tip_zahteva)

@app.route('/zkk_novi_zahtev', methods=['GET', 'POST'])
@login_required_zkk
def Zkk_Novi_Zahtev():

	if request.method == "GET":

		mycursor.execute("SELECT * FROM kompanije WHERE naziv_kompanije = 'VTŠ Apps Team'")
		kompanije = mycursor.fetchone()

		a = session['logged_zkk']
		res=yaml.full_load(a)
		korisnik_id=res['id_korisnika']
		kompanija=res['kompanija']

		upit = "SELECT *, nazivKompanije(kompanija) AS kompanija_naziv FROM korisnici WHERE id_korisnika=%s"
		vrednosti=(korisnik_id, )
		mycursor.execute(upit, vrednosti)
		korisnik = mycursor.fetchone()

		mycursor.execute("SELECT MAX(broj_zahteva) AS zahtev_broj FROM zahtevi")
		br = mycursor.fetchone()

		if br['zahtev_broj'] == None:
			br['zahtev_broj'] = 1
		else:
			br['zahtev_broj'] += 1

		return render_template('zkk_novi_zahtev.html', kompanije = kompanije, korisnik = korisnik, br=br)
		
	elif request.method == 'POST':

		file = request.files['file']
		if file.filename == '':
			flash('Slika nije dodata.')
			return redirect(request.url)
		elif allowed_file(file.filename) is False:
			flash('Izabrani tip fajla nije podržan.')
			return redirect(request.url)
		else:
			filename = secure_filename(file.filename)
			file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

			putanja = (os.path.join(app.config['UPLOAD_FOLDER'], filename))

			a = session['logged_zkk']
			res=yaml.full_load(a)
			korisnik_id=res['id_korisnika']
			ime=res['ime']
			prezime=res['prezime']
			email = res['email']
			
			upit = "SELECT *, nazivKompanije(kompanija) AS kompanija_naziv FROM korisnici WHERE id_korisnika=%s"
			vrednosti=(korisnik_id, )
			mycursor.execute(upit, vrednosti)
			korisnik = mycursor.fetchone()

			kompanija = korisnik['kompanija_naziv']

			ime_prezime_kompanija = ime + " " + prezime + " - " + kompanija

			poruka = Message(subject='Novi zahtev', sender=(ime_prezime_kompanija, email), recipients=['ticketing.sistem@gmail.com'])
			poruka.body = render_template('mejl_za_slanje_3.html')
			mail.send(poruka)

			mycursor.execute("SELECT * FROM status WHERE tip_statusa = 'Otvoren'")
			status = mycursor.fetchone()
			otvoren = status['id_status']

			forma = request.form
			upit = "INSERT INTO zahtevi (broj_zahteva, datum_podnosenja, kompanija, ime_prezime_podnosioca, za_kompaniju, zahtev, slika_kao_opis_zahteva, status) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
			vrednosti = (forma['broj_zahteva'], forma['datum_podnosenja'], forma['kompanija'], forma['ime_prezime_podnosioca'], forma['za_kompaniju'], forma['zahtev'], putanja, otvoren)
			mycursor.execute(upit, vrednosti)
			flash("Zahtev je uspešno kreiran.")
			con.commit()
			
		return redirect(url_for('Zkk_Zahtevi'))

@app.route('/zkk_zahtev_izmena/<string:id_data>', methods=['GET', 'POST'])
@login_required_zkk
def Zkk_Zahtev_Izmena(id_data):

	if request.method == "GET":

			upit= "SELECT *,  nazivStatusa(status) AS naziv_statusa, nazivKompanije(kompanija) AS kompanija_naziv, nazivKompanije(za_kompaniju) AS za_kompaniju_naziv, imePodnosioca(ime_prezime_podnosioca) AS ime, prezimePodnosioca(ime_prezime_podnosioca) AS prezime, nazivTipa(tip_zahteva) AS naziv_tipa FROM zahtevi WHERE id_zahteva = %s"
			vrednost = (id_data,)
			mycursor.execute(upit, vrednost)
			zahtevi = mycursor.fetchone()

			mycursor.execute("SELECT * FROM status")
			status = mycursor.fetchall()

			mycursor.execute("SELECT * FROM tip_zahteva")
			tip_zahteva = mycursor.fetchall()

			return render_template("zkk_zahtev_izmena.html", zahtevi = zahtevi, status = status, tip_zahteva=tip_zahteva)

	elif request.method == "POST":

			upit = """UPDATE zahtevi SET 
			    	zahtev = %s
			    	WHERE id_zahteva = %s"""
			forma = request.form
			vrednosti = (
				forma['zahtev'],
				id_data
			)
			mycursor.execute(upit, vrednosti)
			con.commit()
			flash("Izmena je uspešno izvršena.")

			return redirect(url_for('Zkk_Zahtevi'))

@app.route('/zkk_promena_slike/<string:id_data>', methods=['GET', 'POST'])
@login_required_zkk
def Zkk_Promena_Slike(id_data):

	if request.method == 'GET':

		upit = "SELECT * FROM zahtevi WHERE id_zahteva = %s"
		vrednost = (id_data,)
		mycursor.execute(upit, vrednost)
		zahtevi = mycursor.fetchone()

		return render_template('zkk_promena_slike.html', zahtevi = zahtevi)

	elif request.method == 'POST':

		file = request.files['file']

		if file.filename == '':
			flash('Slika nije dodata.')
			return redirect(request.url)

		elif allowed_file(file.filename) is False:
			flash('Izabrani tip fajla nije podržan.')
			return redirect(request.url)

		else:
			filename = secure_filename(file.filename)
			file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

			putanja = (os.path.join(app.config['UPLOAD_FOLDER'], filename))

			upit = """UPDATE zahtevi SET 
			    	slika_kao_opis_zahteva = %s
			    	WHERE id_zahteva = %s"""
			vrednosti = (
				putanja,
				id_data
			)
			mycursor.execute(upit, vrednosti)
			con.commit()
			flash("Slika je uspešno izmenjena.")

			return redirect(url_for('Zkk_Zahtevi'))

#-----> Nalog <-----

@app.route('/zkk_nalog', methods=['GET', 'POST'])
@login_required_zkk
def Zkk_Nalog():

	if request.method == 'GET':

		a = session['logged_zkk']
		res=yaml.full_load(a)
		korisnik_id=res['id_korisnika']
		kompanija=res['kompanija']

		upit = "SELECT *, nazivKompanije(kompanija) AS kompanija_naziv, nazivRole(rola) AS naziv_role FROM korisnici WHERE id_korisnika=%s"
		vrednosti=(korisnik_id, )
		mycursor.execute(upit, vrednosti)
		korisnik = mycursor.fetchone()

		return render_template('zkk_nalog.html', korisnik = korisnik)

	elif request.method == 'POST':

			forma = request.form

			id_data = forma['id_korisnika']
			ime = forma['ime']
			prezime = forma['prezime']
			email = forma['email']
			mycursor.execute("UPDATE korisnici SET ime=%s, prezime=%s, email=%s WHERE id_korisnika=%s", (ime, prezime, email, id_data))
			flash("Izmena je uspešno izvršena.")
			con.commit()

			return redirect(url_for('Zkk_Nalog'))


@app.route('/zkk_promena_lozinke/<string:id_data>', methods=['GET', 'POST'])
@login_required_zkk
def Zkk_Promena_Lozinke(id_data):

	if request.method == 'GET':

		upit = "SELECT * FROM korisnici WHERE id_korisnika = %s"
		vrednost = (id_data,)
		mycursor.execute(upit, vrednost)
		korisnik = mycursor.fetchone()

		return render_template('zkk_promena_lozinke.html', korisnik = korisnik)

	elif request.method == 'POST':

		forma = request.form
		stara_lozinka = forma['stara_lozinka']
		lozinka = forma['lozinka']
		potvrda_lozinke = forma['potvrda_lozinke']

		if lozinka != potvrda_lozinke:
			flash('Lozinke se ne poklapaju!', 'danger')
			return redirect(request.referrer)

		lozinka = generate_password_hash(lozinka)

		upit = "SELECT * FROM korisnici WHERE id_korisnika = %s"
		vrednost = (id_data,)
		mycursor.execute(upit, vrednost)
		korisnik = mycursor.fetchone()

		old_password = korisnik['lozinka']

		if check_password_hash(old_password, stara_lozinka):
			mycursor.execute("UPDATE korisnici SET lozinka=%s WHERE id_korisnika=%s", (lozinka, id_data))
			flash("Lozinka je uspešno promenjena.", "info")
			con.commit()
			return redirect(url_for('Zkk_Nalog'))
		else:
			flash("Stara lozinka je pogrešna", 'danger')
			return redirect(request.referrer)

#-------------------------------------------------------------------------------------------------------------------------------------------------------------

#-----------------------------------------------> Pretrage <--------------------------------------------------------------------------------------------------

@app.route('/ak_zahtevi_rezultati_pretrage', methods=['GET', 'POST'])
@login_required_ak
def Ak_Zahtevi_Rezultati():

	if isLogged_Ak():

		if request.method == 'POST':
			
			forma = request.form
			ime_prezime_podnosioca = forma['ime_prezime_podnosioca']
			status = forma['status']
			tip_zahteva = forma['tip_zahteva']
			datum_podnosenja = forma['datum_podnosenja']
			
			str = """
				SELECT 
					korisnici.ime,
					korisnici.prezime,
					status.tip_statusa,
					tip_zahteva.skracena_oznaka,
					zahtevi.*,
					kompanije.*,
					nazivKompanije(za_kompaniju) AS za_kompaniju
				FROM 
					korisnici
				JOIN zahtevi
				ON
					korisnici.id_korisnika=zahtevi.ime_prezime_podnosioca
				JOIN tip_zahteva
				ON 
					tip_zahteva.id_tipa_zahteva=zahtevi.tip_zahteva
				JOIN status
				ON 
					status.id_status=zahtevi.status
				JOIN kompanije
				ON 
					korisnici.kompanija = kompanije.id_kompanije
			"""   
			str += 'WHERE '
			if ime_prezime_podnosioca is not None and is_not_blank(ime_prezime_podnosioca):
				str += "ime_prezime_podnosioca = '" + ime_prezime_podnosioca + "' AND "
			if status is not None and is_not_blank(status):
				str += "status='" + status + "' AND "
			if tip_zahteva is not None and is_not_blank(tip_zahteva):
				str += "tip_zahteva='" + tip_zahteva + "' AND "
			if datum_podnosenja is not None and is_not_blank(datum_podnosenja):
				str += "datum_podnosenja='" + datum_podnosenja + "' AND "
			
			str += '1'

			mycursor.execute(str)
			zahtevi = mycursor.fetchall()
			con.commit()
			
			return render_template('ak_zahtevi_rezultati_pretrage.html', zahtevi = zahtevi)
	else:
		return redirect(url_for('Login'))


@app.route('/zk_zahtevi_rezultati_pretrage', methods=['GET', 'POST'])
@login_required_zk
def Zk_Zahtevi_Rezultati():

		if request.method == 'POST':
			
			forma = request.form
			ime_prezime_podnosioca = forma['ime_prezime_podnosioca']
			status = forma['status']
			tip_zahteva = forma['tip_zahteva']
			datum_podnosenja = forma['datum_podnosenja']
			
			str = """
				SELECT 
					korisnici.ime,
					korisnici.prezime,
					status.tip_statusa,
					tip_zahteva.skracena_oznaka,
					zahtevi.*,
					kompanije.*,
					nazivKompanije(za_kompaniju) AS za_kompaniju
				FROM 
					korisnici
				JOIN zahtevi
				ON
					korisnici.id_korisnika=zahtevi.ime_prezime_podnosioca
				JOIN tip_zahteva
				ON 
					tip_zahteva.id_tipa_zahteva=zahtevi.tip_zahteva
				JOIN status
				ON 
					status.id_status=zahtevi.status
				JOIN kompanije
				ON 
					korisnici.kompanija = kompanije.id_kompanije
			"""   
			str += 'WHERE '
			if ime_prezime_podnosioca is not None and is_not_blank(ime_prezime_podnosioca):
				str += "ime_prezime_podnosioca = '" + ime_prezime_podnosioca + "' AND "
			if status is not None and is_not_blank(status):
				str += "status='" + status + "' AND "
			if tip_zahteva is not None and is_not_blank(tip_zahteva):
				str += "tip_zahteva='" + tip_zahteva + "' AND "
			if datum_podnosenja is not None and is_not_blank(datum_podnosenja):
				str += "datum_podnosenja='" + datum_podnosenja + "' AND "
			
			str += '1'

			mycursor.execute(str)
			zahtevi = mycursor.fetchall()
			con.commit()
			
			return render_template('zk_zahtevi_rezultati_pretrage.html', zahtevi = zahtevi)

@app.route('/akk_zahtevi_rezultati_pretrage', methods=['GET', 'POST'])
@login_required_akk
def Akk_Zahtevi_Rezultati():

		if request.method == 'POST':
			
			forma = request.form
			ime_prezime_podnosioca = forma['ime_prezime_podnosioca']
			status = forma['status']
			tip_zahteva = forma['tip_zahteva']
			datum_podnosenja = forma['datum_podnosenja']

			a = session['logged_akk']
			res=yaml.full_load(a)
			kompanija=res['kompanija']
			
			upit = """
				SELECT 
					korisnici.*,
					status.tip_statusa,
					tip_zahteva.skracena_oznaka,
					zahtevi.*,
					kompanije.*,
					nazivKompanije(za_kompaniju) AS za_kompaniju
				FROM 
					korisnici
				JOIN zahtevi
				ON
					korisnici.id_korisnika=zahtevi.ime_prezime_podnosioca
				JOIN tip_zahteva
				ON 
					tip_zahteva.id_tipa_zahteva=zahtevi.tip_zahteva
				JOIN status
				ON 
					status.id_status=zahtevi.status
				JOIN kompanije
				ON 
					korisnici.kompanija = kompanije.id_kompanije
			"""   
			upit += 'WHERE korisnici.kompanija = '

			upit += "'" + str(res['kompanija']) + "' AND "

			if ime_prezime_podnosioca is not None and is_not_blank(ime_prezime_podnosioca):
				upit += "ime_prezime_podnosioca = '" + ime_prezime_podnosioca + "' AND "
			if status is not None and is_not_blank(status):
				upit += "status='" + status + "' AND "
			if tip_zahteva is not None and is_not_blank(tip_zahteva):
				upit += "tip_zahteva='" + tip_zahteva + "' AND "
			if datum_podnosenja is not None and is_not_blank(datum_podnosenja):
				upit += "datum_podnosenja='" + datum_podnosenja + "' AND "
			
			upit += '1'
			

			mycursor.execute(upit)
			zahtevi = mycursor.fetchall()
			con.commit()
			
			return render_template('akk_zahtevi_rezultati_pretrage.html', zahtevi = zahtevi)

@app.route('/zkk_zahtevi_rezultati_pretrage', methods=['GET', 'POST'])
@login_required_zkk
def Zkk_Zahtevi_Rezultati():

		if request.method == 'POST':
			
			forma = request.form
			ime_prezime_podnosioca = forma['ime_prezime_podnosioca']
			status = forma['status']
			tip_zahteva = forma['tip_zahteva']
			datum_podnosenja = forma['datum_podnosenja']

			a = session['logged_zkk']
			res=yaml.full_load(a)
			kompanija=res['kompanija']
			
			upit = """
				SELECT 
					korisnici.*,
					status.tip_statusa,
					tip_zahteva.skracena_oznaka,
					zahtevi.*,
					kompanije.*,
					nazivKompanije(za_kompaniju) AS za_kompaniju
				FROM 
					korisnici
				JOIN zahtevi
				ON
					korisnici.id_korisnika=zahtevi.ime_prezime_podnosioca
				JOIN tip_zahteva
				ON 
					tip_zahteva.id_tipa_zahteva=zahtevi.tip_zahteva
				JOIN status
				ON 
					status.id_status=zahtevi.status
				JOIN kompanije
				ON 
					korisnici.kompanija = kompanije.id_kompanije
			"""   
			upit += 'WHERE korisnici.kompanija = '

			upit += "'" + str(res['kompanija']) + "' AND "

			if ime_prezime_podnosioca is not None and is_not_blank(ime_prezime_podnosioca):
				upit += "ime_prezime_podnosioca = '" + ime_prezime_podnosioca + "' AND "
			if status is not None and is_not_blank(status):
				upit += "status='" + status + "' AND "
			if tip_zahteva is not None and is_not_blank(tip_zahteva):
				upit += "tip_zahteva='" + tip_zahteva + "' AND "
			if datum_podnosenja is not None and is_not_blank(datum_podnosenja):
				upit += "datum_podnosenja='" + datum_podnosenja + "' AND "
			
			upit += '1'
			
			mycursor.execute(upit)
			zahtevi = mycursor.fetchall()
			con.commit()
			
			return render_template('zkk_zahtevi_rezultati_pretrage.html', zahtevi = zahtevi)

@app.route('/ak_korisnici_rezultati_pretrage', methods=['GET', 'POST'])
@login_required_ak
def Ak_Korisnici_Rezultati():

	if isLogged_Ak():

		if request.method == 'POST':
			forma = request.form
			kompanija = forma['kompanija']
			ime = forma['ime']
			prezime = forma['prezime']

			str = """
				SELECT 
					korisnici.*,
					nazivKompanije(kompanija) AS naziv_kompanije,
					nazivRole(rola) AS naziv_role
				FROM 
					korisnici
				JOIN kompanije
				ON 
					korisnici.kompanija = kompanije.id_kompanije
			"""   
			str += 'WHERE '
			if kompanija is not None and is_not_blank(kompanija):
				str += "kompanija = '" + kompanija + "' AND "
			if ime is not None and is_not_blank(ime):
				str += "ime ='" + ime + "' AND "
			if prezime is not None and is_not_blank(prezime):
				str += "prezime ='" + prezime + "' AND "
			
			str += '1'

			mycursor.execute(str)
			korisnici = mycursor.fetchall()
			con.commit()
			
			return render_template('ak_korisnici_rezultati_pretrage.html', korisnici = korisnici)
	else:
		return redirect(url_for('Login'))

@app.route('/akk_korisnici_rezultati_pretrage', methods=['GET', 'POST'])
@login_required_akk
def Akk_Korisnici_Rezultati():

		if request.method == 'POST':
			forma = request.form
			rola = forma['rola']
			ime = forma['ime']
			prezime = forma['prezime']

			str = """
				SELECT 
					korisnici.*,
					nazivRole(rola) AS naziv_role
				FROM 
					korisnici
				JOIN role
				ON 
					korisnici.rola = role.id_role
			"""   
			str += 'WHERE '
			if rola is not None and is_not_blank(rola):
				str += "rola = '" + rola + "' AND "
			if ime is not None and is_not_blank(ime):
				str += "ime ='" + ime + "' AND "
			if prezime is not None and is_not_blank(prezime):
				str += "prezime ='" + prezime + "' AND "
			
			str += '1'

			mycursor.execute(str)
			korisnici = mycursor.fetchall()
			con.commit()
			
			return render_template('akk_korisnici_rezultati_pretrage.html', korisnici = korisnici)
#-------------------------------------------------------------------------------------------------------------------------------------------------------------
#-----------------------------------------------> Resetovanje lozinke <--------------------------------------------------------------------------------------------------

@app.route('/reset_forma', methods=['POST', 'GET'])
def Reset_Forma():

	if request.method == 'POST':

		email = request.form['email']
		token = str(uuid.uuid4())
		
		upit = "SELECT * FROM korisnici WHERE email = %s"
		vrednost = (email,)
		mycursor.execute(upit, vrednost)
		korisnik = mycursor.fetchone()

		if korisnik is not None:
			
			poruka = Message(subject='Resetovanje lozinke', sender=('Ticketing Sistem', 'ticketing.sistem@gmail.com'), recipients=[request.form['email']])
			poruka.body = render_template('mejl_za_slanje.html', token=token, korisnik = korisnik)
			mail.send(poruka)
			mycursor.execute("UPDATE korisnici SET token = %s WHERE email = %s", (token, email))
			con.commit()
			flash('Uputstvo je poslato na Vašu e-mail adresu.', 'info')
			return redirect(request.referrer)
			
		else:
			
			flash('Uneti e-mail ne postoji u našem sistemu.', 'danger')
			return redirect(request.referrer)
			

	return render_template('reset_forma.html')


@app.route('/nova_lozinka/<token>', methods=['GET', 'POST'])
def Nova_Lozinka(token):

	if request.method == 'GET':

		upit = "SELECT * FROM korisnici WHERE token = %s"
		vrednost = (token,)
		mycursor.execute(upit, vrednost)
		korisnik = mycursor.fetchone()

		return render_template('nova_lozinka.html', korisnik = korisnik)

	elif request.method == 'POST':
	
		lozinka = request.form['lozinka']
		potvrda = request.form['potvrda']
		token1 = str(uuid.uuid4())
			
		if lozinka != potvrda:
			flash("Lozinke se ne poklapaju.", 'danger')
			return redirect(request.referrer)

		lozinka = generate_password_hash(lozinka)	
		upit = "SELECT * FROM korisnici WHERE token = %s"
		vrednost = (token,)
		mycursor.execute(upit, vrednost)
		korisnik = mycursor.fetchone()

		if korisnik:
				
			mycursor.execute("UPDATE korisnici SET token = %s, lozinka=%s WHERE token = %s", (token1, lozinka, token))
			flash('Lozinka je uspešno promenjena.', 'info')
			con.commit()
			return redirect(url_for('Login'))

		else:
			flash('Token je neispravan.', 'danger')
			return redirect(url_for('Login'))

		return render_template('nova_lozinka.html')

#----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------   

app.run(debug=True)

