from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED
import csv
import html
import os


OUT_DIR = Path("Cell type-wise  Biomarker/results_celltype_sdae_3000hvg_biomarkers")
TABLE_DIR = OUT_DIR / "tables"
FIG_DIR = OUT_DIR / "figures"
PPTX_PATH = OUT_DIR / "Celltype_SDAE_Biomarker_Workflow_Presentation.pptx"

EMU_PER_IN = 914400
SLIDE_W = 13.333333
SLIDE_H = 7.5


def emu(v):
    return int(v * EMU_PER_IN)


def esc(s):
    return html.escape(str(s), quote=True)


def color(hex_color):
    return hex_color.replace("#", "").upper()


class Slide:
    def __init__(self, title=None, subtitle=None):
        self.items = []
        if title:
            self.textbox(0.45, 0.22, 12.45, 0.48, title, 26, "0F172A", bold=True, align="ctr")
        if subtitle:
            self.textbox(0.7, 0.72, 11.95, 0.35, subtitle, 12, "475569", align="ctr")

    def textbox(self, x, y, w, h, text, size=14, fill=None, line=None, font_color="334155",
                bold=False, align="l", radius=False):
        self.items.append(("shape", dict(x=x, y=y, w=w, h=h, text=text, size=size, fill=fill,
                                         line=line, font_color=font_color, bold=bold,
                                         align=align, radius=radius)))

    def box(self, x, y, w, h, title, lines, fill, line, title_color="111827"):
        body = title + "\n" + "\n".join(lines)
        self.textbox(x, y, w, h, body, size=12, fill=fill, line=line, font_color="334155",
                     bold=False, align="ctr", radius=True)

    def line(self, x1, y1, x2, y2, arrow=True, line_color="1F2937"):
        self.items.append(("line", dict(x1=x1, y1=y1, x2=x2, y2=y2, arrow=arrow, line_color=line_color)))

    def image(self, path, x, y, w, h):
        self.items.append(("image", dict(path=Path(path), x=x, y=y, w=w, h=h)))


def paragraphs(text, size, font_color, bold=False, align="l"):
    out = []
    for i, raw in enumerate(str(text).split("\n")):
        ppr = f'<a:pPr algn="{align}"/>' if align else ""
        b = ' b="1"' if (bold and i == 0) else ""
        sz = int(size * 100)
        out.append(
            f'<a:p>{ppr}<a:r><a:rPr lang="en-US" sz="{sz}"{b}>'
            f'<a:solidFill><a:srgbClr val="{color(font_color)}"/></a:solidFill>'
            f'</a:rPr><a:t>{esc(raw)}</a:t></a:r></a:p>'
        )
    return "".join(out)


def shape_xml(idx, item):
    d = item
    fill_xml = ""
    if d["fill"]:
        fill_xml = f'<a:solidFill><a:srgbClr val="{color(d["fill"])}"/></a:solidFill>'
    else:
        fill_xml = '<a:noFill/>'
    if d["line"]:
        line_xml = f'<a:ln w="15000"><a:solidFill><a:srgbClr val="{color(d["line"])}"/></a:solidFill></a:ln>'
    else:
        line_xml = '<a:ln><a:noFill/></a:ln>'
    prst = "roundRect" if d["radius"] else "rect"
    return f"""
    <p:sp>
      <p:nvSpPr><p:cNvPr id="{idx}" name="TextBox {idx}"/><p:cNvSpPr txBox="1"/><p:nvPr/></p:nvSpPr>
      <p:spPr>
        <a:xfrm><a:off x="{emu(d['x'])}" y="{emu(d['y'])}"/><a:ext cx="{emu(d['w'])}" cy="{emu(d['h'])}"/></a:xfrm>
        <a:prstGeom prst="{prst}"><a:avLst/></a:prstGeom>
        {fill_xml}{line_xml}
      </p:spPr>
      <p:txBody><a:bodyPr wrap="square" anchor="mid"><a:spAutoFit/></a:bodyPr><a:lstStyle/>
        {paragraphs(d['text'], d['size'], d['font_color'], d['bold'], d['align'])}
      </p:txBody>
    </p:sp>"""


