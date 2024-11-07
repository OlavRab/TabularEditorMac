from PyQt5.QtWidgets import QApplication, QMainWindow, QTreeWidget, QTreeWidgetItem, QWidget, QFormLayout, QLineEdit, QSplitter, QFileDialog, QMessageBox, QAction
from PyQt5.QtCore import Qt
import sys
import json
import os

class AuroraTabularModeller(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Aurora Tabular Modeller")
        self.setGeometry(300, 300, 1000, 600)
        self.bim_data = None
        self.file_path = None

        # Main Layout
        splitter = QSplitter(Qt.Horizontal)
        self.setCentralWidget(splitter)

        # Tree Widget for JSON hierarchy
        self.tree = QTreeWidget()
        self.tree.setHeaderLabel("Model Structure")
        splitter.addWidget(self.tree)
        
        # Detail Editor
        self.detail_editor = QWidget()
        self.form_layout = QFormLayout()
        self.detail_editor.setLayout(self.form_layout)
        splitter.addWidget(self.detail_editor)

        # Load JSON from file
        self.load_bim_file()

        # Connect tree item selection to editor update
        self.tree.itemClicked.connect(self.on_tree_item_click)

        # Save Action
        self.create_save_action()

    def create_save_action(self):
        # Save Button in the menu
        save_action = QAction("Save", self)
        save_action.setShortcut("Ctrl+S")
        save_action.triggered.connect(self.save_bim_file)
        self.addAction(save_action)

    def load_bim_file(self):
        options = QFileDialog.Options()
        selected_file, _ = QFileDialog.getOpenFileName(
            self,
            "Open .bim File",
            "",
            "BIM Files (*.bim);;All Files (*)",
            options=options
        )
        
        if selected_file:
            self.file_path = selected_file  # Set the file path here
            try:
                with open(self.file_path, 'r', encoding='utf-8-sig') as file:
                    self.bim_data = json.load(file)
                    self.load_tree()
                    QMessageBox.information(self, "File Loaded", f"{os.path.basename(self.file_path)} loaded successfully.")
            except json.JSONDecodeError as e:
                QMessageBox.critical(self, "Error", f"Failed to parse JSON: {e}")
                self.close()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"An unexpected error occurred: {e}")
                self.close()
        else:
            QMessageBox.information(self, "No File Selected", "Please select a .bim file to proceed.")
            self.close()

    def load_tree(self):
        self.tree.clear()
        model_node = QTreeWidgetItem(self.tree, ["Model"])
        QTreeWidgetItem(model_node, [f"name: {self.bim_data.get('name', '')}"])
        QTreeWidgetItem(model_node, [f"compatibilityLevel: {self.bim_data.get('compatibilityLevel', '')}"])
        self.add_sublevel(model_node, "dataSources", self.bim_data.get("model", {}).get("dataSources", []))
        self.add_sublevel(model_node, "tables", self.bim_data.get("model", {}).get("tables", []))
        self.add_sublevel(model_node, "relationships", self.bim_data.get("model", {}).get("relationships", []))
        self.add_sublevel(model_node, "perspectives", self.bim_data.get("model", {}).get("perspectives", []))
        self.add_sublevel(model_node, "annotations", self.bim_data.get("model", {}).get("annotations", []))
        self.add_sublevel(model_node, "translations", self.bim_data.get("model", {}).get("translations", []))
        model_node.setExpanded(True)

    def add_sublevel(self, parent, key, items):
        sublevel_node = QTreeWidgetItem(parent, [key])
        for item in items:
            item_node = QTreeWidgetItem(sublevel_node, [item.get("name", "Unnamed")])
            for k, v in item.items():
                QTreeWidgetItem(item_node, [f"{k}: {v}"])

    def on_tree_item_click(self, item, column):
        # Clear form layout
        for i in reversed(range(self.form_layout.count())): 
            self.form_layout.itemAt(i).widget().setParent(None)

        # Update form layout based on item details
        text = item.text(column)
        if ": " in text:
            key, value = text.split(": ", 1)
            self.current_key = key.strip()  # Store key for saving
            self.current_item = item
            self.current_path = self.get_json_path(item)  # Get JSON path for nested structure
            label = QLineEdit(value.strip())
            label.editingFinished.connect(lambda: self.update_model_value(label.text()))
            self.form_layout.addRow(key.strip(), label)

    def get_json_path(self, item):
        path = []
        while item and item.parent() is not None:
            path.insert(0, item.text(0).split(": ")[0])
            item = item.parent()
        return path

    def update_model_value(self, value):
        # Traverse and update the JSON data based on the current path
        model = self.bim_data["model"]
        for key in self.current_path[:-1]:
            # Handle lists (for items like dataSources, tables, etc.)
            if key.isdigit():
                model = model[int(key)]
            elif key in model:
                model = model[key]
            else:
                QMessageBox.critical(self, "Error", f"Unable to update the path: {self.current_path}")
                return

        # Update the final key with the new value
        last_key = self.current_path[-1]
        if last_key in model:
            # Try to convert value to integer if the original was an integer
            try:
                if isinstance(model[last_key], int):
                    model[last_key] = int(value)
                else:
                    model[last_key] = value
            except ValueError:
                model[last_key] = value

        # Update tree item to show the new value
        self.current_item.setText(0, f"{self.current_key}: {value}")

    def save_bim_file(self):
        if self.file_path:
            print(f"Saving to file path: {self.file_path}")  # Debugging line
            try:
                with open(self.file_path, 'w', encoding='utf-8') as file:
                    json.dump(self.bim_data, file, indent=4)
                QMessageBox.information(self, "File Saved", f"{os.path.basename(self.file_path)} saved successfully.")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to save file: {e}")
        else:
            QMessageBox.critical(self, "Error", "No file path specified for saving.")
            print("No file path available for saving.")  # Debugging line

def main():
    app = QApplication(sys.argv)
    window = AuroraTabularModeller()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()