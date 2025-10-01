#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Quiz PDF GUI Generator
- Paste a JSON object into the text area
- Click "Generate PDF…" to choose where to save the PDF
- JSON schema expected (keys):
  title: str
  subtitle: str
  questions: list[ { "text": str, "options": {"A": str, "B": str, "C": str, "D": str} } ]
  solution_table: list[ { "number": int, "answer": "A"|"B"|"C"|"D", "explanation": str } ]

Dependencies:
  pip install reportlab

Run:
  python quiz_gui_app.py
"""

import json
import sys
import traceback
from tkinter import Tk, Frame, Button, BOTH, END, LEFT, RIGHT, X, Y, TOP, BOTTOM, messagebox, filedialog
from tkinter.scrolledtext import ScrolledText

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.units import cm

SAMPLE_TEMPLATE = {
    "title": "Networking – Practice Quiz (5 Questions)",
    "subtitle": "Sample: Basic Concepts",
    "questions": [
        {
            "text": "Which OSI layer is responsible for routing?",
            "options": {"A": "Physical", "B": "Network", "C": "Transport", "D": "Application"}
        },
        {
            "text": "Which protocol translates domain names to IP addresses?",
            "options": {"A": "HTTP", "B": "DNS", "C": "FTP", "D": "SSH"}
        },
        {
            "text": "Which device operates primarily at Layer 2 of the OSI model?",
            "options": {"A": "Router", "B": "Switch", "C": "Firewall", "D": "Server"}
        },
        {
            "text": "Which IP version uses 128-bit addresses?",
            "options": {"A": "IPv4", "B": "IPv6", "C": "IPX", "D": "ARP"}
        },
        {
            "text": "Which transport protocol provides reliable, connection‑oriented delivery?",
            "options": {"A": "ICMP", "B": "UDP", "C": "TCP", "D": "ARP"}
        }
    ],
    "solution_table": [
        {"number": 1, "answer": "B", "explanation": "Routing happens at the OSI Network (Layer 3)."},
        {"number": 2, "answer": "B", "explanation": "DNS resolves domain names to IP addresses."},
        {"number": 3, "answer": "B", "explanation": "Switches primarily operate at Layer 2 (Data Link)."},
        {"number": 4, "answer": "B", "explanation": "IPv6 uses 128‑bit addresses."},
        {"number": 5, "answer": "C", "explanation": "TCP is reliable and connection‑oriented."}
    ]
}

def validate_quiz_schema(data: dict):
    """Minimal schema validation; raises ValueError on problems."""
    required_top = ["title", "subtitle", "questions", "solution_table"]
    for k in required_top:
        if k not in data:
            raise ValueError(f"Missing top-level key: {k}")
    if not isinstance(data["questions"], list) or len(data["questions"]) == 0:
        raise ValueError("questions must be a non-empty list")
    for i, q in enumerate(data["questions"], start=1):
        if "text" not in q or "options" not in q:
            raise ValueError(f"Question {i} must have 'text' and 'options'")
        opts = q["options"]
        if not isinstance(opts, dict) or not all(k in opts for k in ("A", "B", "C", "D")):
            raise ValueError(f"Question {i} options must include A, B, C, D")
    if not isinstance(data["solution_table"], list):
        raise ValueError("solution_table must be a list")
    # Optionally ensure solution_table numbers align with question count
    # but allow flexibility if user wants custom numbering.
    return True

def build_pdf(doc_path: str, data: dict):
    """Generate the PDF using ReportLab Platypus."""
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "TitleCentered",
        parent=styles["Title"],
        alignment=TA_CENTER,
        spaceAfter=12
    )
    subtitle_style = ParagraphStyle(
        "SubtitleCentered",
        parent=styles["Normal"],
        alignment=TA_CENTER,
        fontSize=12,
        textColor=colors.grey,
        spaceAfter=24
    )
    h2 = ParagraphStyle(
        "Heading2",
        parent=styles["Heading2"],
        spaceAfter=12
    )
    normal = styles["Normal"]
    question_style = ParagraphStyle(
        "Question",
        parent=styles["BodyText"],
        fontSize=11,
        leading=14,
        spaceBefore=6,
        spaceAfter=6
    )
    option_style = ParagraphStyle(
        "Option",
        parent=styles["BodyText"],
        leftIndent=12,
        fontSize=10.5,
        leading=13
    )

    story = []

    # Title page
    story.append(Spacer(1, 6 * cm))
    story.append(Paragraph(data["title"], title_style))
    story.append(Paragraph(data["subtitle"], subtitle_style))
    story.append(PageBreak())

    # Questions
    story.append(Paragraph("Questions", h2))
    story.append(Spacer(1, 6))

    for idx, q in enumerate(data["questions"], start=1):
        story.append(Paragraph(f"{idx}. {q['text']}", question_style))
        opts = q["options"]
        story.append(Paragraph(f"A) {opts['A']}", option_style))
        story.append(Paragraph(f"B) {opts['B']}", option_style))
        story.append(Paragraph(f"C) {opts['C']}", option_style))
        story.append(Paragraph(f"D) {opts['D']}", option_style))
        story.append(Spacer(1, 4))

    story.append(PageBreak())

    # Solution Table
    story.append(Paragraph("Solution Table", h2))
    table_data = [["#", "Answer", "Explanation"]]
    for row in data.get("solution_table", []):
        num = row.get("number", "")
        ans = row.get("answer", "")
        exp = row.get("explanation", "")
        table_data.append([str(num), str(ans), str(exp)])
    tbl = Table(table_data, colWidths=[1.5 * cm, 2.0 * cm, 13.0 * cm])
    tbl.setStyle(
        TableStyle(
            [
                ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
                ("ALIGN", (0, 0), (-1, 0), "CENTER"),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 6),
                ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                ("FONTSIZE", (0, 0), (-1, -1), 10),
            ]
        )
    )
    story.append(tbl)

    doc = SimpleDocTemplate(
        doc_path,
        pagesize=A4,
        rightMargin=2*cm,
        leftMargin=2*cm,
        topMargin=2*cm,
        bottomMargin=2*cm,
        title=data.get("title", "Quiz")
    )
    doc.build(story)

class App:
    def __init__(self, root: Tk):
        self.root = root
        root.title("Quiz PDF Generator")
        root.geometry("900x600")

        top_frame = Frame(root)
        top_frame.pack(side=TOP, fill=X, padx=8, pady=8)

        btn_paste_sample = Button(top_frame, text="Paste Sample", command=self.paste_sample)
        btn_paste_sample.pack(side=LEFT, padx=4)

        btn_open_json = Button(top_frame, text="Open JSON…", command=self.open_json_file)
        btn_open_json.pack(side=LEFT, padx=4)

        btn_generate_pdf = Button(top_frame, text="Generate PDF…", command=self.generate_pdf)
        btn_generate_pdf.pack(side=RIGHT, padx=4)

        self.text = ScrolledText(root, wrap="word", undo=True, font=("Consolas", 11))
        self.text.pack(side=TOP, fill=BOTH, expand=True, padx=8, pady=(0,8))

        # Load sample JSON at startup
        self.text.delete("1.0", END)
        self.text.insert(END, json.dumps(SAMPLE_TEMPLATE, ensure_ascii=False, indent=2))

    def paste_sample(self):
        self.text.delete("1.0", END)
        self.text.insert(END, json.dumps(SAMPLE_TEMPLATE, ensure_ascii=False, indent=2))

    def open_json_file(self):
        path = filedialog.askopenfilename(
            title="Open JSON file",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        if not path:
            return
        try:
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()
            # Validate it's at least parseable
            _ = json.loads(content)
            self.text.delete("1.0", END)
            self.text.insert(END, content)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open/parse JSON:\n{e}")

    def generate_pdf(self):
        raw = self.text.get("1.0", END).strip()
        if not raw:
            messagebox.showwarning("Empty", "Please paste a JSON object first.")
            return
        try:
            data = json.loads(raw)
            validate_quiz_schema(data)
        except Exception as e:
            messagebox.showerror("Invalid JSON", f"The JSON is invalid or does not match the expected schema:\n\n{e}")
            return

        out_path = filedialog.asksaveasfilename(
            title="Save PDF as…",
            defaultextension=".pdf",
            filetypes=[("PDF files", "*.pdf")]
        )
        if not out_path:
            return

        try:
            build_pdf(out_path, data)
            messagebox.showinfo("Success", f"PDF saved:\n{out_path}")
        except Exception as e:
            tb = traceback.format_exc()
            messagebox.showerror("Error", f"Failed to generate PDF:\n{e}\n\n{tb}")

def main():
    root = Tk()
    App(root)
    root.mainloop()

if __name__ == "__main__":
    main()
