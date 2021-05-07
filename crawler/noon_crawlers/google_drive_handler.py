import os

from googleapiclient.http import MediaFileUpload
from .models import *
from .google_drive_api_login import login_google
import shutil
output_folder_ids = {
    'UAE': '1i_bsSeQujS4-DHbCsC_BsqVFhfRbhaBm',
    'KSA': '1lo4t_0jYNxViTxve8I0TA_T1-EQpxWtY',
}


def upload_files_to_google_drive(country):
    debug_file = open('debug/file-upload-debug.txt', 'at', encoding='utf-8')
    files_to_upload = os.listdir('data/' + country)
    for file in files_to_upload:
        debug_file.write('file name : ' + str(file) + '\n')
        try:
            folder_id = output_folder_ids[country]
            drive_service = login_google()
            file_metadata = {
                'name': file,
                'parents': [folder_id]
            }
            media = MediaFileUpload(
                'data/' + country + '/' + file,
                mimetype='application/vnd.openxmlformats-',
                resumable=True
            )
            uploaded_file = drive_service.files().create(body=file_metadata, media_body=media, fields='id').execute()
            debug_file.write('File uploaded successfully\n')
            FilesToDelete(file_id=uploaded_file['id']).save()
        except Exception as error:
            debug_file.write('Error while uploading file\n')
            debug_file.write('Error : ' + str(error) + '\n')
        debug_file.write('=============================\n')
    debug_file.close()


def move_files_to_backup_folder(country):
    files_to_move = os.listdir('data/' + country)
    for file in files_to_move:
        shutil.copy('data/' + country + '/' + file, 'backup/' + country)
    for file in files_to_move:
        os.remove('data/' + country + '/' + file)


def delete_previous_files_from_google_drive():
    debug_file = open('debug/debug-delete-files.txt', 'at', encoding='utf-8')
    drive_service = login_google()
    files = FilesToDelete.objects.filter(created_at__lt=datetime.datetime.now().date())
    try:
        for file in files:
            debug_file.write('File id : ' + str(file.file_id) + '\n')
            drive_service.files().delete(fileId=file.file_id).execute()
            file.delete()
            debug_file.write('File deleted successfully\n')
    except Exception as error:
        debug_file.write('File delete errored out\n')
        debug_file.write(str(error) + '\n')
    debug_file.write('================================\n')
    debug_file.close()

