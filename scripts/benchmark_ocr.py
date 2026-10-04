import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import time

from jiwer import Compose, RemoveMultipleSpaces, RemovePunctuation, ToLowerCase, wer

from letterbuddy.preprocess import preprocess_file

transform = Compose([ToLowerCase(), RemovePunctuation(), RemoveMultipleSpaces()])

def normalize(text):
    return transform(text.replace('\n', ' '))

ground_truth = "National Insurance Company Ltd. Reference: POL/2026/INS/78432 Date: 15th September 2026 Dear Policyholder, Subject: Insurance Policy Renewal Notice for Policy No. LI-2024-567890 Your current Life Insurance policy is due for renewal on 01/11/2026. The annual premium amount is Rs. 12,500/- (Rupees Twelve Thousand Five Hundred Only). Please ensure payment is made before the due date to avoid lapse of coverage. You may pay via NEFT to Account No. XXXX4532 or visit your nearest branch. For queries contact: 1800-123-4567 (toll-free) or email: support@nationalinsurance.example.com. Yours sincerely, Branch Manager Hyderabad Branch"
gt_norm = normalize(ground_truth)

img_path = Path("data/samples/sample_insurance_renewal.jpg")
images = preprocess_file(img_path)

print("--- Benchmarking Tesseract (eng) ---")
import pytesseract

start = time.time()
tess_eng_text = pytesseract.image_to_string(images[0], lang="eng")
tess_eng_time = time.time() - start
print(f"Time: {tess_eng_time:.2f}s")
print(f"WER: {wer(gt_norm, normalize(tess_eng_text)):.2%}")

print("\n--- Benchmarking Tesseract (eng+tel) ---")
start = time.time()
tess_eng_tel_text = pytesseract.image_to_string(images[0], lang="eng+tel")
tess_eng_tel_time = time.time() - start
print(f"Time: {tess_eng_tel_time:.2f}s")
print(f"WER: {wer(gt_norm, normalize(tess_eng_tel_text)):.2%}")

print("\n--- Benchmarking EasyOCR (en, te) ---")
import easyocr

reader = easyocr.Reader(['en', 'te'])
import numpy as np

start = time.time()
# EasyOCR takes numpy arrays
img_np = np.array(images[0])
results = reader.readtext(img_np)
easy_text = " ".join([r[1] for r in results])
easy_time = time.time() - start
print(f"Time: {easy_time:.2f}s")
print(f"WER: {wer(gt_norm, normalize(easy_text)):.2%}")
