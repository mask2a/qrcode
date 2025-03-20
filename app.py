import os
import zipfile
import io
import pandas as pd
import qrcode
from flask import Flask, render_template, request, send_file, redirect, url_for

app = Flask(__name__)
UPLOAD_FOLDER = "uploads"
QR_FOLDER = "qrcodes"
SAMPLE_FILE = "sample.xlsx"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(QR_FOLDER, exist_ok=True)

# 🔹 Trang chính: Chọn chế độ
@app.route("/")
def home():
    return render_template("index.html")

# 🔹 Chế độ 1: Tạo QR từ link
@app.route("/single", methods=["GET", "POST"])
def single_qr():
    qr_file = None
    if request.method == "POST":
        link = request.form["single_link"].strip()
        if link:
            qr_file = generate_qr_and_save(link, "qrcode.png")
    return render_template("single_qr.html", qr_file=qr_file)

@app.route("/batch", methods=["GET", "POST"])
def batch_qr():
    zip_file = None

    if request.method == "POST":
        if "file" in request.files and request.files["file"].filename:
            file = request.files["file"]
            file_path = os.path.join(UPLOAD_FOLDER, file.filename)
            file.save(file_path)
            zip_file = process_excel(file_path)

    return render_template("batch_qr.html", zip_file=zip_file)  # ✅ Đã sửa lỗi
@app.route("/contact", methods=["GET", "POST"])
def contact():
    if request.method == "POST":
        name = request.form["name"]
        phone = request.form["phone"]
        email = request.form["email"]
        message = request.form["message"]

        # Lưu vào file CSV (hoặc database nếu muốn)
        with open("contacts.csv", "a", encoding="utf-8") as file:
            file.write(f"{name},{phone},{email},{message}\n")

        flash("✅ Gửi liên hệ thành công!", "success")
        return redirect(url_for("contact"))

    return render_template("contact.html")

# 🔹 Hàm tạo QR Code từ link
def generate_qr_and_save(data, filename):
    qr_img = generate_qr(data)
    qr_path = os.path.join(QR_FOLDER, filename)
    qr_img.save(qr_path)
    return filename

def generate_qr(data):
    qr = qrcode.QRCode(version=1, error_correction=qrcode.constants.ERROR_CORRECT_L, box_size=10, border=4)
    qr.add_data(data)
    qr.make(fit=True)
    return qr.make_image(fill="black", back_color="white")

# 🔹 Hàm tạo nhiều QR Code từ file Excel
def process_excel(file_path):
    df = pd.read_excel(file_path, usecols=["STT", "Link", "Tên file"])
    zip_filename = "qrcodes.zip"
    zip_path = os.path.join(UPLOAD_FOLDER, zip_filename)

    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
        for _, row in df.iterrows():
            link = row["Link"]
            filename = f"{row['Tên file']}.png"
            qr_file = generate_qr_and_save(link, filename)
            zipf.write(os.path.join(QR_FOLDER, qr_file), filename)

    return zip_filename

# 🔹 Tải file (QR hoặc ZIP)
@app.route("/download/<filename>")
def download_file(filename):
    file_path = os.path.join(QR_FOLDER, filename) if filename.endswith(".png") else os.path.join(UPLOAD_FOLDER, filename)
    return send_file(file_path, as_attachment=True, download_name=filename)

# 🔹 Tải file Excel mẫu
@app.route("/download-sample")
def download_sample():
    sample_data = pd.DataFrame({"STT": [1, 2], "Link": ["https://example.com/abc", "https://example.com/xyz"], "Tên file": ["qr_abc", "qr_xyz"]})
    sample_data.to_excel(SAMPLE_FILE, index=False)
    return send_file(SAMPLE_FILE, as_attachment=True, download_name="file_excel_mau.xlsx")

if __name__ == "__main__":
    app.run(debug=True)