def line_xml(idx, item):
    x1, y1, x2, y2 = item["x1"], item["y1"], item["x2"], item["y2"]
    x = min(x1, x2)
    y = min(y1, y2)
    w = abs(x2 - x1) or 0.01
    h = abs(y2 - y1) or 0.01
    flip_h = ' flipH="1"' if x2 < x1 else ""
    flip_v = ' flipV="1"' if y2 < y1 else ""
    arrow = '<a:tailEnd type="triangle"/>' if item["arrow"] else ""
    return f"""
    <p:cxnSp>
      <p:nvCxnSpPr><p:cNvPr id="{idx}" name="Arrow {idx}"/><p:cNvCxnSpPr/><p:nvPr/></p:nvCxnSpPr>
      <p:spPr>
        <a:xfrm{flip_h}{flip_v}><a:off x="{emu(x)}" y="{emu(y)}"/><a:ext cx="{emu(w)}" cy="{emu(h)}"/></a:xfrm>
        <a:prstGeom prst="line"><a:avLst/></a:prstGeom>
        <a:ln w="22000"><a:solidFill><a:srgbClr val="{color(item['line_color'])}"/></a:solidFill>{arrow}</a:ln>
      </p:spPr>
    </p:cxnSp>"""


def pic_xml(idx, rid, item):
    return f"""
    <p:pic>
      <p:nvPicPr><p:cNvPr id="{idx}" name="{esc(item['path'].name)}"/><p:cNvPicPr/><p:nvPr/></p:nvPicPr>
      <p:blipFill><a:blip r:embed="{rid}"/><a:stretch><a:fillRect/></a:stretch></p:blipFill>
      <p:spPr><a:xfrm><a:off x="{emu(item['x'])}" y="{emu(item['y'])}"/><a:ext cx="{emu(item['w'])}" cy="{emu(item['h'])}"/></a:xfrm><a:prstGeom prst="rect"><a:avLst/></a:prstGeom></p:spPr>
    </p:pic>"""


def slide_xml(slide, slide_idx):
    parts = []
    rels = ['<Relationship Id="rIdLayout" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slideLayout" Target="../slideLayouts/slideLayout1.xml"/>']
    media = []
    next_id = 2
    pic_num = 1
    for item_type, item in slide.items:
        if item_type == "shape":
            parts.append(shape_xml(next_id, item))
            next_id += 1
        elif item_type == "line":
            parts.append(line_xml(next_id, item))
            next_id += 1
        elif item_type == "image":
            rid = f"rIdImg{pic_num}"
            target = f"../media/{item['path'].name}"
            rels.append(f'<Relationship Id="{rid}" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/image" Target="{esc(target)}"/>')
            parts.append(pic_xml(next_id, rid, item))
            media.append(item["path"])
            next_id += 1
            pic_num += 1
    xml = f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<p:sld xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main"
       xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"
       xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main">
  <p:cSld><p:spTree>
    <p:nvGrpSpPr><p:cNvPr id="1" name=""/><p:cNvGrpSpPr/><p:nvPr/></p:nvGrpSpPr>
    <p:grpSpPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="0" cy="0"/><a:chOff x="0" y="0"/><a:chExt cx="0" cy="0"/></a:xfrm></p:grpSpPr>
    {''.join(parts)}
  </p:spTree></p:cSld>
  <p:clrMapOvr><a:masterClrMapping/></p:clrMapOvr>
</p:sld>"""
    rel_xml = f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
{''.join(rels)}
</Relationships>"""
    return xml, rel_xml, media


