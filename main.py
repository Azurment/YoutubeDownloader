from customtkinter import *
from tkinter import messagebox
import os
import yt_dlp

app = CTk()

# Global variable to store available resolutions
available_resolutions = []
resolution_var = StringVar(value="Select Resolution")

def fetch_resolutions():
    """Fetch available resolutions for the given YouTube video link."""
    video_url = input_box.get()

    if not video_url.strip():
        messagebox.showerror("Error", "Please enter a valid YouTube link.")
        return

    global available_resolutions

    try:
        # Use yt-dlp to get video information
        ydl_opts = {
            'noplaylist': True,  # Only fetch the info for a single video
            'quiet': True,  # Suppress console output
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_url, download=False)  # Fetch video info without downloading

        # Extract available resolutions with audio
        available_resolutions = [
            f"{stream['format_id']} ({stream['height']}p)"
            for stream in info['formats']
            if 'height' in stream and 'vcodec' in stream and stream['vcodec'] != 'none'
        ]

        # If no resolutions found, notify the user
        if not available_resolutions:
            available_resolutions = ["No Resolutions Found"]

        # Update the dropdown menu
        resolution_menu.configure(values=available_resolutions)

        # Reset to the first resolution option
        resolution_var.set(available_resolutions[0])
        messagebox.showinfo("Resolutions Loaded", "Available resolutions have been loaded.")
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred while fetching resolutions: {str(e)}")

def download_video():
    video_url = input_box.get()
    selected_resolution = resolution_var.get()

    if not video_url.strip():
        messagebox.showerror("Error", "Please enter a valid YouTube link.")
        return

    if not available_resolutions or selected_resolution == "Select Resolution":
        messagebox.showerror("Error", "Please load and select a resolution before downloading.")
        return

    try:
        # Extract the format_id from the selected resolution
        selected_format = selected_resolution.split(" ")[0]  # Get the format ID (e.g., '22')

        # Get the video size using yt-dlp
        ydl_opts = {
            'noplaylist': True,  # Only fetch the info for a single video
            'quiet': True,  # Suppress console output
            'extract_flat': True  # Only extract metadata, no download
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_url, download=False)

        # Find the file size in MB
        file_size = info.get('filesize', None)
        if file_size:
            file_size_mb = file_size / (1024 * 1024)  # Convert bytes to MB
            file_size_mb = round(file_size_mb, 2)  # Round to 2 decimal places
        else:
            file_size_mb = "Unknown"

        # Ask for user confirmation with file size
        confirm = messagebox.askyesno(
            "Confirm Download",
            f"Do you want to download the video with size {file_size_mb} MB?"
        )

        if not confirm:
            return

        # Get the user's Downloads folder
        downloads_folder = os.path.join(os.path.expanduser("~"), "Downloads", "YouTube Downloads")

        # Create the folder if it doesn't exist
        if not os.path.exists(downloads_folder):
            os.makedirs(downloads_folder)

        # Path to ffmpeg (if not already in PATH)
        ffmpeg_path = r'ffmpeg/bin/ffmpeg.exe'  # Update to the correct path

        # yt-dlp options to download both video and audio
        ydl_opts = {
            'ffmpeg_location': ffmpeg_path,  # Specify ffmpeg location
            'format': f'{selected_format}+bestaudio',  # Ensure best video and audio are downloaded
            'outtmpl': os.path.join(downloads_folder, '%(title)s.%(ext)s'),  # Save with the video title as filename
            'noplaylist': True,  # Ensure only a single video is downloaded
            'merge_output_format': 'mp4',  # Merge video and audio into an MP4 file if they're separate
        }

        # Download the video
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([video_url])

        messagebox.showinfo("Success", f"Video downloaded successfully!\nSaved to {downloads_folder}")
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {str(e)}")

# UI Components
app.title("YouTube Video Downloader")
app.geometry("600x400")
app.minsize(500, 300)
app.maxsize(800, 600)

label = CTkLabel(app, text="YouTube Video Downloader", font=("Arial", 36, "bold"))
label.pack(pady=10)

space = CTkLabel(app, text="")
space.pack(pady=10)

input_box = CTkEntry(app, placeholder_text="Enter the link", width=275)
input_box.pack(pady=10)

fetch_button = CTkButton(app, text="Load Resolutions", command=fetch_resolutions)
fetch_button.pack(pady=10)

resolution_menu = CTkOptionMenu(app, variable=resolution_var, values=["Select Resolution"])
resolution_menu.pack(pady=10)

download_button = CTkButton(app, text="Download", command=download_video)
download_button.pack(pady=10)

app.mainloop()
