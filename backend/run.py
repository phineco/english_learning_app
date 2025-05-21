from app import create_app, db
from flask_migrate import Migrate
# from app.models import User, Word, Recording # Import models if needed for shell context

app = create_app()
migrate = Migrate(app, db) # Initialize migrate here if not done in create_app or if preferred

@app.shell_context_processor
def make_shell_context():
    # return {'db': db, 'User': User, 'Word': Word, 'Recording': Recording}
    return {'db': db, 'app': app} # Add other models as needed

if __name__ == '__main__':
    # Consider adding host='0.0.0.0' to make it accessible externally if needed
    # and debug=True for development (app.config['DEBUG'] should handle this ideally)
    app.run(debug=app.config.get('DEBUG', True), host='0.0.0.0', port=5001)