def read_csv_dicts(path):
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def build_slides():
    metrics = read_csv_dicts(TABLE_DIR / "ALL_celltype_sdae_test_metrics.csv")
    balance = read_csv_dicts(TABLE_DIR / "selected_celltype_condition_balance_summary.csv")

    slides = []
    s = Slide()
    s.textbox(0.6, 0.65, 12.1, 0.65, "Cell Type-wise SDAE Biomarker Discovery", 32, font_color="0F172A", bold=True, align="ctr")
    s.textbox(1.0, 1.35, 11.3, 0.4, "GSE183276 single-cell kidney data | AKI, CKD, Ref | PT, TAL, IMM, EC, IC, PC, CNT, DCT", 15, font_color="475569", align="ctr")
    s.box(1.2, 2.15, 3.25, 1.25, "Dataset", ["109,741 cells", "37,080 genes", "metadata-driven analysis"], "E0F2FE", "0369A1")
    s.box(5.05, 2.15, 3.25, 1.25, "Model", ["Supervised Denoising Autoencoder", "3000 HVG input", "latent dimension = 32"], "EDE9FE", "6D28D9")
    s.box(8.9, 2.15, 3.25, 1.25, "Output", ["Cell-wise biomarkers", "AKI / CKD / Ref genes", "metrics + plots + tables"], "DCFCE7", "15803D")
    s.textbox(1.0, 4.4, 11.3, 0.8, "Goal: identify condition-specific genes inside each kidney cell type using model importance and expression difference together.", 18, font_color="111827", align="ctr")
    slides.append(s)

    s = Slide("Study Design", "What data entered the pipeline and how labels were selected")
    s.box(0.7, 1.55, 3.4, 1.2, "Condition column", ["condition.l1", "AKI, CKD, Ref"], "E0F2FE", "0369A1")
    s.box(4.95, 1.55, 3.4, 1.2, "Cell type column", ["subclass.l1", "PT, TAL, IMM, EC, IC, PC, CNT, DCT"], "DCFCE7", "15803D")
    s.box(9.2, 1.55, 3.4, 1.2, "Per-cell-type loop", ["Each cell type processed separately", "separate HVGs, model weights, biomarkers"], "FFEDD5", "C2410C")
    s.line(4.1, 2.15, 4.95, 2.15)
    s.line(8.35, 2.15, 9.2, 2.15)
    s.textbox(1.0, 3.45, 11.3, 0.55, "Important interpretation", 20, font_color="0F172A", bold=True, align="ctr")
    s.textbox(1.1, 4.05, 11.1, 1.2, "The architecture is the same for all selected cell types, but the training data, selected HVG set, learned weights, performance metrics, and biomarker genes are different for each cell type.", 18, fill="F1F5F9", line="CBD5E1", font_color="334155", align="ctr", radius=True)
    slides.append(s)

    s = Slide("Parameter Block", "What each group of notebook settings controls")
    boxes = [
        (0.55, 1.25, "Metadata", ["CONDITION_COL", "CELLTYPE_COL"], "E0F2FE", "0369A1"),
        (3.25, 1.25, "Targets", ["TARGET_CLASSES", "TARGET_CELL_TYPES"], "DCFCE7", "15803D"),
        (5.95, 1.25, "Feature + Split", ["N_TOP_HVG = 3000", "TEST_SIZE, VAL_SIZE"], "FFEDD5", "C2410C"),
        (8.65, 1.25, "Training", ["BATCH_SIZE, EPOCHS", "PATIENCE, LR, WD"], "FEF3C7", "B45309"),
        (11.35, 1.25, "Model + Biomarkers", ["NOISE, HIDDEN, LATENT", "TOP_N, MAX_CELLS"], "EDE9FE", "6D28D9"),
    ]
    for x, y, title, lines, fill, ln in boxes:
        s.box(x, y, 2.35, 1.35, title, lines, fill, ln)
    for x in [2.9, 5.6, 8.3, 11.0]:
        s.line(x, 1.93, x + 0.35, 1.93)
    s.box(1.0, 3.4, 3.6, 1.4, "Balancing", ["Use Ref count when possible", "No oversampling replacement", "otherwise use minimum count"], "FEE2E2", "B91C1C")
    s.box(4.9, 3.4, 3.6, 1.4, "Loss", ["Reconstruction weight = 1.0", "Classification weight = 1.5", "condition prediction emphasized"], "EDE9FE", "6D28D9")
    s.box(8.8, 3.4, 3.6, 1.4, "Biomarker output", ["Top 200 genes per class", "Gradient x Input uses up to 400 cells", "ranked by combined score"], "F1F5F9", "475569")
    slides.append(s)

    s = Slide("Total Workflow", "From raw single-cell matrix to final cell type-wise biomarker tables")
    steps = [
        ("Load data", "expression matrix + metadata", "E0F2FE", "0369A1"),
        ("Filter targets", "AKI, CKD, Ref + selected cell types", "DCFCE7", "15803D"),
        ("Balance classes", "equal cells per condition", "FEE2E2", "B91C1C"),
        ("Select HVGs", "top 3000 by variance", "FFEDD5", "C2410C"),
        ("Train SDAE", "denoising + classification", "EDE9FE", "6D28D9"),
        ("Evaluate", "accuracy, F1, confusion matrix, PCA", "FEF3C7", "B45309"),
        ("Rank genes", "Gradient x Input + expression difference", "F1F5F9", "475569"),
    ]
    x = 0.45
    for i, (title, body, fill, ln) in enumerate(steps):
        s.box(x, 2.15, 1.55, 1.25, title, [body], fill, ln)
        if i < len(steps) - 1:
            s.line(x + 1.55, 2.78, x + 1.85, 2.78)
        x += 1.85
    s.textbox(0.75, 4.45, 12.0, 0.9, "The loop repeats for PT, TAL, IMM, EC, IC, PC, CNT, and DCT. Final tables concatenate the top biomarkers from all cell types and classes.", 18, fill="FFFFFF", line="CBD5E1", font_color="334155", align="ctr", radius=True)
    slides.append(s)

    s = Slide("SDAE Architecture", "Same architecture is used for every selected cell type")
    arch = [
        ("Input", "3000 HVG genes", "E0F2FE", "0369A1"),
        ("Noise", "random masking p=0.20", "FEE2E2", "B91C1C"),
        ("Encoder", "3000 -> 512 -> 128 -> 32", "DCFCE7", "15803D"),
        ("Latent", "z = 32", "EDE9FE", "6D28D9"),
        ("Decoder", "32 -> 128 -> 512 -> 3000", "FFEDD5", "C2410C"),
        ("Classifier", "32 -> 64 -> AKI/CKD/Ref", "FEF3C7", "B45309"),
    ]
    x = 0.6
    for i, (title, body, fill, ln) in enumerate(arch):
        s.box(x, 2.0, 1.85, 1.25, title, [body], fill, ln)
        if i < len(arch) - 1:
            s.line(x + 1.85, 2.63, x + 2.15, 2.63)
        x += 2.15
    s.textbox(1.1, 4.25, 11.1, 1.05, "Training objective combines reconstruction and classification: MSE encourages robust representation, CrossEntropy learns disease condition prediction.", 18, fill="F1F5F9", line="CBD5E1", font_color="334155", align="ctr", radius=True)
    slides.append(s)

    s = Slide("Gene Importance Logic", "How biomarkers are scored, not just predicted")
    logic = [
        ("Target class", "AKI or CKD or Ref", "DCFCE7", "15803D"),
        ("Class logit", "use classifier score before softmax", "EDE9FE", "6D28D9"),
        ("Gradient", "d(logit) / d(gene)", "DCFCE7", "15803D"),
        ("Gradient x Input", "importance = sensitivity x expression", "DCFCE7", "15803D"),
        ("Expression direction", "target mean - others mean", "FFEDD5", "C2410C"),
        ("Combined score", "importance x abs(diff)", "FEE2E2", "B91C1C"),
    ]
    x = 0.65
    for i, (title, body, fill, ln) in enumerate(logic):
        s.box(x, 1.85, 1.75, 1.35, title, [body], fill, ln)
        if i < len(logic) - 1:
            s.line(x + 1.75, 2.52, x + 2.05, 2.52)
        x += 2.05
    s.textbox(1.0, 4.3, 11.4, 0.95, "A high-ranked gene is both useful for the trained classifier and strongly different in the target condition compared with the other two conditions.", 18, fill="FFFFFF", line="CBD5E1", font_color="334155", align="ctr", radius=True)
    slides.append(s)

    s = Slide("Balanced Cell Counts", "Cell count used after within-cell-type class balancing")
    x0, y0 = 0.65, 1.35
    headers = ["Cell", "Balanced cells", "Rule"]
    widths = [1.4, 2.0, 3.6]
    for i, h in enumerate(headers):
        s.textbox(x0 + sum(widths[:i]), y0, widths[i], 0.35, h, 12, fill="0F172A", line="0F172A", font_color="FFFFFF", bold=True, align="ctr")
    y = y0 + 0.35
    for row in balance:
        vals = [row["cell_type"], row["balanced_total_cells"], row["balance_reason"]]
        for i, v in enumerate(vals):
            s.textbox(x0 + sum(widths[:i]), y, widths[i], 0.32, v, 10, fill="FFFFFF", line="CBD5E1", font_color="334155", align="ctr")
        y += 0.32
    s.box(8.25, 1.7, 4.2, 2.0, "Why balancing matters", ["Prevents dominant condition from controlling training", "Makes AKI, CKD, Ref comparison fairer", "Avoids replacement oversampling in this setup"], "FEE2E2", "B91C1C")
    slides.append(s)

    s = Slide("Model Performance", "Test performance across cell type-specific SDAE models")
    headers = ["Cell", "Accuracy", "Macro F1", "Best val F1", "Epochs"]
    widths = [1.0, 1.3, 1.3, 1.4, 1.0]
    x0, y0 = 0.7, 1.3
    for i, h in enumerate(headers):
        s.textbox(x0 + sum(widths[:i]), y0, widths[i], 0.35, h, 11, fill="0F172A", line="0F172A", font_color="FFFFFF", bold=True, align="ctr")
    y = y0 + 0.35
    for row in sorted(metrics, key=lambda r: r["cell_type"]):
        vals = [
            row["cell_type"],
            f"{float(row['test_accuracy']):.3f}",
            f"{float(row['test_macro_f1']):.3f}",
            f"{float(row['best_val_macro_f1']):.3f}",
            row["epochs_ran"],
        ]
        for i, v in enumerate(vals):
            s.textbox(x0 + sum(widths[:i]), y, widths[i], 0.32, v, 10, fill="FFFFFF", line="CBD5E1", font_color="334155", align="ctr")
        y += 0.32
    s.box(7.2, 1.45, 5.3, 1.8, "Overall pattern", ["Most cell type-specific models achieved strong macro F1", "PT and CNT were among the highest-performing models", "IMM was comparatively lower but still learned useful signal"], "DCFCE7", "15803D")
    s.box(7.2, 3.7, 5.3, 1.4, "Use in biomarker discovery", ["Performance supports using classifier gradients", "Biomarkers should still be interpreted biologically"], "F1F5F9", "475569")
    slides.append(s)

    s = Slide("Example Output Plots", "Saved figures produced by the notebook")
    imgs = [
        FIG_DIR / "celltype_PT__latent_pca_condition.png",
        FIG_DIR / "celltype_PT__confusion_matrix.png",
        FIG_DIR / "celltype_PT__top20_CKD_biomarkers.png",
    ]
    labels = ["PT latent PCA", "PT confusion matrix", "PT CKD top biomarkers"]
    for i, img in enumerate(imgs):
        x = 0.65 + i * 4.25
        if img.exists():
            s.image(img, x, 1.45, 3.85, 3.0)
        s.textbox(x, 4.62, 3.85, 0.35, labels[i], 13, fill="FFFFFF", line="CBD5E1", font_color="334155", align="ctr", radius=True)
    s.textbox(0.9, 5.5, 11.6, 0.55, "Similar plots are saved for every selected cell type with prefix celltype_<CELLTYPE>__...", 16, fill="F1F5F9", line="CBD5E1", font_color="334155", align="ctr", radius=True)
    slides.append(s)

    s = Slide("Final Biomarker Tables", "How to read the saved results")
    s.box(0.8, 1.45, 3.6, 1.4, "ALL_celltype_top_biomarkers", ["Top ranked genes per cell type", "separate class labels", "AKI, CKD, Ref"], "E0F2FE", "0369A1")
    s.box(4.85, 1.45, 3.6, 1.4, "FINAL_compact_celltype_biomarkers", ["Report-friendly compact table", "gene, class, score, importance", "mean expression columns"], "DCFCE7", "15803D")
    s.box(8.9, 1.45, 3.6, 1.4, "Per-cell files", ["HVG list, metrics, confusion matrix", "latent representation", "trained model weights"], "FFEDD5", "C2410C")
    s.textbox(1.2, 3.75, 10.9, 1.2, "Columns to explain: importance = Gradient x Input model relevance; target_minus_others_mean = expression difference; combined_score = final ranking score combining both.", 18, fill="FFFFFF", line="CBD5E1", font_color="334155", align="ctr", radius=True)
    slides.append(s)

    s = Slide("Take-home Message", "What this workflow contributes")
    s.textbox(1.0, 1.55, 11.3, 0.7, "Cell type-wise modeling avoids mixing biologically different kidney compartments.", 22, fill="E0F2FE", line="0369A1", font_color="0F172A", align="ctr", radius=True)
    s.textbox(1.0, 2.65, 11.3, 0.7, "The SDAE learns robust latent features while also predicting AKI, CKD, and Ref.", 22, fill="EDE9FE", line="6D28D9", font_color="0F172A", align="ctr", radius=True)
    s.textbox(1.0, 3.75, 11.3, 0.7, "Biomarkers are prioritized by both model importance and condition-specific expression shift.", 22, fill="DCFCE7", line="15803D", font_color="0F172A", align="ctr", radius=True)
    s.textbox(1.0, 5.1, 11.3, 0.55, "Result: separate AKI, CKD, and Ref biomarker candidates for PT, TAL, IMM, EC, IC, PC, CNT, and DCT.", 18, font_color="334155", align="ctr")
    slides.append(s)
    return slides


