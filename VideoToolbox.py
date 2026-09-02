import sys, os, subprocess, threading
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QPushButton, QLabel, QFileDialog, QCheckBox, QRadioButton, 
                             QGroupBox, QLineEdit, QTextEdit, QTabWidget)
from PyQt5.QtCore import Qt

class QuaklerApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Quakler - By Penelope Rose")
        self.resize(600, 700)
        
        # Apply Apple Glass UI (Vibrancy)
        self.setAttribute(Qt.WA_TranslucentBackground)
        try:
            from BlurWindow.blurWindow import GlobalBlur
            GlobalBlur(self.winId(), Dark=True, QWidget=self)
        except Exception:
            pass # Fallback if library fails
            
        self.setStyleSheet("""
            QMainWindow { background: transparent; }
            QWidget { background: transparent; color: #EEEEEE; font-size: 13px; }
            QPushButton {
                background: rgba(255, 255, 255, 0.1);
                border: 1px solid rgba(255, 255, 255, 0.15);
                border-radius: 6px; padding: 6px 12px; font-weight: bold;
            }
            QPushButton:hover { background: rgba(255, 255, 255, 0.2); }
            QPushButton:pressed { background: rgba(255, 255, 255, 0.05); }
            QPushButton:disabled { color: rgba(255, 255, 255, 0.3); }
            QTabWidget::pane {
                border: 1px solid rgba(255, 255, 255, 0.1);
                background: rgba(0, 0, 0, 0.3); border-radius: 8px;
            }
            QTabBar::tab {
                background: rgba(255, 255, 255, 0.05);
                border: 1px solid rgba(255, 255, 255, 0.1);
                padding: 6px 15px; border-top-left-radius: 6px; border-top-right-radius: 6px;
                margin-right: 2px;
            }
            QTabBar::tab:selected { background: rgba(255, 255, 255, 0.2); border-bottom: none; }
            QLineEdit, QTextEdit {
                background: rgba(0, 0, 0, 0.4); border: 1px solid rgba(255, 255, 255, 0.15);
                border-radius: 5px; padding: 5px; color: white;
            }
            QCheckBox::indicator, QRadioButton::indicator {
                width: 16px; height: 16px;
            }
        """)
        
        self.videos = []
        self.watermark_path = ""
        
        w = QWidget()
        l = QVBoxLayout(w)
        l.setContentsMargins(20, 20, 20, 20)
        self.setCentralWidget(w)
        
        # Files
        l.addWidget(QLabel("<b>1. Files (Batch Supported)</b>"))
        self.btn_vids = QPushButton("Select Videos")
        self.btn_vids.clicked.connect(self.sel_vids)
        l.addWidget(self.btn_vids)
        
        self.lbl_vids = QLabel("0 videos selected")
        self.lbl_vids.setStyleSheet("color: #AAAAAA;")
        l.addWidget(self.lbl_vids)
        
        self.btn_wm = QPushButton("Select Watermark (.png)")
        self.btn_wm.clicked.connect(self.sel_wm)
        l.addWidget(self.btn_wm)
        
        # Tabs
        tabs = QTabWidget()
        l.addWidget(tabs)
        
        t1 = QWidget()
        l1 = QVBoxLayout(t1)
        tabs.addTab(t1, "Video Options")
        
        self.rad_h264 = QRadioButton("H.264 (Compatible)")
        self.rad_h264.setChecked(True)
        self.rad_hevc = QRadioButton("H.265 (HEVC)")
        l1.addWidget(self.rad_h264)
        l1.addWidget(self.rad_hevc)
        
        self.chk_hw = QCheckBox("Use Apple Silicon Hardware Acceleration (Blazing Fast)")
        self.chk_hw.setChecked(True)
        l1.addWidget(self.chk_hw)
        
        hl = QHBoxLayout()
        hl.addWidget(QLabel("Trim Start:"))
        self.ent_s = QLineEdit()
        hl.addWidget(self.ent_s)
        hl.addWidget(QLabel("End:"))
        self.ent_e = QLineEdit()
        hl.addWidget(self.ent_e)
        l1.addLayout(hl)
        
        self.chk_crop = QCheckBox("Crop to Vertical (9:16)")
        l1.addWidget(self.chk_crop)
        
        self.chk_trans = QCheckBox("Transcribe & Create Subtitles (AI)")
        l1.addWidget(self.chk_trans)
        
        self.chk_burn = QCheckBox("Hard-Burn Subtitles to Video")
        l1.addWidget(self.chk_burn)
        l1.addStretch()
        
        # Tab 2
        t2 = QWidget()
        l2 = QVBoxLayout(t2)
        tabs.addTab(t2, "Audio & Extras")
        
        self.chk_norm = QCheckBox("Normalize Audio (Broadcast Levels)")
        self.chk_denoise = QCheckBox("Clean Voice (Remove Background Noise)")
        self.chk_silence = QCheckBox("Auto-Remove Silence (Jump Cuts)")
        self.chk_mute = QCheckBox("Mute All Audio (B-Roll mode)")
        self.chk_audio = QCheckBox("Extract Audio Only (.mp3)")
        self.chk_thumb = QCheckBox("Extract Thumbnail (1s mark)")
        self.chk_safe = QCheckBox("Generate Social Media Safe-Zone Preview Image")
        self.chk_gif = QCheckBox("Create GIF clip")
        
        for c in (self.chk_norm, self.chk_denoise, self.chk_silence, self.chk_mute, 
                  self.chk_audio, self.chk_thumb, self.chk_safe, self.chk_gif):
            l2.addWidget(c)
        l2.addStretch()
        
        self.btn_run = QPushButton("Start Processing")
        self.btn_run.setStyleSheet("background: rgba(0, 150, 255, 0.4); border: 1px solid rgba(0, 150, 255, 0.8);")
        self.btn_run.clicked.connect(self.run)
        l.addWidget(self.btn_run)
        
        self.log_txt = QTextEdit()
        self.log_txt.setReadOnly(True)
        l.addWidget(self.log_txt)
        
        copy = QLabel("<i>© 2026 Penelope Rose. Proprietary License. All rights reserved.</i>")
        copy.setStyleSheet("color: #888888; font-size: 11px;")
        copy.setAlignment(Qt.AlignCenter)
        l.addWidget(copy)

    def sel_vids(self):
        fs, _ = QFileDialog.getOpenFileNames(self, "Select Videos")
        if fs:
            self.videos = fs
            self.lbl_vids.setText(f"{len(fs)} videos selected")

    def sel_wm(self):
        f, _ = QFileDialog.getOpenFileName(self, "Select Watermark", "", "Images (*.png)")
        if f: self.watermark_path = f

    def log(self, msg):
        self.log_txt.append(msg)
        QApplication.processEvents()

    def run(self):
        if not self.videos: return
        self.btn_run.setEnabled(False)
        threading.Thread(target=self.process, daemon=True).start()

    def process(self):
        try:
            for vid in self.videos:
                self.log(f"\nProcessing: {os.path.basename(vid)}")
                base, _ = os.path.splitext(vid)
                out = base + "_quakler"
                
                srt = None
                if self.chk_trans.isChecked() or self.chk_burn.isChecked():
                    self.log("AI Transcribing...")
                    subprocess.run(["/Users/penelope/homebrew/bin/whisper", vid, "--model", "tiny.en", "--output_dir", os.path.dirname(vid), "--output_format", "srt"], check=True)
                    srt = base + ".srt"
                
                if self.chk_audio.isChecked():
                    subprocess.run(["/Users/penelope/homebrew/bin/ffmpeg", "-y", "-i", vid, "-q:a", "0", "-map", "a", out+".mp3"])
                    continue
                
                cmd = ["/Users/penelope/homebrew/bin/ffmpeg", "-y", "-i", vid]
                if self.watermark_path: cmd.extend(["-i", self.watermark_path])
                
                if self.ent_s.text(): cmd.extend(["-ss", self.ent_s.text()])
                if self.ent_e.text(): cmd.extend(["-to", self.ent_e.text()])
                
                vf, af = [], []
                
                if self.chk_crop.isChecked(): vf.append("crop=ih*(9/16):ih")
                if self.watermark_path: vf.append("overlay=W-w-10:H-h-10")
                if self.chk_burn.isChecked() and srt: vf.append(f"subtitles='{srt.replace(':', '\\:')}'")
                
                if self.chk_mute.isChecked(): cmd.append("-an")
                else:
                    if self.chk_norm.isChecked(): af.append("loudnorm=I=-16:TP=-1.5:LRA=11")
                    if self.chk_denoise.isChecked(): af.append("afftdn")
                    if self.chk_silence.isChecked(): af.append("silenceremove=stop_periods=-1:stop_duration=0.5:stop_threshold=-30dB")
                
                if vf: cmd.extend(["-vf", ",".join(vf)])
                if af: cmd.extend(["-af", ",".join(af)])
                
                if self.chk_hw.isChecked():
                    c = "h264_videotoolbox" if self.rad_h264.isChecked() else "hevc_videotoolbox"
                    cmd.extend(["-c:v", c, "-q:v", "55"])  # Adaptive bitrate for VideoToolbox
                else:
                    c = "libx264" if self.rad_h264.isChecked() else "libx265"
                    cmd.extend(["-c:v", c, "-crf", "28"])  # Adaptive Constant Rate Factor
                    
                cmd.extend(["-movflags", "+faststart", out+".mp4"])
                self.log("Rendering Video...")
                subprocess.run(cmd, check=True)
                
                if self.chk_thumb.isChecked():
                    subprocess.run(["/Users/penelope/homebrew/bin/ffmpeg", "-y", "-ss", "00:00:01", "-i", out+".mp4", "-vframes", "1", out+"_thumb.jpg"])
                
                if self.chk_gif.isChecked():
                    subprocess.run(["/Users/penelope/homebrew/bin/ffmpeg", "-y", "-i", out+".mp4", "-vf", "fps=10,scale=320:-1:flags=lanczos,split[s0][s1];[s0]palettegen[p];[s1][p]paletteuse", out+".gif"])
                
                if self.chk_safe.isChecked():
                    subprocess.run(["/Users/penelope/homebrew/bin/ffmpeg", "-y", "-i", out+".mp4", "-vframes", "1", "-vf", "drawbox=x=0:y=ih*0.75:w=iw:h=ih*0.25:color=red@0.5:t=fill,drawbox=x=iw*0.8:y=ih*0.4:w=iw*0.2:h=ih*0.4:color=red@0.5:t=fill", out+"_safezone.jpg"])
                    
        except Exception as e:
            self.log(f"Error: {e}")
        finally:
            self.log("Done!")
            self.btn_run.setEnabled(True)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = QuaklerApp()
    ex.show()
    sys.exit(app.exec_())

