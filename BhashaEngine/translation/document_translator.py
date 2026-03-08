import os
import tempfile
from docx import Document
import openpyxl
from pptx import Presentation

class DocumentTranslator:
    def __init__(self, translation_engine):
        self.engine = translation_engine

    def _translate_text(self, text, src_lang, tgt_lang):
        if not text or not text.strip():
            return text
        try:
            return self.engine.translate(text=text, source_lang=src_lang, target_lang=tgt_lang)
        except Exception as e:
            print(f"Failed to translate segment: {text[:30]}... Error: {e}")
            return text

    def _apply_translations(self, operations, src_lang, tgt_lang):
        if not operations:
            return
            
        texts = [op["text"] for op in operations]
        
        # Batch translate via engine for significant speedup
        if hasattr(self.engine, 'translate_batch'):
            # Chunk into reasonable sizes to not overwhelm memory
            batch_size = 16 
            translated_texts = []
            for i in range(0, len(texts), batch_size):
                batch = texts[i:i+batch_size]
                try:
                    translated_batch = self.engine.translate_batch(batch, src_lang, tgt_lang)
                    translated_texts.extend(translated_batch)
                except Exception as e:
                    print(f"Batch translation failed: {e}. Falling back to single.")
                    for text in batch:
                        translated_texts.append(self._translate_text(text, src_lang, tgt_lang))
        else:
            translated_texts = [self._translate_text(t, src_lang, tgt_lang) for t in texts]
            
        for op, translated in zip(operations, translated_texts):
            if translated and translated.strip():
                op["update"](translated)

    def translate_docx(self, file_path, src_lang, tgt_lang):
        """Translates a Word document (.docx)."""
        doc = Document(file_path)
        operations = []
        
        # Translate paragraphs
        for paragraph in doc.paragraphs:
            if paragraph.text.strip():
                def update_p(t, p=paragraph):
                    if p.runs:
                        p.runs[0].text = t
                        for i in range(1, len(p.runs)):
                            p.runs[i].text = ""
                operations.append({
                    "text": paragraph.text,
                    "update": update_p
                })

        # Translate tables
        for table in doc.tables:
            for row in table.rows:
                for cell in row.cells:
                    if cell.text.strip():
                        def update_c(t, c=cell):
                            c.text = t
                        operations.append({
                            "text": cell.text,
                            "update": update_c
                        })
                        
        self._apply_translations(operations, src_lang, tgt_lang)
        
        output_path = os.path.join(tempfile.gettempdir(), f"translated_{os.path.basename(file_path)}")
        doc.save(output_path)
        return output_path

    def translate_xlsx(self, file_path, src_lang, tgt_lang):
        """Translates an Excel document (.xlsx)."""
        workbook = openpyxl.load_workbook(file_path)
        operations = []
        
        for sheet_name in workbook.sheetnames:
            sheet = workbook[sheet_name]
            for row in sheet.iter_rows():
                for cell in row:
                    if cell.value and isinstance(cell.value, str) and cell.value.strip():
                        # Exclude formulas
                        if not cell.value.startswith('='):
                            def update_c(t, c=cell):
                                c.value = t
                            operations.append({
                                "text": cell.value,
                                "update": update_c
                            })
                            
        self._apply_translations(operations, src_lang, tgt_lang)                            
        
        output_path = os.path.join(tempfile.gettempdir(), f"translated_{os.path.basename(file_path)}")
        workbook.save(output_path)
        return output_path

    def translate_pptx(self, file_path, src_lang, tgt_lang):
        """Translates a PowerPoint document (.pptx)."""
        prs = Presentation(file_path)
        operations = []
        
        for slide in prs.slides:
            for shape in slide.shapes:
                if shape.has_text_frame:
                    for paragraph in shape.text_frame.paragraphs:
                        full_text = "".join([run.text for run in paragraph.runs])
                        if full_text.strip():
                            def update_p(t, p=paragraph):
                                if p.runs:
                                    p.runs[0].text = t
                                    for i in range(1, len(p.runs)):
                                        p.runs[i].text = ""
                            operations.append({
                                "text": full_text,
                                "update": update_p
                            })
                
                # Check for tables
                if shape.has_table:
                    for row in shape.table.rows:
                        for cell in row.cells:
                            if cell.text_frame:
                                for paragraph in cell.text_frame.paragraphs:
                                    full_text = "".join([run.text for run in paragraph.runs])
                                    if full_text.strip():
                                        def update_p(t, p=paragraph):
                                            if p.runs:
                                                p.runs[0].text = t
                                                for i in range(1, len(p.runs)):
                                                    p.runs[i].text = ""
                                        operations.append({
                                            "text": full_text,
                                            "update": update_p
                                        })

        self._apply_translations(operations, src_lang, tgt_lang)
        
        output_path = os.path.join(tempfile.gettempdir(), f"translated_{os.path.basename(file_path)}")
        prs.save(output_path)
        return output_path