def write_package(slides):
    slide_entries = []
    rel_entries = []
    media_files = {}
    with ZipFile(PPTX_PATH, "w", ZIP_DEFLATED) as z:
        for i, slide in enumerate(slides, start=1):
            sx, rx, media = slide_xml(slide, i)
            z.writestr(f"ppt/slides/slide{i}.xml", sx)
            z.writestr(f"ppt/slides/_rels/slide{i}.xml.rels", rx)
            slide_entries.append(f'<p:sldId id="{255+i}" r:id="rId{i+1}"/>')
            rel_entries.append(f'<Relationship Id="rId{i+1}" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slide" Target="slides/slide{i}.xml"/>')
            for m in media:
                media_files[m.name] = m

        z.writestr("[Content_Types].xml", content_types(len(slides), media_files))
        z.writestr("_rels/.rels", package_rels())
        z.writestr("docProps/core.xml", core_props())
        z.writestr("docProps/app.xml", app_props(len(slides)))
        z.writestr("ppt/presentation.xml", presentation_xml(slide_entries))
        z.writestr("ppt/_rels/presentation.xml.rels", presentation_rels(rel_entries))
        z.writestr("ppt/slideMasters/slideMaster1.xml", slide_master_xml())
        z.writestr("ppt/slideMasters/_rels/slideMaster1.xml.rels", slide_master_rels())
        z.writestr("ppt/slideLayouts/slideLayout1.xml", slide_layout_xml())
        z.writestr("ppt/slideLayouts/_rels/slideLayout1.xml.rels", slide_layout_rels())
        z.writestr("ppt/theme/theme1.xml", theme_xml())
        z.writestr("ppt/viewProps.xml", view_props())
        z.writestr("ppt/presProps.xml", pres_props())
        z.writestr("ppt/tableStyles.xml", table_styles())
        for name, path in media_files.items():
            z.write(path, f"ppt/media/{name}")


