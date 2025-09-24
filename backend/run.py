from app.main import app, socketio

# Expose the app for Gunicorn
application = app  

if __name__ == '__main__':
    # Only used when running locally (python run.py)
    socketio.run(app, debug=False, host='0.0.0.0', port=8080)
