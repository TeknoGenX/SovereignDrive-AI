from django import forms
from .models import Folder, StoredFile

class FolderForm(forms.ModelForm):
    class Meta:
        model = Folder
        fields = ["name", "parent"]
        widgets = {"name": forms.TextInput(attrs={"class": "input"}), "parent": forms.HiddenInput()}

class FileUploadForm(forms.ModelForm):
    class Meta:
        model = StoredFile
        fields = ["name", "file", "folder"]
        widgets = {"name": forms.TextInput(attrs={"class": "input"}), "folder": forms.HiddenInput()}

class FileEditForm(forms.ModelForm):
    class Meta:
        model = StoredFile
        fields = ["name"]
        widgets = {"name": forms.TextInput(attrs={"class": "input"})}