def content_types(n_slides, media_files):
    slide_overrides = "\n".join(
        f'<Override PartName="/ppt/slides/slide{i}.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.slide+xml"/>'
        for i in range(1, n_slides + 1)
    )
    return f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
  <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
  <Default Extension="xml" ContentType="application/xml"/>
  <Default Extension="png" ContentType="image/png"/>
  <Override PartName="/ppt/presentation.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.presentation.main+xml"/>
  <Override PartName="/ppt/slideMasters/slideMaster1.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.slideMaster+xml"/>
  <Override PartName="/ppt/slideLayouts/slideLayout1.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.slideLayout+xml"/>
  <Override PartName="/ppt/theme/theme1.xml" ContentType="application/vnd.openxmlformats-officedocument.theme+xml"/>
  <Override PartName="/ppt/presProps.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.presProps+xml"/>
  <Override PartName="/ppt/viewProps.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.viewProps+xml"/>
  <Override PartName="/ppt/tableStyles.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.tableStyles+xml"/>
  <Override PartName="/docProps/core.xml" ContentType="application/vnd.openxmlformats-package.core-properties+xml"/>
  <Override PartName="/docProps/app.xml" ContentType="application/vnd.openxmlformats-officedocument.extended-properties+xml"/>
  {slide_overrides}
