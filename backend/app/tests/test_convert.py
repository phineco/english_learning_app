import pytest
import io
from unittest import mock # Corrected import for mock

from backend.app.models import User, UploadedFile # Added model imports

# Helper function to create a user
def create_user(db_session, id, username, email, password="password"):
    user = User(id=id, username=username, email=email)
    user.set_password(password)
    db_session.add(user)
    db_session.commit()
    return user

def test_text_to_speech_valid_file(client):
    """Test text-to-speech with a valid .txt file."""
    data = {
        'file': (io.BytesIO(b"Hello world"), 'test.txt')
    }
    response = client.post('/convert/text-to-speech', data=data, content_type='multipart/form-data')

    assert response.status_code == 200
    assert response.mimetype == 'audio/mpeg'
    assert response.data == b'MOCK_MP3_DATA' # This is based on the current mock in the route
    assert 'attachment' in response.headers['Content-Disposition']
    assert 'filename=output.mp3' in response.headers['Content-Disposition']

def test_text_to_speech_no_file(client):
    """Test text-to-speech with no file provided."""
    response = client.post('/convert/text-to-speech', data={})
    
    assert response.status_code == 400
    json_data = response.get_json()
    assert json_data == {'message': '缺少txt文件'}

def test_text_to_speech_invalid_extension(client):
    """Test text-to-speech with a file having an invalid extension."""
    data = {
        'file': (io.BytesIO(b"fake image data"), 'test.jpg')
    }
    response = client.post('/convert/text-to-speech', data=data, content_type='multipart/form-data')
    
    assert response.status_code == 400
    json_data = response.get_json()
    assert json_data == {'message': '文件类型错误，仅支持txt'}

# Tests for /speech-to-text endpoint

@mock.patch('backend.app.routes.convert.model.generate')
def test_speech_to_text_valid_file(mock_generate, client, db_session):
    """Test speech-to-text with a valid .mp3 file and user_id."""
    mock_generate.return_value = [{'text': 'mocked recognized text'}]
    
    # Create a dummy user
    test_user = create_user(db_session, id=1, username='testuser_stt_valid', email='test_stt_valid@example.com')

    data = {
        'file': (io.BytesIO(b"fake mp3 data"), 'audio.mp3'),
        'user_id': test_user.id
    }
    response = client.post('/convert/speech-to-text', data=data, content_type='multipart/form-data')

    assert response.status_code == 200
    json_data = response.get_json()
    assert json_data == {'text': 'mocked recognized text'}

    # Verify database record
    uploaded_file = db_session.query(UploadedFile).filter_by(user_id=test_user.id).first()
    assert uploaded_file is not None
    assert uploaded_file.filename == 'audio.mp3'
    assert uploaded_file.text_content == 'mocked recognized text'
    assert uploaded_file.file_type == 'mp3'
    assert uploaded_file.user_id == test_user.id
    mock_generate.assert_called_once()

def test_speech_to_text_no_file(client, db_session):
    """Test speech-to-text with no file provided but with user_id."""
    test_user = create_user(db_session, id=2, username='testuser_stt_nofile', email='test_stt_nofile@example.com')
    data = {'user_id': test_user.id} # No file part
    response = client.post('/convert/speech-to-text', data=data, content_type='multipart/form-data')
    
    assert response.status_code == 400
    json_data = response.get_json()
    assert json_data == {'message': '缺少mp3文件'}

def test_speech_to_text_invalid_extension(client, db_session):
    """Test speech-to-text with an invalid file extension and user_id."""
    test_user = create_user(db_session, id=3, username='testuser_stt_invalidext', email='test_stt_invalidext@example.com')
    data = {
        'file': (io.BytesIO(b"fake text data"), 'document.txt'),
        'user_id': test_user.id
    }
    response = client.post('/convert/speech-to-text', data=data, content_type='multipart/form-data')
    
    assert response.status_code == 400
    json_data = response.get_json()
    assert json_data == {'message': '文件类型错误，仅支持mp3'}

def test_speech_to_text_no_user_id_no_default_user(client, db_session, app):
    """Test speech-to-text with a valid file but no user_id and no default user in DB."""
    # Ensure no users exist
    db_session.query(User).delete()
    db_session.commit()
    
    data = {
        'file': (io.BytesIO(b"fake mp3 data"), 'audio.mp3')
    }
    response = client.post('/convert/speech-to-text', data=data, content_type='multipart/form-data')
    
    assert response.status_code == 401
    json_data = response.get_json()
    assert json_data == {"success": False, "message": "User not found or not authenticated. Please create a user first."}

@mock.patch('backend.app.routes.convert.model.generate')
def test_speech_to_text_no_user_id_with_default_user(mock_generate, client, db_session, app):
    """Test speech-to-text with a valid file, no user_id, but a default user exists."""
    mock_generate.return_value = [{'text': 'mocked recognized text for default user'}]

    # Ensure no users exist initially for a clean test, then create the default
    db_session.query(User).delete()
    db_session.commit()
    default_user = create_user(db_session, id=10, username='defaultuser', email='default@example.com') # ID 10 or any other

    data = {
        'file': (io.BytesIO(b"fake mp3 data for default"), 'default_audio.mp3')
    }
    response = client.post('/convert/speech-to-text', data=data, content_type='multipart/form-data')

    assert response.status_code == 200
    json_data = response.get_json()
    assert json_data == {'text': 'mocked recognized text for default user'}

    # Verify database record for the default user
    # The route implementation should pick the first user if no user_id is provided.
    # We need to ensure our default_user is that first user.
    first_user_in_db = db_session.query(User).order_by(User.id).first()
    assert first_user_in_db is not None
    assert first_user_in_db.id == default_user.id # Ensure it's our intended default user

    uploaded_file = db_session.query(UploadedFile).filter_by(user_id=first_user_in_db.id).first()
    assert uploaded_file is not None
    assert uploaded_file.filename == 'default_audio.mp3'
    assert uploaded_file.text_content == 'mocked recognized text for default user'
    assert uploaded_file.file_type == 'mp3'
    assert uploaded_file.user_id == first_user_in_db.id
    mock_generate.assert_called_once()
