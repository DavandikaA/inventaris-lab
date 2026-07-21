from flask import Flask, render_template, request, redirect, session
from supabase import create_client
from datetime import datetime, timedelta

app = Flask(__name__)
app.secret_key = "inventaris123"
url = "https://tuwhswoguvoquovrnhqv.supabase.co"
key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InR1d2hzd29ndXZvcXVvdnJuaHF2Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODIxNDkwMTQsImV4cCI6MjA5NzcyNTAxNH0.q9uy2SCUNnFHZ5IsPe6CVFYsk6pAMqImAoW83-Qh4Xk"

supabase = create_client(url, key)

@app.route("/", methods=["GET", "POST"])
def home():

    if "login" not in session:
        return redirect("/login")

    if request.method == "POST":

        nama_alat = request.form["nama_alat"]
        kategori = request.form["kategori"]
        jumlah = int(request.form["jumlah"])
        kondisi = request.form["kondisi"]

        supabase.table("inventaris").insert({
            "nama_alat": nama_alat,
            "kategori": kategori,
            "jumlah": jumlah,
            "kondisi": kondisi
        }).execute()

        return redirect("/")

    search = request.args.get("search", "")

    if search:
        data = supabase.table("inventaris") \
            .select("*") \
            .ilike("nama_alat", f"%{search}%") \
            .execute()
    else:
        data = supabase.table("inventaris") \
            .select("*") \
            .execute()

    total_data = len(data.data)

    jumlah_baik = 0
    jumlah_rusak = 0

    for item in data.data:
        if item["kondisi"] == "Baik":
            jumlah_baik += 1
        elif item["kondisi"] == "Rusak":
            jumlah_rusak += 1
    for item in data.data:
        if item.get("tanggal_input"):
            dt = datetime.fromisoformat(item["tanggal_input"])
            dt = dt + timedelta(hours=7)

            item["tanggal_wib"] = dt.strftime("%Y-%m-%d %H:%M:%S")

    return render_template(
        "index.html",
        data=data.data,
        total_data=total_data,
        jumlah_baik=jumlah_baik,
        jumlah_rusak=jumlah_rusak,
        search=search
    )
    
@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]

        data = supabase.table("admin") \
            .select("*") \
            .eq("username", username) \
            .eq("password", password) \
            .execute()

        if len(data.data) > 0:

            session["login"] = True

            return redirect("/")

    return render_template("login.html")

@app.route("/hapus/<int:id>")
def hapus(id):

    supabase.table("inventaris").delete().eq("id", id).execute()

    return redirect("/")
@app.route("/logout")
def logout():

    session.clear()

    return redirect("/login")
@app.route("/inventaris")
def inventaris():

    data = supabase.table("inventaris") \
        .select("*") \
        .execute()

    return render_template(
        "inventaris.html",
        data=data.data
    )


@app.route("/laporan")
def laporan():

    data = supabase.table("inventaris") \
        .select("*") \
        .execute()

    for item in data.data:
        if item.get("tanggal_input"):
            dt = datetime.fromisoformat(item["tanggal_input"])
            dt = dt + timedelta(hours=7)

            item["tanggal_wib"] = dt.strftime("%Y-%m-%d %H:%M:%S")

    return render_template(
        "laporan.html",
        data=data.data
    )


@app.route("/tentang")
def tentang():
    return render_template("tentang.html")

@app.route("/edit/<int:id>", methods=["GET", "POST"])
def edit(id):

    if request.method == "POST":

        nama_alat = request.form["nama_alat"]
        kategori = request.form["kategori"]
        jumlah = int(request.form["jumlah"])
        kondisi = request.form["kondisi"]

        supabase.table("inventaris").update({
            "nama_alat": nama_alat,
            "kategori": kategori,
            "jumlah": jumlah,
            "kondisi": kondisi
        }).eq("id", id).execute()

        return redirect("/")

    data = supabase.table("inventaris").select("*").eq("id", id).execute()

    item = data.data[0]

    return render_template(
        "edit.html",
        item=item
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)