</Types>"""


def package_rels():
    return """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="ppt/presentation.xml"/>
  <Relationship Id="rId2" Type="http://schemas.openxmlformats.org/package/2006/relationships/metadata/core-properties" Target="docProps/core.xml"/>
  <Relationship Id="rId3" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/extended-properties" Target="docProps/app.xml"/>
</Relationships>"""


def presentation_xml(slide_entries):
    return f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<p:presentation xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main"
 xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"
 xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main">
  <p:sldMasterIdLst><p:sldMasterId id="2147483648" r:id="rId1"/></p:sldMasterIdLst>
  <p:sldIdLst>{''.join(slide_entries)}</p:sldIdLst>
  <p:sldSz cx="{emu(SLIDE_W)}" cy="{emu(SLIDE_H)}" type="wide"/>
  <p:notesSz cx="6858000" cy="9144000"/>
</p:presentation>"""


def presentation_rels(rel_entries):
    return f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slideMaster" Target="slideMasters/slideMaster1.xml"/>
  {''.join(rel_entries)}
  <Relationship Id="rId999" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/theme" Target="theme/theme1.xml"/>
</Relationships>"""


def slide_master_xml():
    return """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<p:sldMaster xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships" xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main">
<p:cSld><p:spTree><p:nvGrpSpPr><p:cNvPr id="1" name=""/><p:cNvGrpSpPr/><p:nvPr/></p:nvGrpSpPr><p:grpSpPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="0" cy="0"/><a:chOff x="0" y="0"/><a:chExt cx="0" cy="0"/></a:xfrm></p:grpSpPr></p:spTree></p:cSld>
<p:clrMap bg1="lt1" tx1="dk1" bg2="lt2" tx2="dk2" accent1="accent1" accent2="accent2" accent3="accent3" accent4="accent4" accent5="accent5" accent6="accent6" hlink="hlink" folHlink="folHlink"/>
<p:sldLayoutIdLst><p:sldLayoutId id="2147483649" r:id="rId1"/></p:sldLayoutIdLst>
<p:txStyles><p:titleStyle/><p:bodyStyle/><p:otherStyle/></p:txStyles>
</p:sldMaster>"""


def slide_master_rels():
    return """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slideLayout" Target="../slideLayouts/slideLayout1.xml"/>
  <Relationship Id="rId2" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/theme" Target="../theme/theme1.xml"/>
