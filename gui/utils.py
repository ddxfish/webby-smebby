from datetime import datetime

def format_time_since(timestamp_str):
    """Convert timestamp to human-readable time-since with max 2 significant numbers"""
    if not timestamp_str:
        return ""
    
    try:
        timestamp = datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S')
        now = datetime.now()
        delta = now - timestamp
        
        # Get total seconds
        total_seconds = delta.total_seconds()
        
        # Less than a minute
        if total_seconds < 60:
            return f"{int(total_seconds)}s"
        
        # Less than an hour
        if total_seconds < 3600:
            minutes = int(total_seconds / 60)
            seconds = int(total_seconds % 60)
            return f"{minutes}m {seconds}s"
        
        # Less than a day
        if total_seconds < 86400:
            hours = int(total_seconds / 3600)
            minutes = int((total_seconds % 3600) / 60)
            return f"{hours}h {minutes}m"
        
        # Less than a month (30 days)
        if total_seconds < 2592000:
            days = int(total_seconds / 86400)
            hours = int((total_seconds % 86400) / 3600)
            return f"{days}d {hours}h"
        
        # Less than a year
        if total_seconds < 31536000:
            months = int(total_seconds / 2592000)
            days = int((total_seconds % 2592000) / 86400)
            return f"{months}mo {days}d"
        
        # More than a year
        years = int(total_seconds / 31536000)
        days = int((total_seconds % 31536000) / 86400)
        return f"{years}y {days}d"
    except:
        return timestamp_str

def get_short_status_code(status, status_code):
    """Convert status and status_code to a 3-character code"""
    # Handle None status
    if status is None:
        return 'UNK'  # Unknown status
    
    if status == 'OK':
        return status_code[:3] if status_code else '200'
    
    # Check that status is a string before calling string methods
    if isinstance(status, str):
        if status.startswith('DNS'):
            return 'DNS'
        
        if status.startswith('SSL'):
            return 'SSL'
        
        if status.startswith('HTTP'):
            # Return the actual HTTP status code if available
            if status_code and status_code.isdigit():
                return status_code[:3]
            return 'HTT'
        
        if status.startswith('String'):
            return 'STR'
        
        if status.startswith('Timeout'):
            return 'TMO'
        
        if status.startswith('Connection'):
            return 'CON'
    
    if status_code and len(status_code) <= 3:
        return status_code
    
    # Default case: take first 3 characters of status if it's a string
    if isinstance(status, str) and status:
        return status[:3].upper()
    
    return 'UNK'  # Default for any other case