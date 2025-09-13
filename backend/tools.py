import asyncio
import subprocess
import os
import uuid
from typing import Dict, Any
from datetime import datetime

class VisualizationTools:
    """Tools for generating educational visualizations"""
    
    def __init__(self):
        self.visualizations_dir = "visualizations"
        self._ensure_visualizations_dir()
    
    def _ensure_visualizations_dir(self):
        """Create visualizations directory if it doesn't exist"""
        if not os.path.exists(self.visualizations_dir):
            os.makedirs(self.visualizations_dir)
    
    def _cleanup_temp_files(self, script_path: str):
        """Clean up manim script file and media folder after processing"""
        try:
            # Clean up the script file
            if os.path.exists(script_path):
                os.remove(script_path)
                print(f"🧹 Cleaned up manim script: {os.path.basename(script_path)}")
            
            # Clean up the media folder (contains intermediate files from manim)
            media_dir = os.path.join(self.visualizations_dir, "media")
            if os.path.exists(media_dir):
                import shutil
                shutil.rmtree(media_dir)
                print(f"🧹 Cleaned up media folder: {media_dir}")
                
        except Exception as e:
            print(f"Warning: Could not clean up files: {e}")
    
    async def generate_visualization_video(self, manim_script: str, scene_name: str = "Scene") -> Dict[str, Any]:
        """
        Generate a visualization video from a Manim script
        
        Args:
            manim_script: The Manim Python script content
            scene_name: Name of the scene class to render (default: "Scene")
            
        Returns:
            Dict with success status, video path, and any error messages
        """
        try:
            # Generate unique filename for the script
            script_id = str(uuid.uuid4())[:8]
            script_filename = f"manim_script_{script_id}.py"
            script_path = os.path.join(self.visualizations_dir, script_filename)
            
            # Clean the script content - remove escaped newlines
            cleaned_script = manim_script.replace('\\n', '\n').replace('\\', '')
            
            # Add proper imports if not present
            if 'from manim import' not in cleaned_script:
                cleaned_script = f"from manim import *\n\n{cleaned_script}"
            
            # Write the Manim script to file
            with open(script_path, 'w', encoding='utf-8') as f:
                f.write(cleaned_script)
            
            # Debug: Print the script content for debugging (commented out for production)
            # print(f"🔍 Generated Manim script for {scene_name}:")
            # print("=" * 50)
            # print(cleaned_script)
            # print("=" * 50)
            
            # Generate output video filename
            video_filename = f"visualization_{script_id}.mp4"
            video_path = os.path.join(self.visualizations_dir, video_filename)
            
            # Run Manim command asynchronously
            cmd = [
                "manim",
                "-ql",  # Quality low for faster rendering (removed -p to prevent auto-opening)
                os.path.basename(script_path),
                scene_name,
                "-o", video_filename
            ]
            
            # Execute Manim command
            # Set up environment with LaTeX PATH
            env = os.environ.copy()
            env["PATH"] = "/Library/TeX/texbin:" + env.get("PATH", "")
            
            process = await asyncio.create_subprocess_exec(
                *cmd,
                cwd=os.path.dirname(script_path),
                env=env,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            if process.returncode == 0:
                # Look for the video in the media directory structure
                media_dir = os.path.join(self.visualizations_dir, "media", "videos")
                video_found = False
                actual_video_path = None
                
                if os.path.exists(media_dir):
                    for root, dirs, files in os.walk(media_dir):
                        for file in files:
                            if file == video_filename:
                                actual_video_path = os.path.join(root, file)
                                video_found = True
                                break
                        if video_found:
                            break
                
                if video_found and actual_video_path:
                    # Copy video to the expected location for easier access
                    import shutil
                    shutil.copy2(actual_video_path, video_path)
                    
                    # Clean up the manim script file and media folder after successful video generation
                    self._cleanup_temp_files(script_path)
                    
                    return {
                        "success": True,
                        "video_path": video_path,
                        "script_path": script_path,
                        "message": f"Video generated successfully: {video_filename}"
                    }
                else:
                    # Clean up the manim script file and media folder even if video generation failed
                    self._cleanup_temp_files(script_path)
                    return {
                        "success": False,
                        "error": "Video file was not created despite successful command execution",
                        "stdout": stdout.decode(),
                        "stderr": stderr.decode()
                    }
            else:
                # Clean up the manim script file and media folder even if manim command failed
                self._cleanup_temp_files(script_path)
                print(f"❌ Manim command failed with return code {process.returncode}")
                print(f"STDOUT: {stdout.decode()}")
                print(f"STDERR: {stderr.decode()}")
                return {
                    "success": False,
                    "error": f"Manim command failed with return code {process.returncode}",
                    "stdout": stdout.decode(),
                    "stderr": stderr.decode()
                }
                
        except FileNotFoundError:
            # Clean up the manim script file and media folder even if manim is not found
            if 'script_path' in locals():
                self._cleanup_temp_files(script_path)
            return {
                "success": False,
                "error": "Manim is not installed. Please install it with: pip install manim"
            }
        except Exception as e:
            # Clean up the manim script file and media folder even if there's an unexpected error
            if 'script_path' in locals():
                self._cleanup_temp_files(script_path)
            return {
                "success": False,
                "error": f"Unexpected error: {str(e)}"
            }
    
    def cleanup_old_files(self, max_age_hours: int = 24):
        """Clean up old visualization files"""
        try:
            current_time = datetime.now().timestamp()
            max_age_seconds = max_age_hours * 3600
            
            for filename in os.listdir(self.visualizations_dir):
                file_path = os.path.join(self.visualizations_dir, filename)
                if os.path.isfile(file_path):
                    file_age = current_time - os.path.getmtime(file_path)
                    if file_age > max_age_seconds:
                        os.remove(file_path)
        except Exception as e:
            print(f"Error cleaning up files: {e}")

# Global tools instance
visualization_tools = VisualizationTools()