</Relationships>"""


def slide_layout_xml():
    return """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<p:sldLayout xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships" xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main" type="blank" preserve="1">
<p:cSld name="Blank"><p:spTree><p:nvGrpSpPr><p:cNvPr id="1" name=""/><p:cNvGrpSpPr/><p:nvPr/></p:nvGrpSpPr><p:grpSpPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="0" cy="0"/><a:chOff x="0" y="0"/><a:chExt cx="0" cy="0"/></a:xfrm></p:grpSpPr></p:spTree></p:cSld>
<p:clrMapOvr><a:masterClrMapping/></p:clrMapOvr>
</p:sldLayout>"""


def slide_layout_rels():
    return """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slideMaster" Target="../slideMasters/slideMaster1.xml"/>
</Relationships>"""


def theme_xml():
    return """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<a:theme xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" name="Office Theme">
<a:themeElements>
<a:clrScheme name="Office"><a:dk1><a:srgbClr val="000000"/></a:dk1><a:lt1><a:srgbClr val="FFFFFF"/></a:lt1><a:dk2><a:srgbClr val="1F2937"/></a:dk2><a:lt2><a:srgbClr val="F8FAFC"/></a:lt2><a:accent1><a:srgbClr val="0369A1"/></a:accent1><a:accent2><a:srgbClr val="15803D"/></a:accent2><a:accent3><a:srgbClr val="C2410C"/></a:accent3><a:accent4><a:srgbClr val="6D28D9"/></a:accent4><a:accent5><a:srgbClr val="B45309"/></a:accent5><a:accent6><a:srgbClr val="B91C1C"/></a:accent6><a:hlink><a:srgbClr val="0563C1"/></a:hlink><a:folHlink><a:srgbClr val="954F72"/></a:folHlink></a:clrScheme>
<a:fontScheme name="Office"><a:majorFont><a:latin typeface="Arial"/></a:majorFont><a:minorFont><a:latin typeface="Arial"/></a:minorFont></a:fontScheme>
<a:fmtScheme name="Office"><a:fillStyleLst><a:solidFill><a:schemeClr val="phClr"/></a:solidFill></a:fillStyleLst><a:lnStyleLst><a:ln w="9525"><a:solidFill><a:schemeClr val="phClr"/></a:solidFill></a:ln></a:lnStyleLst><a:effectStyleLst><a:effectStyle/></a:effectStyleLst><a:bgFillStyleLst><a:solidFill><a:schemeClr val="phClr"/></a:solidFill></a:bgFillStyleLst></a:fmtScheme>
</a:themeElements><a:objectDefaults/><a:extraClrSchemeLst/></a:theme>"""


def core_props():
    return """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<cp:coreProperties xmlns:cp="http://schemas.openxmlformats.org/package/2006/metadata/core-properties" xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:dcterms="http://purl.org/dc/terms/" xmlns:dcmitype="http://purl.org/dc/dcmitype/" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
