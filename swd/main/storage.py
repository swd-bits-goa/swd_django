from django.core.files.storage import FileSystemStorage

class OverwriteStorage(FileSystemStorage):
    
    def _save(self, name, content):
        self.delete(name)
        return super(OverwriteStorage, self)._save(name, content)

    def get_available_name(self, name, max_length=None):
        return name
    
no_duplicate_storage = OverwriteStorage()