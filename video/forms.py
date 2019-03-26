from django import forms

class UploadFileForm(forms.Form):
    file = forms.FileField()
    title = forms.CharField(
        required=False,
        max_length=50,
        label='タイトル',
        help_text='空白の場合は元ファイル名になります'
    )
    