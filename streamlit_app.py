
import io
from datetime import datetime
import streamlit as st

try:
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.units import mm
    from reportlab.pdfgen import canvas
    from reportlab.lib import colors
    from reportlab.platypus import Table, TableStyle
except Exception:
    st.error("reportlab is required for PDF generation. Install with: pip install reportlab")
    raise

st.set_page_config(page_title="Fablaundry", layout="wide")

# ---------- Dark CSS ----------
st.markdown(
    """
    <style>
    /* Strong black background, white primary text */
    .stApp {
        background-color: #000000;
        color: #FFFFFF;
        font-family: Inter, ui-sans-serif, system-ui, -apple-system, "Segoe UI", Roboto, "Helvetica Neue", Arial;
    }

    /* Header */
    .header {
        background: linear-gradient(90deg,#0f172a,#0b1220);
        color: #ffffff;
        padding: 18px 22px;
        border-radius: 10px;
        box-shadow: 0 6px 18px rgba(0,0,0,0.7);
        margin-bottom: 16px;
    }
    .header h1 { margin: 0; font-size: 26px; }
    .header p { margin: 0; color: rgba(255,255,255,0.85); font-size: 13px; }

    /* Card with dark gray */
    .card {
        background: #0b1220;
        border-radius: 10px;
        padding: 16px;
        box-shadow: 0 8px 30px rgba(0,0,0,0.7);
        border: 1px solid rgba(255,255,255,0.04);
    }
    .accent-band {
        height: 6px;
        border-radius: 6px;
        background: linear-gradient(90deg,#06b6d4,#7c3aed);
        margin-bottom: 12px;
    }

    /* Buttons */
    .primary-btn > button {
        background: linear-gradient(90deg,#06b6d4,#7c3aed);
        color: #000;
        border: none;
        padding: 10px 16px;
        border-radius: 10px;
        font-weight: 700;
    }
    .secondary-btn > button {
        background: transparent;
        border: 1px solid rgba(255,255,255,0.08);
        color: #fff;
        padding: 8px 12px;
        border-radius: 8px;
    }

    /* Force inputs to dark background & white text (Streamlit structure may vary by version) */
    .stTextInput>div>div>input, .stNumberInput>div>div>input, .stTextArea>div>div>textarea, .stSelectbox>div>div>select {
        background-color: #0b1220 !important;
        color: #ffffff !important;
        border: 1px solid rgba(255,255,255,0.06) !important;
        padding: 8px 10px !important;
        border-radius: 8px !important;
    }

    /* Selectbox label and input label colors */
    .stTextInput>div>label, .stNumberInput>div>label, .stSelectbox>div>label, .stTextArea>div>label {
        color: #e6eef8;
        font-weight: 700;
    }

    /* Small muted text (lighter) */
    .muted { color: rgba(255,255,255,0.6); font-size: 13px; }

    /* Table preview styling */
    .stTable thead tr th { color: #e6eef8 !important; }
    .stTable tbody tr td { color: #dbeafe !important; }

    /* Footer spacing */
    .footer { padding-top: 12px; color: rgba(255,255,255,0.6); }
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------- Session state ----------
if "rows" not in st.session_state:
    st.session_state.rows = [{"description": "Service / Item", "qty": 1, "unit_price": 0.0}]
if "invoice_no" not in st.session_state:
    st.session_state.invoice_no = f"INV-{datetime.now().strftime('%Y%m%d%H%M%S')}"
if "logo_bytes" not in st.session_state:
    st.session_state.logo_bytes = None

# ---------- Header ----------
st.markdown(
    f"""
    <div class="header">
      <div style="display:flex;justify-content:space-between;align-items:center">
        <div>
          <h1>Fablaundry — Email:info@fablaundry.in</h1>
          <p class="muted">Customer Satisfaction · Trusted · Indian</p>
        </div>
        <div style="text-align:right">
          <div class="muted">Ready • {datetime.now().strftime('%b %d, %Y')}</div>
        </div>
      </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# ---------- Sidebar ----------
with st.sidebar:
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.subheader("Help (Dark)")
    st.markdown(
        """
        - GST options: 0%, 5%, 18%, 40%  
        - Discount applied before GST (taxable = subtotal - discount)  
        - Upload a logo to appear in the PDF  
        - Click Generate & Download to create the PDF
        """)
    st.markdown("</div>", unsafe_allow_html=True)

# ---------- Layout ----------
left, right = st.columns([2, 1])

with left:
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.markdown("<div class='accent-band'></div>", unsafe_allow_html=True)
    col1, col2 = st.columns([3, 2])
    with col1:
        company_name = st.text_input("Company name", "")
        company_email = st.text_input("Company email", "")
        company_phone = st.text_input("Company phone", "")
        company_address = st.text_area("Company address", value="")
    with col2:
        uploaded_logo = st.file_uploader("Upload logo (optional, PNG/JPG)", type=["png", "jpg", "jpeg"])
        if uploaded_logo is not None:
            st.session_state.logo_bytes = uploaded_logo.getvalue()
            st.image(st.session_state.logo_bytes, width=140)
        project_name = st.text_input("Project / Service name", "Annual Maintenance + Website (Python backend)")
        contact_person = st.text_input("Contact person", "")
        invoice_no = st.text_input("Invoice number", st.session_state.invoice_no)
        date = st.date_input("Invoice date", datetime.today())
    st.markdown("</div>", unsafe_allow_html=True)

    # Tax & discount
    st.markdown("<div style='margin-top:12px' class='card'>", unsafe_allow_html=True)
    st.markdown("<div class='accent-band'></div>", unsafe_allow_html=True)
    st.subheader("Tax & Discount")
    g1, g2, g3 = st.columns([1,1,1])
    with g1:
        gst_choice = st.selectbox("GST Rate", options=[0,5,18,40], index=2)
    with g2:
        discount_mode = st.selectbox("Discount type", options=["No discount", "Percentage (%)", "Fixed amount (₹)"])
    with g3:
        split_gst = st.checkbox("Split GST (CGST/SGST)", value=True)

    if discount_mode == "Percentage (%)":
        discount_pct = st.slider("Discount %", 0.0, 100.0, 0.0, step=0.5)
        discount_fixed = 0.0
    elif discount_mode == "Fixed amount (₹)":
        discount_fixed = st.number_input("Discount amount (₹)", min_value=0.0, value=0.0, step=1.0, format="%.2f")
        discount_pct = 0.0
    else:
        discount_pct = 0.0
        discount_fixed = 0.0
    st.markdown("</div>", unsafe_allow_html=True)

    # Items
    st.markdown("<div style='margin-top:12px' class='card'>", unsafe_allow_html=True)
    st.markdown("<div class='accent-band'></div>", unsafe_allow_html=True)
    st.subheader("Items / Services")
    remove_idx = None
    for i, row in enumerate(st.session_state.rows):
        st.markdown(f"<div style='margin-bottom:10px'>", unsafe_allow_html=True)
        rcols = st.columns([6,1,2,1])
        with rcols[0]:
            st.session_state.rows[i]["description"] = st.text_input(f"Description #{i+1}", value=row.get("description",""), key=f"desc_{i}")
        with rcols[1]:
            st.session_state.rows[i]["qty"] = st.number_input(f"Qty #{i+1}", min_value=0.0, value=float(row.get("qty",1.0)), step=1.0, format="%.0f", key=f"qty_{i}")
        with rcols[2]:
            st.session_state.rows[i]["unit_price"] = st.number_input(f"Unit price #{i+1}", min_value=0.0, value=float(row.get("unit_price",0.0)), format="%.2f", key=f"up_{i}")
        with rcols[3]:
            if st.button("Remove", key=f"remove_{i}"):
                remove_idx = i
        st.markdown("</div>", unsafe_allow_html=True)
    if remove_idx is not None:
        st.session_state.rows.pop(remove_idx)
    if st.button("➕ Add row", key="add_row"):
        st.session_state.rows.append({"description": "", "qty": 1, "unit_price": 0.0})
    st.markdown("</div>", unsafe_allow_html=True)

with right:
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.markdown("<div class='accent-band'></div>", unsafe_allow_html=True)
    st.subheader("Summary")
    def compute_totals(rows, gst, disc_pct, disc_fixed):
        lines = []
        subtotal = 0.0
        for r in rows:
            qty = float(r.get("qty",0) or 0.0)
            up = float(r.get("unit_price",0) or 0.0)
            total_line = qty * up
            lines.append({"description": r.get("description",""), "qty": qty, "unit_price": up, "total": total_line})
            subtotal += total_line
        # discount
        discount_amount = 0.0
        if disc_pct:
            discount_amount = subtotal * (disc_pct / 100.0)
        elif disc_fixed:
            discount_amount = float(disc_fixed)
        taxable = max(subtotal - discount_amount, 0.0)
        gst_amount = taxable * (gst / 100.0)
        grand = taxable + gst_amount
        return lines, round(subtotal,2), round(discount_amount,2), round(taxable,2), round(gst_amount,2), round(grand,2)

    lines, subtotal, discount_amount, taxable_value, gst_amount, grand_total = compute_totals(st.session_state.rows, gst_choice, discount_pct, discount_fixed)

    st.metric("Subtotal (₹)", f"{subtotal:,.2f}")
    st.metric("Discount (₹)", f"{discount_amount:,.2f}")
    st.metric("Taxable Value (₹)", f"{taxable_value:,.2f}")
    if split_gst:
        half = gst_amount / 2.0
        st.write(f"GST ({gst_choice}%) = ₹ {gst_amount:.2f} → CGST ₹ {half:.2f} + SGST ₹ {half:.2f}")
    else:
        st.write(f"GST ({gst_choice}%) = ₹ {gst_amount:.2f}")
    st.markdown(f"### **Total: ₹ {grand_total:,.2f}**")
    st.markdown("</div>", unsafe_allow_html=True)

    # small preview
    st.markdown("<div style='margin-top:12px' class='card'>", unsafe_allow_html=True)
    st.subheader("Preview (small)")
    preview = []
    for it in lines:
        preview.append([it["description"] or "-", int(it["qty"]) if float(it["qty"]).is_integer() else it["qty"], f"{it['unit_price']:.2f}", f"{it['total']:.2f}"])
    st.table(preview)
    st.markdown("</div>", unsafe_allow_html=True)

# ---------- PDF generator ----------
def generate_pdf(company_info, invoice_meta, lines, subtotal, discount_amount, taxable, gst_amount, total, split_gst, logo_bytes):
    buf = io.BytesIO()
    PAGE_W, PAGE_H = A4
    c = canvas.Canvas(buf, pagesize=A4)
    margin = 15 * mm
    x = margin
    y = PAGE_H - margin

    # Logo
    if logo_bytes:
        try:
            from reportlab.lib.utils import ImageReader
            img = ImageReader(io.BytesIO(logo_bytes))
            iw, ih = img.getSize()
            max_w = 60 * mm
            scale = min(1.0, max_w / iw)
            w = iw * scale
            h = ih * scale
            c.drawImage(img, x, y - h, width=w, height=h, preserveAspectRatio=True, mask='auto')
            logo_h = h + 4*mm
        except Exception:
            logo_h = 0
    else:
        logo_h = 0

    # Header text
    c.setFont("Helvetica-Bold", 16)
    c.setFillColor(colors.black)  # PDF body remains standard dark-on-light for printing
    c.drawString(x + (logo_h and (logo_h + 6*mm) or 0), y - (logo_h and (logo_h/2) or 0), company_info.get("name",""))
    c.setFont("Helvetica", 9)
    y -= max(logo_h, 14*mm)
    for line in company_info.get("address","").splitlines():
        c.drawString(x, y, line)
        y -= 4 * mm
    if company_info.get("email"):
        c.drawString(x, y, f"Email: {company_info.get('email')}")
        y -= 4 * mm
    if company_info.get("phone"):
        c.drawString(x, y, f"Phone: {company_info.get('phone')}")
        y -= 6 * mm

    # Meta block right
    meta_x = PAGE_W - margin - 80*mm
    meta_y = PAGE_H - margin
    c.setFont("Helvetica-Bold", 12)
    c.drawString(meta_x, meta_y, "Invoice")
    c.setFont("Helvetica", 9)
    meta_y -= 5 * mm
    c.drawString(meta_x, meta_y, f"Invoice #: {invoice_meta.get('no')}")
    meta_y -= 4 * mm
    c.drawString(meta_x, meta_y, f"Date: {invoice_meta.get('date').strftime('%Y-%m-%d')}")
    meta_y -= 4 * mm
    c.drawString(meta_x, meta_y, f"Project: {invoice_meta.get('project','')}")

    # Table rows
    y -= 10 * mm
    table_data = [["Description","Qty","Unit Price (₹)","Total (₹)"]]
    for it in lines:
        table_data.append([
            it["description"] or "-",
            str(int(it["qty"])) if float(it["qty"]).is_integer() else f"{it['qty']}",
            f"{it['unit_price']:.2f}",
            f"{it['total']:.2f}",
        ])
    table_data.append(["","","Subtotal (₹)", f"{subtotal:.2f}"])
    table_data.append(["","","Discount (₹)", f"-{discount_amount:.2f}"])
    table_data.append(["","","Taxable Value (₹)", f"{taxable:.2f}"])
    if split_gst:
        half = gst_amount / 2.0
        table_data.append(["","","CGST (%)", f"{half:.2f}"])
        table_data.append(["","","SGST (%)", f"{half:.2f}"])
    else:
        table_data.append(["","","GST (%)", f"{gst_amount:.2f}"])
    table_data.append(["","","Total (₹)", f"{total:.2f}"])

    table = Table(table_data, colWidths=[90*mm, 20*mm, 30*mm, 30*mm])
    style = TableStyle([
        ("GRID", (0,0), (-1,-1), 0.4, colors.HexColor("#e6eef8")),
        ("BACKGROUND", (0,0), (-1,0), colors.HexColor("#f0f7ff")),
        ("FONT", (0,0), (-1,0), "Helvetica-Bold"),
        ("ALIGN", (1,1), (-1,-1), "RIGHT"),
        ("BOTTOMPADDING", (0,0), (-1,0), 6),
    ])
    end = len(table_data) - 1
    style.add("FONT", (2,end), (3,end), "Helvetica-Bold")
    table.setStyle(style)
    tw, th = table.wrapOn(c, PAGE_W - 2*margin, PAGE_H)
    table.drawOn(c, x, y - th)

    # Footer
    footer_y = 22 * mm
    c.setFont("Helvetica", 9)
    c.drawString(x, footer_y, "Thank you for your business.")
    c.drawRightString(PAGE_W - margin, footer_y, "Authorized signatory")

    c.showPage()
    c.save()
    buf.seek(0)
    return buf.getvalue()

# ---------- Generate & Download ----------
cta_col, help_col = st.columns([1,1])
with cta_col:
    if st.button("Generate & Download PDF", key="gen_dark"):
        with st.spinner("Generating PDF..."):
            invoice_meta = {"no": invoice_no, "date": date, "project": project_name, "gst": float(gst_choice)}
            company_info = {"name": company_name, "email": company_email, "phone": company_phone, "address": company_address}
            pdf = generate_pdf(company_info, invoice_meta, lines, subtotal, discount_amount, taxable_value, gst_amount, grand_total, split_gst, st.session_state.logo_bytes)
            st.success("PDF ready")
            st.download_button("📥 Download PDF", data=pdf, file_name=f"{invoice_meta['no']}.pdf", mime="application/pdf")
with help_col:
    st.markdown("<div class='muted' style='text-align:right'>Tip: use high-contrast logos (light) for best PDF look.</div>", unsafe_allow_html=True)

st.markdown("<div class='footer muted'>S.L.H Laboratory Pvt. Ltd • Made with Love • By Laraib</div>", unsafe_allow_html=True)
