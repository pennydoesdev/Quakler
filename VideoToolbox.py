import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import subprocess
import os
import threading

class VideoToolboxApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Quakler")
        self.root.geometry("650x750")
        self.root.resizable(False, False)
        
        # Variables
        self.video_path = tk.StringVar()
        self.watermark_path = tk.StringVar()
        self.codec_var = tk.StringVar(value="H.264")
        self.trim_start = tk.StringVar()
        self.trim_end = tk.StringVar()
        self.crop_916 = tk.BooleanVar(value=False)
        self.normalize_audio = tk.BooleanVar(value=False)
        self.extract_audio = tk.BooleanVar(value=False)
        self.transcribe = tk.BooleanVar(value=False)
        self.burn_subs = tk.BooleanVar(value=False)
        self.extract_thumb = tk.BooleanVar(value=False)
        
        self.create_widgets()
        
    def create_widgets(self):
        frame = ttk.Frame(self.root, padding=20)
        frame.pack(fill=tk.BOTH, expand=True)
        
        # Select Video
        ttk.Label(frame, text="1. Select Video", font=("Arial", 14, "bold")).pack(anchor=tk.W, pady=(0, 5))
        vid_frame = ttk.Frame(frame)
        vid_frame.pack(fill=tk.X, pady=5)
        ttk.Entry(vid_frame, textvariable=self.video_path, state='readonly').pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        ttk.Button(vid_frame, text="Browse...", command=self.browse_video).pack(side=tk.RIGHT)
        
        # Video Processing
        ttk.Label(frame, text="2. Video Processing", font=("Arial", 14, "bold")).pack(anchor=tk.W, pady=(15, 5))
        
        codec_frame = ttk.Frame(frame)
        codec_frame.pack(fill=tk.X, pady=2)
        ttk.Label(codec_frame, text="Output Codec:").pack(side=tk.LEFT)
        ttk.Radiobutton(codec_frame, text="H.264 (Most Compatible)", variable=self.codec_var, value="H.264").pack(side=tk.LEFT, padx=10)
        ttk.Radiobutton(codec_frame, text="H.265 (HEVC - Best Compression)", variable=self.codec_var, value="H.265").pack(side=tk.LEFT)
        
        trim_frame = ttk.Frame(frame)
        trim_frame.pack(fill=tk.X, pady=5)
        ttk.Label(trim_frame, text="Trim (Optional) - Start:").pack(side=tk.LEFT)
        ttk.Entry(trim_frame, textvariable=self.trim_start, width=8).pack(side=tk.LEFT, padx=5)
        ttk.Label(trim_frame, text="End:").pack(side=tk.LEFT)
        ttk.Entry(trim_frame, textvariable=self.trim_end, width=8).pack(side=tk.LEFT, padx=5)
        ttk.Label(trim_frame, text="(e.g., 00:00:15)").pack(side=tk.LEFT)
        
        ttk.Checkbutton(frame, text="Crop to Vertical (9:16 for Social)", variable=self.crop_916).pack(anchor=tk.W, pady=2)
        ttk.Checkbutton(frame, text="Extract Thumbnail (Saves a frame as JPG)", variable=self.extract_thumb).pack(anchor=tk.W, pady=2)
        
        # Watermark
        ttk.Label(frame, text="3. Watermark", font=("Arial", 14, "bold")).pack(anchor=tk.W, pady=(15, 5))
        wm_frame = ttk.Frame(frame)
        wm_frame.pack(fill=tk.X, pady=2)
        ttk.Entry(wm_frame, textvariable=self.watermark_path, state='readonly').pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        ttk.Button(wm_frame, text="Select Image (.png)...", command=self.browse_watermark).pack(side=tk.RIGHT)
        
        # Audio & Captions
        ttk.Label(frame, text="4. Audio & Captions", font=("Arial", 14, "bold")).pack(anchor=tk.W, pady=(15, 5))
        ttk.Checkbutton(frame, text="Normalize Audio (Boost to broadcast levels)", variable=self.normalize_audio).pack(anchor=tk.W, pady=2)
        ttk.Checkbutton(frame, text="Extract Audio Only (Rips MP3 and stops)", variable=self.extract_audio).pack(anchor=tk.W, pady=2)
        ttk.Checkbutton(frame, text="Generate Transcript & Subtitles (.txt & .srt via AI)", variable=self.transcribe).pack(anchor=tk.W, pady=2)
        ttk.Checkbutton(frame, text="Hard-Burn Subtitles onto Video", variable=self.burn_subs).pack(anchor=tk.W, pady=2)
        
        # Process Button
        self.process_btn = ttk.Button(frame, text="Start Processing", command=self.start_processing)
        self.process_btn.pack(pady=20, fill=tk.X)
        
        ttk.Label(frame, text="© 2026 Penelope Rose. Proprietary License. All rights reserved.", font=("Arial", 10, "italic"), foreground="gray").pack(side=tk.BOTTOM, pady=(5, 0))
        
        self.log_text = tk.Text(frame, height=10, state='disabled')

        self.log_text.pack(fill=tk.BOTH, expand=True)

    def log(self, msg):
        self.log_text.config(state='normal')
        self.log_text.insert(tk.END, msg + "\n")
        self.log_text.see(tk.END)
        self.log_text.config(state='disabled')
        self.root.update()

    def browse_video(self):
        f = filedialog.askopenfilename(filetypes=[("Video Files", "*.mp4 *.mov *.mkv")])
        if f: self.video_path.set(f)

    def browse_watermark(self):
        f = filedialog.askopenfilename(filetypes=[("Image Files", "*.png")])
        if f: self.watermark_path.set(f)

    def start_processing(self):
        if not self.video_path.get():
            messagebox.showerror("Error", "Please select a video first.")
            return
        self.process_btn.config(state='disabled')
        self.log("Starting job...")
        threading.Thread(target=self.process_video, daemon=True).start()

    def process_video(self):
        try:
            input_file = self.video_path.get()
            base, ext = os.path.splitext(input_file)
            out_dir = os.path.dirname(input_file)
            
            # Step 1: Transcribe
            srt_file = None
            if self.transcribe.get() or self.burn_subs.get():
                self.log("Running Whisper AI Transcription...")
                cmd = ["/Users/penelope/homebrew/bin/whisper", input_file, "--model", "tiny.en", "--output_dir", out_dir, "--output_format", "srt"]
                subprocess.run(cmd, check=True)
                self.log("Transcription finished.")
                srt_file = os.path.join(out_dir, os.path.basename(base) + ".srt")
                
                if self.transcribe.get():
                    cmd_txt = ["/Users/penelope/homebrew/bin/whisper", input_file, "--model", "tiny.en", "--output_dir", out_dir, "--output_format", "txt"]
                    subprocess.run(cmd_txt, check=True)

            # Step 2: Extract Audio
            if self.extract_audio.get():
                self.log("Extracting audio to MP3...")
                out_mp3 = base + "_audio.mp3"
                subprocess.run(["/Users/penelope/homebrew/bin/ffmpeg", "-y", "-i", input_file, "-q:a", "0", "-map", "a", out_mp3], check=True)
                self.log(f"Saved: {out_mp3}")
                self.process_btn.config(state='normal')
                return

            # Step 3: Main Video Processing
            self.log("Processing Video...")
            out_vid = base + "_processed.mp4"
            
            cmd = ["/Users/penelope/homebrew/bin/ffmpeg", "-y", "-i", input_file]
            
            if self.watermark_path.get():
                cmd.extend(["-i", self.watermark_path.get()])
            
            # Trim
            if self.trim_start.get():
                cmd = ["/Users/penelope/homebrew/bin/ffmpeg", "-y", "-ss", self.trim_start.get()]
                if self.trim_end.get():
                    cmd.extend(["-to", self.trim_end.get()])
                cmd.extend(["-i", input_file])
                if self.watermark_path.get():
                    cmd.extend(["-i", self.watermark_path.get()])

            filters = []
            
            if self.crop_916.get():
                filters.append("crop=ih*(9/16):ih")
                
            if self.watermark_path.get():
                filters.append("overlay=W-w-10:H-h-10")
                
            if self.burn_subs.get() and srt_file and os.path.exists(srt_file):
                safe_path = srt_file.replace("\\", "/").replace(":", "\\:")
                filters.append(f"subtitles='{safe_path}'")
                
            if filters:
                cmd.extend(["-vf", ",".join(filters)])
                
            if self.codec_var.get() == "H.265":
                cmd.extend(["-c:v", "libx265", "-tag:v", "hvc1"])
            else:
                cmd.extend(["-c:v", "libx264"])
                
            cmd.extend(["-movflags", "+faststart"])
            
            if self.normalize_audio.get():
                cmd.extend(["-af", "loudnorm=I=-16:TP=-1.5:LRA=11"])
            
            cmd.append(out_vid)
            
            self.log(f"Running FFmpeg...")
            subprocess.run(cmd, check=True)
            self.log(f"Video saved: {out_vid}")
            
            if self.extract_thumb.get():
                self.log("Extracting thumbnail...")
                out_jpg = base + "_thumb.jpg"
                subprocess.run(["/Users/penelope/homebrew/bin/ffmpeg", "-y", "-ss", "00:00:01", "-i", out_vid, "-vframes", "1", "-q:v", "2", out_jpg], check=True)
                self.log(f"Thumbnail saved: {out_jpg}")
                
            self.log("All tasks completed successfully!")
            messagebox.showinfo("Success", "Video processing completed!")
            
        except Exception as e:
            self.log(f"Error: {str(e)}")
            messagebox.showerror("Error", str(e))
        finally:
            self.process_btn.config(state='normal')

if __name__ == '__main__':
    root = tk.Tk()
    app = VideoToolboxApp(root)
    root.mainloop()

