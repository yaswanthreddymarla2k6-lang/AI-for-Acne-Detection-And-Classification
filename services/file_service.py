import os
import uuid
from datetime import datetime
from werkzeug.utils import secure_filename
from flask import current_app
import logging

logger = logging.getLogger(__name__)

class FileService:
    """File handling service for uploads and storage"""
    
    @staticmethod
    def save_uploaded_file(file, subfolder='uploads'):
        """Save uploaded file and return file path"""
        try:
            if not file or not file.filename:
                return None, "No file provided"
            
            # Generate secure filename
            filename = secure_filename(file.filename)
            if not filename:
                return None, "Invalid filename"
            
            # Add timestamp and UUID to prevent conflicts
            file_ext = filename.rsplit('.', 1)[1].lower() if '.' in filename else ''
            unique_filename = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}.{file_ext}"
            
            # Create upload directory if it doesn't exist
            upload_folder = current_app.config.get('UPLOAD_FOLDER', 'uploads')
            if subfolder:
                upload_folder = os.path.join(upload_folder, subfolder)
            
            os.makedirs(upload_folder, exist_ok=True)
            
            # Save file
            file_path = os.path.join(upload_folder, unique_filename)
            file.save(file_path)
            
            # Return relative path for database storage
            relative_path = os.path.join(subfolder, unique_filename) if subfolder else unique_filename
            
            logger.info(f"File saved: {relative_path}")
            return relative_path, None
            
        except Exception as e:
            logger.error(f"File save error: {str(e)}")
            return None, f"File save failed: {str(e)}"
    
    @staticmethod
    def delete_file(file_path):
        """Delete file from storage"""
        try:
            if not file_path:
                return True
            
            upload_folder = current_app.config.get('UPLOAD_FOLDER', 'uploads')
            full_path = os.path.join(upload_folder, file_path)
            
            if os.path.exists(full_path):
                os.remove(full_path)
                logger.info(f"File deleted: {file_path}")
                return True
            else:
                logger.warning(f"File not found for deletion: {file_path}")
                return True
                
        except Exception as e:
            logger.error(f"File deletion error: {str(e)}")
            return False
    
    @staticmethod
    def get_file_url(file_path):
        """Get URL for accessing file"""
        if not file_path:
            return None
        
        # In production, this would return a proper URL
        # For now, return the path as is
        return f"/files/{file_path}"
    
    @staticmethod
    def cleanup_old_files(days_old=30):
        """Clean up files older than specified days"""
        try:
            upload_folder = current_app.config.get('UPLOAD_FOLDER', 'uploads')
            current_time = datetime.now()
            
            deleted_count = 0
            for root, dirs, files in os.walk(upload_folder):
                for file in files:
                    file_path = os.path.join(root, file)
                    file_time = datetime.fromtimestamp(os.path.getctime(file_path))
                    
                    # Calculate age in days
                    age_days = (current_time - file_time).days
                    
                    if age_days > days_old:
                        os.remove(file_path)
                        deleted_count += 1
                        logger.info(f"Deleted old file: {file}")
            
            logger.info(f"Cleanup completed. Deleted {deleted_count} files older than {days_old} days")
            return deleted_count
            
        except Exception as e:
            logger.error(f"File cleanup error: {str(e)}")
            return 0
    
    @staticmethod
    def get_file_info(file_path):
        """Get file information"""
        try:
            if not file_path:
                return None
            
            upload_folder = current_app.config.get('UPLOAD_FOLDER', 'uploads')
            full_path = os.path.join(upload_folder, file_path)
            
            if not os.path.exists(full_path):
                return None
            
            stat = os.stat(full_path)
            return {
                'path': file_path,
                'size': stat.st_size,
                'created': datetime.fromtimestamp(stat.st_ctime),
                'modified': datetime.fromtimestamp(stat.st_mtime),
                'extension': file_path.rsplit('.', 1)[1].lower() if '.' in file_path else None
            }
            
        except Exception as e:
            logger.error(f"Get file info error: {str(e)}")
            return None
    
    @staticmethod
    def validate_file_type(filename, allowed_types=None):
        """Validate file type"""
        if not filename:
            return False, "No filename provided"
        
        allowed_types = allowed_types or current_app.config.get('ALLOWED_EXTENSIONS', {'png', 'jpg', 'jpeg', 'gif'})
        file_ext = filename.rsplit('.', 1)[1].lower() if '.' in filename else ''
        
        if file_ext in allowed_types:
            return True, "Valid file type"
        else:
            return False, f"File type '{file_ext}' not allowed"
    
    @staticmethod
    def get_storage_stats():
        """Get storage statistics"""
        try:
            upload_folder = current_app.config.get('UPLOAD_FOLDER', 'uploads')
            
            total_files = 0
            total_size = 0
            
            for root, dirs, files in os.walk(upload_folder):
                for file in files:
                    file_path = os.path.join(root, file)
                    if os.path.isfile(file_path):
                        total_files += 1
                        total_size += os.path.getsize(file_path)
            
            return {
                'total_files': total_files,
                'total_size': total_size,
                'total_size_mb': round(total_size / (1024 * 1024), 2),
                'upload_folder': upload_folder
            }
            
        except Exception as e:
            logger.error(f"Storage stats error: {str(e)}")
            return None
