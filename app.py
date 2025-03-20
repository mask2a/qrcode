import base64
import io
import qrcode
from flask import Flask, render_template, request, send_file

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def home():
    qr_base64 = None
    if request.method == "POST":
        link = request.form.get("link")
        if link:
            qr_base64 = generate_qr(link)  # Lấy QR Code dưới dạng Base64
    
    return render_template("index.html", qr_base64=qr_base64)

def generate_qr(data):
    """Tạo mã QR và mã hóa thành Base64"""
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(data)
    qr.make(fit=True)
    
    img = qr.make_image(fill="black", back_color="white")

    # Chuyển ảnh thành Base64 để hiển thị trên web
    img_io = io.BytesIO()
    img.save(img_io, format="PNG")
    img_io.seek(0)
    img_base64 = base64.b64encode(img_io.getvalue()).decode("utf-8")
    
    return img_base64

@app.route("/download")
def download():
    """Tải ảnh QR về"""
    link = request.args.get("link")
    img_io = generate_qr(link)
    return send_file(io.BytesIO(base64.b64decode(img_io)), mimetype="image/png", as_attachment=True, download_name="qrcode.png")

if __name__ == "__main__":
    app.run(debug=True)
