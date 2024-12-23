import re
from textual.app import App ,on
from textual.containers import Grid, Horizontal, Vertical
from textual.screen import Screen
from textual.widgets import (
    Button,
    DataTable,
    Footer,
    Header,
    Input,
    Label,
    Static,
)
from contacts.database1 import Database

def validate_email(email: str) -> bool:
    """Validate an email using regex."""
    pattern = r'^[a-zA-Z][\w\.-]+@[a-zA-Z]+\.[a-zA-Z]{2,3}$'
    return bool(re.match(pattern, email))

def validate_phone(phone :str) -> bool:
    pattern = r'^(\+91)?[6-9]\d{9}$'
    return bool(re.match(pattern , phone))

class ContactsApp(App):
    CSS_PATH = "contacts.tcss"
    BINDINGS = [
        ("m", "toggle_dark", "Toggle dark mode"),
        ("a", "add", "Add"),
        ("d", "delete", "Delete"),
        ("c", "clear_all", "Clear All"),
        ("q", "request_quit", "Quit"),
    ]

    def __init__(self, db):
        super().__init__()
        self.db = db


    def compose(self):
        yield Header()
        search_input = Input(placeholder="Search by Name or Phone", id="search_input") 
        search_button = Button("SEARCH", id="search_button", variant="primary") 

        search_input.styles.width = "80%"
        search_button.styles.width = "20%"

        contacts_list = DataTable(classes="contacts-list",id="contacts-list")
        contacts_list.focus()
        contacts_list.add_columns("Name", "Phone", "Email")
        contacts_list.cursor_type = "row"
        contacts_list.zebra_stripes = True
        add_button = Button("Add", variant="success", id="add")
        add_button.focus()
        buttons_panel = Vertical(
            add_button,
            Button("Delete", variant="warning", id="delete"),
            Static(classes="separator"),
            Button("Clear All", variant="error", id="clear"),
            classes="buttons-panel",
        )
        yield Horizontal(search_input, search_button , classes = "horizontal")
        yield Horizontal(contacts_list, buttons_panel)
        yield Footer()

    def on_mount(self):
        self.title = "RP Contacts"
        self.sub_title = "A Contacts Book App With Textual & Python"
        self._load_contacts()

    def _load_contacts(self):
        contacts_list = self.query_one(DataTable)
        for contact_data in self.db.get_all_contacts():
            id, *contact = contact_data
            contacts_list.add_row(*contact, key=id)
    
    # def action_toggle_dark(self):
    #     self.dark = not self.dark

    def action_request_quit(self):
        def check_answer(accepted):
            if accepted:
                self.exit()

        self.push_screen(QuestionDialog("Do you want to quit?"), check_answer)
    
    def validate_email(email : str) -> bool:
        pattern = r'^[a-zA-Z][\w\.-]+@[a-zA-Z]+\.[a-zA-Z]{2,3}$'
        return bool(re.match(pattern, email))

    
    @on(Button.Pressed, "#add")
    def action_add(self):
        def check_contact(contact_data):
            if contact_data:
                self.db.add_contact(contact_data)
                id, *contact = self.db.get_last_contact()
                self.query_one(DataTable).add_row(*contact, key=id)

        self.push_screen(InputDialog(), check_contact)

    
    @on(Button.Pressed, "#delete")
    def action_delete(self):
        contacts_list = self.query_one(DataTable)
        row_key, _ = contacts_list.coordinate_to_cell_key(
            contacts_list.cursor_coordinate
        )

        def check_answer(accepted):
            if accepted and row_key:
                self.db.delete_contact(id=row_key.value)
                contacts_list.remove_row(row_key)

        name = contacts_list.get_row(row_key)[0]
        self.push_screen(
            QuestionDialog(f"Do you want to delete {name}'s contact?"),
            check_answer,
        )

    @on(Button.Pressed, "#clear")
    def action_clear_all(self):
        def check_answer(accepted):
            if accepted:
                self.db.clear_all_contacts()
                self.query_one(DataTable).clear()

        self.push_screen(
            QuestionDialog("Are you sure you want to remove all contacts?"),
            check_answer,
        )

    @on(Button.Pressed, "#search_button")
    def action_search_contacts(self):
        """Search contacts by name or phone number."""
        query = self.query_one("#search_input", Input).value.strip()  # Get search input
        contacts_list = self.query_one("#contacts-list", DataTable)
        contacts_list.clear()  # Clear current list for displaying search results

        search_results = self.db.search_contacts(query)
        if search_results:
                for contact_data in search_results:
                    id, *contact = contact_data
                    contacts_list.add_row(*contact, key=id)
                self.query_one("#search_input", Input).value = ""  # Clear search input field
        else:
                self.query_one("#search_input", Input).placeholder = "No results found"


class QuestionDialog(Screen):
    def __init__(self, message, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.message = message

    def compose(self):
        no_button = Button("No", variant="primary", id="no")
        no_button.focus()

        yield Grid(
            Label(self.message, id="question"),
            Button("Yes", variant="error", id="yes"),
            no_button,
            id="question-dialog",
        )

    def on_button_pressed(self, event):
        if event.button.id == "yes":
            self.dismiss(True)
        else:
            self.dismiss(False)

class InputDialog(Screen):
    def compose(self):
        yield Grid(
            Label("Add Contact", id="title"),
            Label("Name:", classes="label"),
            Input(
                placeholder="Contact Name",
                classes="input",
                id="name",
            ),
            Label("Phone:", classes="label"),
            Input(
                placeholder="Contact Phone",
                classes="input",
                id="phone",
            ),
            Label("Email:", classes="label"),
            Input(
                placeholder="Contact Email",
                classes="input",
                id="email",
            ),
            Static(),
            Button("Cancel", variant="warning", id="cancel"),
            Button("Ok", variant="success", id="ok"),
            id="input-dialog",
        )

    def on_button_pressed(self, event):
        if event.button.id == "ok":
            name = self.query_one("#name", Input).value
            phone = self.query_one("#phone", Input).value
            email = self.query_one("#email", Input).value
            if not validate_email(email) or not validate_phone(phone):
                self.app.push_screen(
                    QuestionDialog("Invalid Email or Phone No. Please Try again")
                )
            else:
                self.dismiss((name, phone, email))
        else:
            self.dismiss(())
    

