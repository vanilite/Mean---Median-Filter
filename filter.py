import cv2
import numpy as np
import tkinter as tk
from tkinter import ttk, filedialog
from PIL import ImageTk, Image

def noise_reduction(image, kernel_size_mean, kernel_size_median, num_iterations_recursive):
    # Menerapkan filter mean pada citra
    filtered_mean = cv2.blur(image, (kernel_size_mean, kernel_size_mean))

    # Menerapkan filter median pada citra hasil filter mean
    filtered_median = cv2.medianBlur(filtered_mean, kernel_size_median)

    # Menggabungkan hasil filter mean dan filter median dengan bobot 0.5
    filtered_combination = cv2.addWeighted(filtered_mean, 0.5, filtered_median, 0.5, 0)

    # Menerapkan filter mean secara rekursif
    filtered_recursive = filtered_combination.copy()
    for i in range(num_iterations_recursive):
        filtered_recursive = cv2.blur(filtered_recursive, (kernel_size_mean, kernel_size_mean))

    return filtered_recursive

def remove_blur(image, sharpening_strength):
    # Menerapkan filter dekonvolusi (Wiener) pada citra
    psf = np.ones((7, 7)) / 49  # PSF (Point Spread Function) yang digunakan
    deblurred = cv2.filter2D(image, -1, psf)
    sharpened = cv2.addWeighted(image, 1.0 + sharpening_strength, deblurred, -sharpening_strength, 0)

    return sharpened

def denoise_image(image, filter_size):
    height, width = image.shape
    filtered_image = np.zeros((height, width), dtype=np.uint8)
    offset = filter_size // 2

    for i in range(offset, height - offset):
        for j in range(offset, width - offset):
            neighborhood = image[i-offset:i+offset+1, j-offset:j+offset+1]
            filtered_image[i, j] = np.median(neighborhood)

    return filtered_image

def open_image():
    # Tampilkan dialog pemilihan file untuk memilih gambar
    filepath = filedialog.askopenfilename(filetypes=[("Image Files", "*.png;*.jpg;*.jpeg")])
    if filepath:
        # Baca gambar menggunakan OpenCV
        image = cv2.imread(filepath, 0)  # Mode '0' untuk membaca gambar sebagai citra skala abu-abu

        # Reduksi noise pada gambar
        filtered_image = noise_reduction(image, kernel_size_mean, kernel_size_median, num_iterations_recursive)

        # Hapus derau menggunakan metode kustom
        denoised_image = denoise_image(filtered_image, denoise_filter_size)

        # Hapus kabur menggunakan deblur pada gambar hasil akhir
        final_result = remove_blur(denoised_image, sharpening_strength)

        # Tampilkan gambar asli dan gambar hasil pemrosesan
        show_image(image, final_result, filepath)

def show_image(image, result, filepath):
    # Ubah ukuran gambar agar sesuai dengan jendela tetapi tetap mempertahankan rasio aspek
    resized_image = resize_image(image)
    resized_result = resize_image(result)

    # Konversi gambar ke format yang bisa ditampilkan oleh Tkinter
    img_original = ImageTk.PhotoImage(Image.fromarray(resized_image))
    img_result = ImageTk.PhotoImage(Image.fromarray(resized_result))

    # Buat label untuk menampilkan gambar asli dan nama gambar
    original_name_label.configure(text="Gambar Asli: " + filepath)
    original_name_label.grid(row=2, column=0, columnspan=2, pady=5)

    # Buat label untuk menampilkan gambar asli
    original_label.configure(image=img_original)
    original_label.image = img_original
    original_label.grid(row=3, column=0, padx=10)

    # Buat label untuk menampilkan gambar hasil pemrosesan dan nama gambar
    filtered_name_label.configure(text="Gambar Hasil Pemrosesan")
    filtered_name_label.grid(row=2, column=2, columnspan=2, pady=5)

    # Buat label untuk menampilkan gambar hasil pemrosesan
    result_label.configure(image=img_result)
    result_label.image = img_result
    result_label.grid(row=3, column=2, padx=10)

def resize_image(image):
    height, width = image.shape[:2]
    max_size = min(root.winfo_width() - 20, root.winfo_height() - 100)  # Ukuran maksimum berdasarkan dimensi jendela
    if height > width:
        new_height = max_size
        new_width = int(width * (max_size / height))
    else:
        new_width = max_size
        new_height = int(height * (max_size / width))
    resized_image = cv2.resize(image, (new_width, new_height))
    return resized_image

# Inisialisasi GUI
root = tk.Tk()
root.title("Aplikasi Pengolahan Gambar")

# Buat frame untuk konten
content_frame = ttk.Frame(root)
content_frame.pack(padx=20, pady=10)

# Buat label dengan gaya untuk judul
title_label = ttk.Label(content_frame, text="Aplikasi Pengolahan Gambar", font=("Helvetica", 20, "bold"))
title_label.grid(row=0, column=0, columnspan=4, pady=10)

# Buat tombol untuk membuka gambar
open_button = ttk.Button(content_frame, text="Impor Gambar", command=open_image)
open_button.grid(row=1, column=1, pady=10)

# Buat label untuk menampilkan gambar asli
original_label = ttk.Label(content_frame)
original_label.grid(row=2, column=0, padx=10)

# Buat label untuk menampilkan gambar hasil pemrosesan
result_label = ttk.Label(content_frame)
result_label.grid(row=2, column=3, padx=10)

# Buat label untuk menampilkan nama gambar asli
original_name_label = ttk.Label(content_frame)
original_name_label.grid(row=3, column=0, columnspan=2, pady=5)

# Buat label untuk menampilkan nama gambar hasil pemrosesan
filtered_name_label = ttk.Label(content_frame)
filtered_name_label.grid(row=3, column=2, columnspan=2, pady=5)

# Tentukan parameter untuk reduksi noise
kernel_size_mean = 1
kernel_size_median = 1
num_iterations_recursive = 10
sharpening_strength = 0.5
denoise_filter_size = 5

# Jalankan aplikasi GUI
root.mainloop()
