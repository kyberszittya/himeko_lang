import json

class SaveJsonCommand:
    def __init__(self, editor, filename):
        self.editor = editor
        self.filename = filename

    def execute(self):
        data = self.editor.serialize_to_json()
        with open(self.filename, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
        if hasattr(self.editor, "statusBar"):
            self.editor.statusBar().showMessage(f"Saved to {self.filename}")

class LoadJsonCommand:
    def __init__(self, editor, filename):
        self.editor = editor
        self.filename = filename

    def execute(self):
        with open(self.filename, "r", encoding="utf-8") as f:
            data = json.load(f)
        self.editor.deserialize_from_json(data)
        if hasattr(self.editor, "statusBar"):
            self.editor.statusBar().showMessage(f"Loaded from {self.filename}")

class ClearCommand:
    def __init__(self, editor):
        self.editor = editor

    def execute(self):
        self.editor.scene.clear()
        self.editor.factory.reset()
        self.editor.updateHierarchyPanel()
        self.editor.statusBar().showMessage("Scene cleared.")

class SerializeToJsonCommand:
    def __init__(self, editor):
        self.editor = editor

    def execute(self):
        return self.editor.serialize_to_json()

class DeserializeFromJsonCommand:
    def __init__(self, editor, data):
        self.editor = editor
        self.data = data

    def execute(self):
        self.editor.deserialize_from_json(self.data)

class SaveScreenshotCommand:
    def __init__(self, editor, filename):
        self.editor = editor
        self.filename = filename

    def execute(self):
        pixmap = self.editor.view.grab()
        pixmap.save(self.filename, "PNG")
        if hasattr(self.editor, "statusBar"):
            self.editor.statusBar().showMessage(f"Screenshot saved to {self.filename}")