<dc:title>Cell Type-wise SDAE Biomarker Workflow</dc:title><dc:creator>Codex</dc:creator><cp:lastModifiedBy>Codex</cp:lastModifiedBy><dcterms:created xsi:type="dcterms:W3CDTF">2026-06-25T00:00:00Z</dcterms:created><dcterms:modified xsi:type="dcterms:W3CDTF">2026-06-25T00:00:00Z</dcterms:modified></cp:coreProperties>"""


def app_props(n):
    return f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Properties xmlns="http://schemas.openxmlformats.org/officeDocument/2006/extended-properties" xmlns:vt="http://schemas.openxmlformats.org/officeDocument/2006/docPropsVTypes">
<Application>Codex</Application><PresentationFormat>On-screen Show (16:9)</PresentationFormat><Slides>{n}</Slides></Properties>"""


def view_props():
    return """<?xml version="1.0" encoding="UTF-8" standalone="yes"?><p:viewPr xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main"><p:normalViewPr/></p:viewPr>"""


def pres_props():
    return """<?xml version="1.0" encoding="UTF-8" standalone="yes"?><p:presentationPr xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main"/>"""


def table_styles():
    return """<?xml version="1.0" encoding="UTF-8" standalone="yes"?><a:tblStyleLst xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" def="{5C22544A-7EE6-4342-B048-85BDC9FD1C3A}"/>"""


if __name__ == "__main__":
    slides = build_slides()
    write_package(slides)
    print(PPTX_PATH)
