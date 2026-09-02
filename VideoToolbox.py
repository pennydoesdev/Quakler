import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import subprocess, os, threading

class QuaklerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Quakler - By Penelope Rose")
        self.root.geometry("600x650")
        self.root.resizable(False, False)
        
        self.videos = []
        self.watermark = tk.StringVar()
        self.codec = tk.StringVar(value="h264")
        self.trim_s = tk.StringVar()
        self.trim_e = tk.StringVar()
        
        self.opts = {
            'crop916': tk.BooleanVar(),
            'hwaccel': tk.BooleanVar(value=True),
            'denoise': tk.BooleanVar(),
            'silence': tk.BooleanVar(),
            'norm': tk.BooleanVar(),
            'mute': tk.BooleanVar(),
            'audio_only': tk.BooleanVar(),
            'transcribe': tk.BooleanVar(),
            'burn_subs': tk.BooleanVar(),
            'thumb': tk.BooleanVar(),
            'safe_zone': tk.BooleanVar(),
            'gif': tk.BooleanVar()
        }
        
        self.setup_ui()

    def setup_ui(self):
        f = ttk.Frame(self.root, padding=15)
        f.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(f, text="1. Files (Batch Supported)", font=("", 12, "bold")).pack(anchor=tk.W)
        ttk.Button(f, text="Select Videos", command=self.sel_vids).pack(fill=tk.X, pady=2)
        self.vid_lbl = ttk.Label(f, text="0 videos selected", foreground="gray")
        self.vid_lbl.pack(anchor=tk.W)
        
        ttk.Button(f, text="Select Watermark (.png)", command=lambda: self.watermark.set(filedialog.askopenfilename())).pack(fill=tk.X, pady=2)
        
        nb = ttk.Notebook(f)
        nb.pack(fill=tk.BOTH, expand=True, pady=10)
        
        t1 = ttk.Frame(nb, padding=10)
        t2 = ttk.Frame(nb, padding=10)
        nb.add(t1, text="Video Options")
        nb.add(t2, text="Audio & Extras")
        
        # Tab 1
        ttk.Radiobutton(t1, text="H.264 (Compatible)", variable=self.codec, value="h264").pack(anchor=tk.W)
        ttk.Radiobutton(t1, text="H.265 (HEVC)", variable=self.codec, value="hevc").pack(anchor=tk.W)
        ttk.Checkbutton(t1, text="Use Apple Silicon Hardware Acceleration (Blazing Fast)", variable=self.opts['hwaccel']).pack(anchor=tk.W, pady=5)
        
        tf = ttk.Frame(t1)
        tf.pack(anchor=tk.W, pady=5)
        ttk.Label(tf, text="Trim Start:").pack(side=tk.LEFT)
        ttk.Entry(tf, textvariable=self.trim_s, width=8).pack(side=tk.LEFT, padx=5)
        ttk.Label(tf, text="End:").pack(side=tk.LEFT)
        ttk.Entry(tf, textvariable=self.trim_e, width=8).pack(side=tk.LEFT, padx=5)
        
        ttk.Checkbutton(t1, text="Crop to Vertical (9:16)", variable=self.opts['crop916']).pack(anchor=tk.W)
        ttk.Checkbutton(t1, text="Transcribe & Create Subtitles (AI)", variable=self.opts['transcribe']).pack(anchor=tk.W)
        ttk.Checkbutton(t1, text="Hard-Burn Subtitles to Video", variable=self.opts['burn_subs']).pack(anchor=tk.W)
        
        # Tab 2
        ttk.Checkbutton(t2, text="Normalize Audio (Broadcast Levels)", variable=self.opts['norm']).pack(anchor=tk.W)
        ttk.Checkbutton(t2, text="Clean Voice (Remove Background Noise)", variable=self.opts['denoise']).pack(anchor=tk.W)
        ttk.Checkbutton(t2, text="Auto-Remove Silence (Jump Cuts)", variable=self.opts['silence']).pack(anchor=tk.W)
        ttk.Checkbutton(t2, text="Mute All Audio (B-Roll mode)", variable=self.opts['mute']).pack(anchor=tk.W)
        ttk.Separator(t2, orient='horizontal').pack(fill=tk.X, pady=5)
        ttk.Checkbutton(t2, text="Extract Audio Only (.mp3)", variable=self.opts['audio_only']).pack(anchor=tk.W)
        ttk.Checkbutton(t2, text="Extract Thumbnail (1s mark)", variable=self.opts['thumb']).pack(anchor=tk.W)
        ttk.Checkbutton(t2, text="Generate Social Media Safe-Zone Preview Image", variable=self.opts['safe_zone']).pack(anchor=tk.W)
        ttk.Checkbutton(t2, text="Create GIF clip", variable=self.opts['gif']).pack(anchor=tk.W)
        
        self.btn = ttk.Button(f, text="Start Processing", command=self.run)
        self.btn.pack(fill=tk.X, pady=5)
        
        self.log_txt = tk.Text(f, height=6, state='disabled')
        self.log_txt.pack(fill=tk.BOTH, expand=True)
        ttk.Label(f, text="© 2026 Penelope Rose. Proprietary License. All rights reserved.", font=("", 10, "italic"), foreground="gray").pack(pady=2)

    def sel_vids(self):
        fs = filedialog.askopenfilenames()
        if fs:
            self.videos = list(fs)
            self.vid_lbl.config(text=f"{len(self.videos)} videos selected")

    def log(self, msg):
        self.log_txt.config(state='normal')
        self.log_txt.insert(tk.END, msg + "\n")
        self.log_txt.see(tk.END)
        self.log_txt.config(state='disabled')
        self.root.update()

    def run(self):
        if not self.videos: return
        self.btn.config(state='disabled')
        threading.Thread(target=self.process, daemon=True).start()

    def process(self):
        try:
            for vid in self.videos:
                self.log(f"\nProcessing: {os.path.basename(vid)}")
                base, _ = os.path.splitext(vid)
                out = base + "_quakler"
                
                srt = None
                if self.opts['transcribe'].get() or self.opts['burn_subs'].get():
                    self.log("AI Transcribing...")
                    subprocess.run(["/Users/penelope/homebrew/bin/whisper", vid, "--model", "tiny.en", "--output_dir", os.path.dirname(vid), "--output_format", "srt"], check=True)
                    srt = base + ".srt"
                
                if self.opts['audio_only'].get():
                    subprocess.run(["/Users/penelope/homebrew/bin/ffmpeg", "-y", "-i", vid, "-q:a", "0", "-map", "a", out+".mp3"])
                    continue
                
                cmd = ["/Users/penelope/homebrew/bin/ffmpeg", "-y", "-i", vid]
                if self.watermark.get(): cmd.extend(["-i", self.watermark.get()])
                
                if self.trim_s.get(): cmd.extend(["-ss", self.trim_s.get()])
                if self.trim_e.get(): cmd.extend(["-to", self.trim_e.get()])
                
                vf, af = [], []
                
                if self.opts['crop916'].get(): vf.append("crop=ih*(9/16):ih")
                if self.watermark.get(): vf.append("overlay=W-w-10:H-h-10")
                if self.opts['burn_subs'].get() and srt: vf.append(f"subtitles='{srt.replace(':', '\\:')}'")
                
                if self.opts['mute'].get(): cmd.append("-an")
                else:
                    if self.opts['norm'].get(): af.append("loudnorm=I=-16:TP=-1.5:LRA=11")
                    if self.opts['denoise'].get(): af.append("afftdn")
                    if self.opts['silence'].get(): af.append("silenceremove=stop_periods=-1:stop_duration=0.5:stop_threshold=-30dB")
                
                if vf: cmd.extend(["-vf", ",".join(vf)])
                if af: cmd.extend(["-af", ",".join(af)])
                
                if self.opts['hwaccel'].get():
                    c = "h264_videotoolbox" if self.codec.get() == "h264" else "hevc_videotoolbox"
                    cmd.extend(["-c:v", c, "-b:v", "5000k"])
                else:
                    c = "libx264" if self.codec.get() == "h264" else "libx265"
                    cmd.extend(["-c:v", c])
                    
                cmd.extend(["-movflags", "+faststart", out+".mp4"])
                self.log("Rendering Video...")
                subprocess.run(cmd, check=True)
                
                if self.opts['thumb'].get():
                    subprocess.run(["/Users/penelope/homebrew/bin/ffmpeg", "-y", "-ss", "00:00:01", "-i", out+".mp4", "-vframes", "1", out+"_thumb.jpg"])
                
                if self.opts['gif'].get():
                    subprocess.run(["/Users/penelope/homebrew/bin/ffmpeg", "-y", "-i", out+".mp4", "-vf", "fps=10,scale=320:-1:flags=lanczos,split[s0][s1];[s0]palettegen[p];[s1][p]paletteuse", out+".gif"])
                
                if self.opts['safe_zone'].get():
                    subprocess.run(["/Users/penelope/homebrew/bin/ffmpeg", "-y", "-i", out+".mp4", "-vframes", "1", "-vf", "drawbox=x=0:y=ih*0.75:w=iw:h=ih*0.25:color=red@0.5:t=fill,drawbox=x=iw*0.8:y=ih*0.4:w=iw*0.2:h=ih*0.4:color=red@0.5:t=fill", out+"_safezone.jpg"])
                    
        except Exception as e:
            self.log(f"Error: {e}")
        finally:
            self.log("Done!")
            self.btn.config(state='normal')

if __name__ == '__main__':
    root = tk.Tk()
    QuaklerApp(root)
    root.mainloop()

