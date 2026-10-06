import os

def create_minimal_pdf(filename: str, text_content: str):
    lines = [l.strip() for l in text_content.splitlines() if l.strip()]
    
    stream_lines = ["BT", "/F1 10 Tf", "50 750 Td", "14 TL"]
    for line in lines[:45]:
        clean = line.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")
        stream_lines.append(f"({clean}) '")
    stream_lines.append("ET")
    stream_data = "\n".join(stream_lines).encode("latin1", "replace")
    
    stream_len = len(stream_data)
    
    pdf = bytearray()
    pdf.extend(b"%PDF-1.4\n")
    
    # Obj 1: Catalog
    o1 = len(pdf)
    pdf.extend(b"1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n")
    
    # Obj 2: Pages
    o2 = len(pdf)
    pdf.extend(b"2 0 obj\n<< /Type /Pages /Kids [3 0 R] /Count 1 >>\nendobj\n")
    
    # Obj 3: Page
    o3 = len(pdf)
    pdf.extend(b"3 0 obj\n<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Contents 4 0 R /Resources << /Font << /F1 5 0 R >> >> >>\nendobj\n")
    
    # Obj 4: Content stream
    o4 = len(pdf)
    pdf.extend(f"4 0 obj\n<< /Length {stream_len} >>\nstream\n".encode("latin1"))
    pdf.extend(stream_data)
    pdf.extend(b"\nendstream\nendobj\n")
    
    # Obj 5: Font
    o5 = len(pdf)
    pdf.extend(b"5 0 obj\n<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>\nendobj\n")
    
    xref_pos = len(pdf)
    pdf.extend(f"xref\n0 6\n0000000000 65535 f \n{o1:010d} 00000 n \n{o2:010d} 00000 n \n{o3:010d} 00000 n \n{o4:010d} 00000 n \n{o5:010d} 00000 n \n".encode("latin1"))
    pdf.extend(f"trailer\n<< /Size 6 /Root 1 0 R >>\nstartxref\n{xref_pos}\n%%EOF\n".encode("latin1"))
    
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    with open(filename, "wb") as f:
        f.write(pdf)
    print(f"Successfully generated {filename} ({len(pdf)} bytes)")

if __name__ == "__main__":
    with open("data/sample_resume.txt", "r", encoding="utf-8") as f:
        create_minimal_pdf("data/sample_resume.pdf", f.read())
