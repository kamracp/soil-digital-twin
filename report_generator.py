from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

def generate_report(data, filename="soil_report.pdf"):

    doc = SimpleDocTemplate(filename)
    styles = getSampleStyleSheet()

    content = []

    content.append(Paragraph("Soil Digital Twin Report", styles["Title"]))
    content.append(Spacer(1, 20))

    content.append(Paragraph(f"Crop: {data['crop']}", styles["Normal"]))
    content.append(Paragraph(f"Moisture: {data['moisture']}%", styles["Normal"]))
    content.append(Paragraph(f"Temperature: {data['temp']} °C", styles["Normal"]))
    content.append(Paragraph(f"pH: {data['ph']}", styles["Normal"]))

    content.append(Spacer(1, 20))

    content.append(Paragraph(f"Irrigation Decision: {data['irrigation']}", styles["Normal"]))
    content.append(Paragraph(f"Energy Insight: {data['energy']}", styles["Normal"]))

    content.append(Spacer(1, 20))

    content.append(Paragraph(f"Base Cost: ₹ {data['base_cost']}", styles["Normal"]))
    content.append(Paragraph(f"Optimized Cost: ₹ {data['opt_cost']}", styles["Normal"]))
    content.append(Paragraph(f"Saving: ₹ {data['saving']}", styles["Normal"]))
    content.append(Paragraph(f"Saving %: {data['saving_percent']}%", styles["Normal"]))

    doc.build(content)

    return filename