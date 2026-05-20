# /home/andi-liani/code/awan/storage/views/__init__.py

from .home import home
from .create_folder import create_folder
from .dashboard import dashboard
from .folder_detail import folder_detail
from .delete_file import delete_file
from .delete_folder import delete_folder
from .download_file import download_file
from .edit_file import edit_file
from .file_detail import file_detail
from .get_file_access_role import get_file_access_role
from .get_user_profile import get_user_profile
from .hard_delete_file import hard_delete_file
from .hard_delete_folder import hard_delete_folder
from .profile import profile
from .public_download import public_download
from .restore_file import restore_file
from .restore_folder import restore_folder
from .download_folder import download_folder_zip
from .webhooks import telegram_webhook
from .share_file import share_file
from .share_folder import share_folder
from .toggle_public import toggle_public
from .trash_bin import trash_bin
from .upload_file import upload_file
from .view_file import view_file
from .shared_link import shared_link_view
from .static_pages import privacy_policy, terms_of_service, help_center, user_guide, security_docs