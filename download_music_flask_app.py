from flask import Flask, request, jsonify
import subprocess
import os
import logging
from urllib.parse import urlparse

app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.route('/download_music', methods=['POST', 'GET'])
def download_music():
    try:
        # Get the link parameter from either POST JSON or GET query parameter
        if request.method == 'POST':
            data = request.get_json()
            if not data or 'link' not in data:
                return jsonify({'error': 'Missing link parameter in JSON body'}), 400
            link = data['link']
        else:  # GET request
            link = request.args.get('link')
            if not link:
                return jsonify({'error': 'Missing link parameter'}), 400
        
        # Validate the link is an HTTPS URL
        parsed_url = urlparse(link)
        if not parsed_url.scheme == 'https':
            return jsonify({'error': 'Link must be an HTTPS URL'}), 400
        
        logger.info(f"Processing download request for: {link}")
        
        # Create downloads directory if it doesn't exist
        download_dir = os.path.join(os.getcwd(), 'downloads')
        os.makedirs(download_dir, exist_ok=True)
        
        # Example system commands - modify these based on your needs
        # This example uses yt-dlp (YouTube downloader) as a common use case
        commands = [
            # Command 1: Download the audio
            ["spotdl", "download" ,link, "--no-lyrics" , "--bitrate", "320k"],
            
            # Command 2: You can add more commands here
            # ['ffmpeg', '-i', 'input.mp4', 'output.mp3'],  # Example conversion
        ]
        
        results = []
        
        # Execute commands synchronously
        for i, command in enumerate(commands, 1):
            try:
                logger.info(f"Executing command {i}: {' '.join(command)}")
                
                # Run the command and capture output
                result = subprocess.run(
                    command,
                    capture_output=True,
                    text=True,
                    timeout=300,  # 5 minute timeout
                    check=True
                )
                
                results.append({
                    'command': i,
                    'status': 'success',
                    'stdout': result.stdout,
                    'stderr': result.stderr
                })
                
                logger.info(f"Command {i} completed successfully")
                
            except subprocess.CalledProcessError as e:
                error_msg = f"Command {i} failed with return code {e.returncode}"
                logger.error(f"{error_msg}: {e.stderr}")
                results.append({
                    'command': i,
                    'status': 'error',
                    'error': error_msg,
                    'stderr': e.stderr,
                    'stdout': e.stdout
                })
                # Continue with next command even if one fails
                
            except subprocess.TimeoutExpired:
                error_msg = f"Command {i} timed out"
                logger.error(error_msg)
                results.append({
                    'command': i,
                    'status': 'timeout',
                    'error': error_msg
                })
        
        # Prepare response
        success_count = sum(1 for r in results if r['status'] == 'success')
        total_commands = len(results)
        
        response = {
            'message': f'Processing completed. {success_count}/{total_commands} commands succeeded.',
            'link': link,
            'results': results,
            'download_directory': download_dir
        }
        
        # Return appropriate status code
        if success_count == total_commands:
            return jsonify(response), 200
        elif success_count > 0:
            return jsonify(response), 207  # Partial success
        else:
            return jsonify(response), 500  # All failed
            
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        return jsonify({
            'error': 'Internal server error',
            'message': str(e)
        }), 500

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'healthy'}), 200

if __name__ == '__main__':
    # Create downloads directory on startup
    os.makedirs('downloads', exist_ok=True)
    
    # Run the app
    app.run(host='0.0.0.0', port=5000, debug=True)
