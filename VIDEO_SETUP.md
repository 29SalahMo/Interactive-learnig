# Demo Video Setup Guide

## Current Status

The demo video (`Demo/hci project Demo.mp4`) is 155MB, which exceeds GitHub's 100MB file size limit. 

## Solutions

### Option 1: Use Git LFS (Recommended for GitHub)

Git LFS (Large File Storage) allows you to store large files in your repository.

#### Setup Git LFS:

1. **Install Git LFS** (if not already installed):
   ```bash
   # Windows (using Chocolatey)
   choco install git-lfs
   
   # Or download from: https://git-lfs.github.com/
   ```

2. **Initialize Git LFS in your repository**:
   ```bash
   cd "D:\Interactive learnig english quiz for children"
   git lfs install
   ```

3. **Track the video file**:
   ```bash
   git lfs track "Demo/hci project Demo.mp4"
   git add .gitattributes
   git commit -m "Add Git LFS tracking for demo video"
   ```

4. **Add and push the video**:
   ```bash
   git add "Demo/hci project Demo.mp4"
   git commit -m "Add demo video using Git LFS"
   git push origin main
   ```

5. **Update the HTML link** (already done):
   The link in `docs/index.html` will automatically work once the file is in the repository.

### Option 2: Upload to YouTube and Embed

1. Upload your video to YouTube (unlisted or public)
2. Get the video ID from the URL
3. Update `docs/index.html` to embed the YouTube video:

```html
<div class="video-container">
    <iframe width="100%" height="450" 
            src="https://www.youtube.com/embed/YOUR_VIDEO_ID" 
            frameborder="0" 
            allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" 
            allowfullscreen>
    </iframe>
</div>
```

### Option 3: Compress the Video

Reduce the video file size to under 100MB:

1. Use a video compression tool like:
   - HandBrake (free, open-source)
   - FFmpeg (command-line)
   - Online tools like CloudConvert

2. **Using FFmpeg** (if installed):
   ```bash
   ffmpeg -i "Demo/hci project Demo.mp4" -vcodec libx264 -crf 28 -preset slow -acodec aac -b:a 128k "Demo/demo_compressed.mp4"
   ```

3. Replace the original with the compressed version if it's under 100MB

### Option 4: Host on External Service

Upload to a free video hosting service and embed:
- **Vimeo**: Free tier available
- **Google Drive**: Share as embeddable link
- **Dropbox**: Share as direct link

## Current Implementation

The GitHub Pages site currently links to the video using GitHub's raw content URL:
```
https://github.com/29SalahMo/Interactive-learnig/raw/main/Demo/hci%20project%20Demo.mp4
```

This will work once the video is properly added to the repository using one of the methods above.

## Recommendation

**Use Git LFS (Option 1)** - It's the cleanest solution for GitHub repositories and keeps everything in one place.
