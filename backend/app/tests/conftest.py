import pytest
import tempfile
import shutil
from backend.app import create_app, db as _db

@pytest.fixture(scope='session')
def app():
    """Create and configure a new app instance for each test session."""
    # Create a new app instance for testing
    _app = create_app() # Renamed to avoid conflict with app variable name

    # Create a temporary directory for uploads
    temp_upload_dir = tempfile.mkdtemp()

    # Configure for testing
    _app.config.update({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
        # Ensure JWT_SECRET_KEY is set for testing if your app uses Flask-JWT-Extended
        "JWT_SECRET_KEY": "test-secret-key",
        "UPLOAD_FOLDER": temp_upload_dir, # For file saving in routes
        "TTS_AUDIO_FOLDER": temp_upload_dir # Assuming TTS audio also goes here for tests
    })

    with _app.app_context():
        _db.create_all()

    yield _app

    # Teardown: drop all tables after the session and remove temp dir
    with _app.app_context():
        _db.drop_all()
    shutil.rmtree(temp_upload_dir) # Clean up the temporary directory

@pytest.fixture(scope='function')
def client(app):
    """A test client for the app."""
    return app.test_client()

@pytest.fixture(scope='function')
def db_session(app):
    """
    Provides a database session for a test.
    Creates all tables before the test and drops them afterwards.
    Rolls back the session after the test to ensure isolation.
    """
    with app.app_context():
        # _db.create_all() # Tables are created in the app fixture for the session
        
        # Begin a new transaction or use the existing one
        connection = _db.engine.connect()
        transaction = connection.begin()
        
        # Bind an individual session to the connection
        options = dict(bind=connection, binds={})
        session = _db.create_scoped_session(options=options)
        
        _db.session = session # Use this session for the test

    yield session

    # Teardown for the session
    session.remove()
    transaction.rollback() # Rollback to ensure no changes persist
    connection.close()
    # _db.drop_all() # Tables are dropped in the app fixture at the end of the session
