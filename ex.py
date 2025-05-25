# -*- coding: utf-8 -*-
import flet as ft
from datetime import datetime

class ExpenseTracker:
    def __init__(self, page: ft.Page):
        self.page = page
        self.expenses = []
        self.current_tab = 0

        # --- UI Elements ---
        self.expense_name = ft.TextField(
            label="Expense Name", prefix_icon=ft.icons.TITLE, width=300, border_radius=10
        )
        self.expense_amount = ft.TextField(
            label="Expense Amount", prefix_icon=ft.icons.ATTACH_MONEY, width=300, border_radius=10,
            keyboard_type=ft.KeyboardType.NUMBER
        )
        self.expense_category = ft.Dropdown(
            label="Category",
            options=[
                ft.dropdown.Option("Food"),
                ft.dropdown.Option("Transportation"),
                ft.dropdown.Option("Entertainment"),
                ft.dropdown.Option("Utilities"),
                ft.dropdown.Option("Others")
            ],
            width=300,
            border_radius=10
        )

        # --- Date Picker Setup ---
        self.date_display = ft.TextField(
            label="Expense Date",
            read_only=True,
            width=250,
            border_radius=10,
            value=datetime.today().strftime('%Y-%m-%d'),
            tooltip="Selected expense date"
        )
        self.expense_date_picker = ft.DatePicker(
            first_date=datetime(2020, 1, 1),
            last_date=datetime(2030, 12, 31),
            on_change=self.handle_date_change,
        )
        self.date_picker_button = ft.IconButton(
            icon=ft.icons.CALENDAR_MONTH,
            tooltip="Select Date",
            on_click=self.open_date_picker
        )
        # Add DatePicker to overlay ONCE during initialization
        # It's safe to do this here.
        self.page.overlay.append(self.expense_date_picker)

        # --- Other UI Elements ---
        self.expense_list = ft.Column(
            scroll=ft.ScrollMode.AUTO,
            # height=300, # Let container control height
            spacing=5, # Spacing between list items
            expand=True # Allow list to expand within its container
        )
        self.total_expense_text = ft.Text( # Keep as ft.Text
            "Total Expense: ₹0",
            style=ft.TextThemeStyle.HEADLINE_SMALL,
            weight=ft.FontWeight.BOLD,
            color="#2196F3"
        )
        self.chart_bars = ft.Row(
            [],
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=5,
            vertical_alignment=ft.CrossAxisAlignment.END
         )
        self.search_expense = ft.TextField(
            label="Search Expenses",
            prefix_icon=ft.icons.SEARCH,
            width=300,
            border_radius=10,
            on_change=self.filter_expenses
        )
        self.navbar = ft.NavigationBar(
            destinations=[
                ft.NavigationBarDestination(icon=ft.icons.HOME, label="Home"),
                ft.NavigationBarDestination(icon=ft.icons.ADD, label="Add Expense"),
                ft.NavigationBarDestination(icon=ft.icons.ANALYTICS, label="Analytics")
            ],
            selected_index=self.current_tab,
            on_change=self.switch_tab,
            bgcolor="#E3F2FD"
        )

        # Main content area placeholder (will be populated later)
        self.main_content_area = ft.Column(
            expand=True,
            scroll=ft.ScrollMode.ADAPTIVE
        )

    # --- Methods for Date Picker ---
    def open_date_picker(self, e):
        self.expense_date_picker.pick_date()

    def handle_date_change(self, e):
        """Updates the date display field. Safe to update here as UI exists."""
        if self.expense_date_picker.value:
            selected_date = self.expense_date_picker.value.strftime('%Y-%m-%d')
            self.date_display.value = selected_date
            # Check if the control is actually on the page before updating
            # This check might be overly cautious here, but good practice
            if self.date_display.page:
                 try:
                     self.date_display.update()
                 except AssertionError as ae:
                      print(f"AssertionError updating date_display: {ae}. Control might not be fully attached yet.")
                 except Exception as ex:
                      print(f"Error updating date_display: {ex}")


    # --- Core Logic Methods ---
    def add_expense(self, e):
        # Get values
        name = self.expense_name.value.strip()
        amount_str = self.expense_amount.value.strip()
        category = self.expense_category.value
        date_value = self.expense_date_picker.value if self.expense_date_picker.value else datetime.today()

        # Validate
        if not name:
            self.show_snackbar("Please enter an expense name!")
            return
        if not amount_str:
             self.show_snackbar("Please enter an expense amount!")
             return
        if not category:
            self.show_snackbar("Please select a category!")
            return
        try:
            amount = float(amount_str)
            if amount <= 0:
                 self.show_snackbar("Amount must be positive!")
                 return
        except ValueError:
            self.show_snackbar("Enter a valid number for the amount!")
            return

        # Add data
        self.expenses.append({"name": name, "amount": amount, "category": category, "date": date_value})
        self.expenses.sort(key=lambda x: x['date'], reverse=True) # Keep expenses sorted by date desc

        # Update UI (safe to update here)
        self.update_expense_list_display(self.expenses) # Update list display immediately
        self.calculate_total() # Update total immediately

        # Reset fields
        self.expense_name.value = ""
        self.expense_amount.value = ""
        self.expense_category.value = None
        self.expense_date_picker.value = None # Reset picker value
        self.date_display.value = datetime.today().strftime('%Y-%m-%d')

        # Update input fields visually
        self.expense_name.update()
        self.expense_amount.update()
        self.expense_category.update()
        self.date_display.update()

        self.show_snackbar("Expense Added Successfully!")
        # No page.update() needed here, individual updates handled it.

    def calculate_total(self, update_control=True):
        """Calculates and updates the total expenses text.
           Avoids calling update() if update_control is False or control not on page.
        """
        total = sum(expense["amount"] for expense in self.expenses)
        self.total_expense_text.value = f"Total Expense: ₹{total:.2f}"

        # Only update the control if requested AND it's actually part of the page structure
        if update_control and self.total_expense_text.page:
             try:
                 self.total_expense_text.update()
             except Exception as e:
                 print(f"Error updating total_expense_text: {e}") # Log potential update errors

    def delete_last_expense(self, e):
        if not self.expenses:
            self.show_snackbar("No expenses to delete!")
            return

        # Find the most recent expense (assuming list is sorted desc)
        expense_to_delete = self.expenses[0] if self.expenses else None
        if not expense_to_delete: return # Should not happen if expenses list is not empty

        def close_dialog(e):
            self.page.dialog.open = False
            self.page.update()

        def delete_confirmed(e):
            self.expenses.pop(0) # Remove the first item (most recent)
            self.update_expense_list_display(self.expenses) # Update list (safe here)
            self.calculate_total() # Update total (safe here)
            self.show_snackbar("Most Recent Expense Deleted")
            close_dialog(e)

        self.page.dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Delete Recent Expense?"),
            content=ft.Text(f"Delete '{expense_to_delete['name']}' (₹{expense_to_delete['amount']:.2f}) added on {expense_to_delete['date']:%Y-%m-%d}?"),
            actions=[
                ft.TextButton("Cancel", on_click=close_dialog),
                ft.TextButton("Delete", on_click=delete_confirmed, style=ft.ButtonStyle(color=ft.colors.RED)),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
            open=True,
        )
        self.page.update()

    def clear_all_expenses(self, e):
        if not self.expenses:
             self.show_snackbar("No expenses to clear!")
             return

        def close_dialog(e):
            self.page.dialog.open = False
            self.page.update()

        def clear_confirmed(e):
            self.expenses.clear()
            self.update_expense_list_display(self.expenses) # Update list (safe here)
            self.calculate_total() # Update total (safe here)
            self.show_snackbar("All Expenses Cleared")
            close_dialog(e)

        self.page.dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Clear All Expenses?"),
            content=ft.Text("Are you sure you want to clear ALL expenses? This cannot be undone."),
            actions=[
                ft.TextButton("Cancel", on_click=close_dialog),
                ft.TextButton("Clear All", on_click=clear_confirmed, style=ft.ButtonStyle(color=ft.colors.RED)),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
            open=True,
        )
        self.page.update()

    def filter_expenses(self, e):
        query = self.search_expense.value.strip().lower()
        if not query:
             filtered_expenses = self.expenses
        else:
            filtered_expenses = [
                expense for expense in self.expenses
                if query in expense["name"].lower() or \
                   query in expense["category"].lower() or \
                   query in expense["date"].strftime('%Y-%m-%d')
            ]
        # Update display with filtered list (safe to update here as user typed)
        self.update_expense_list_display(filtered_expenses)


    def update_expense_list_display(self, expenses_to_display, update_control=True):
        """Rebuilds the expense list view.
           Avoids calling update() if update_control is False or control not on page.
        """
        self.expense_list.controls.clear()
        if not expenses_to_display:
            self.expense_list.controls.append(ft.Text("No expenses found.", italic=True, color=ft.colors.GREY))
        else:
            for expense in expenses_to_display: # Assumes sorted already
                self.expense_list.controls.append(
                     ft.Container(
                         content=ft.Row([
                             ft.Icon(ft.icons.LABEL_OUTLINE, color="#4CAF50", tooltip=expense['category']),
                             ft.Text(expense["name"], size=15, weight=ft.FontWeight.W_500, expand=True),
                             ft.Text(f"₹{expense['amount']:.2f}", size=15, weight=ft.FontWeight.BOLD, color="#2196F3", text_align=ft.TextAlign.RIGHT),
                             ft.Text(expense['date'].strftime('%d %b %Y'), size=13, color="#757575", text_align=ft.TextAlign.RIGHT),
                         ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN, vertical_alignment=ft.CrossAxisAlignment.CENTER),
                         padding=ft.padding.symmetric(vertical=8, horizontal=12),
                         margin=ft.margin.only(bottom=5),
                         bgcolor=ft.colors.with_opacity(0.05, ft.colors.BLUE_GREY),
                         border_radius=8,
                         ink=True,
                         # on_click=lambda _, exp=expense: self.edit_expense_dialog(exp), # Future edit
                     )
                 )
        # Only update the control if requested AND it's part of the page structure
        if update_control and self.expense_list.page:
             try:
                self.expense_list.update()
             except Exception as e:
                 print(f"Error updating expense_list: {e}")

    def show_snackbar(self, message: str, color: str = ft.colors.BLACK):
        """Helper to show snackbar."""
        if not self.page: return # Guard against page not being available
        self.page.snack_bar = ft.SnackBar(
            content=ft.Text(message, color=ft.colors.WHITE),
            bgcolor=color,
            duration=2500 # Slightly longer duration
        )
        self.page.snack_bar.open = True
        self.page.update() # Update page to show snackbar

    # --- UI Building Methods ---

    def build_home(self):
        """Builds the home screen UI structure."""
        # Set the state of controls based on current data, but DON'T update them individually here.
        self.calculate_total(update_control=False)
        # Pass the current expenses to be displayed initially. Don't update the list control itself here.
        self.update_expense_list_display(self.expenses, update_control=False)

        date_input_row = ft.Row(
            [self.date_display, self.date_picker_button],
            alignment=ft.MainAxisAlignment.START, spacing=5
        )
        action_buttons_row = ft.Row(
            [
                ft.ElevatedButton("Add Expense", icon=ft.icons.ADD, on_click=self.add_expense, bgcolor=ft.colors.GREEN_700, color=ft.colors.WHITE),
                ft.ElevatedButton("Delete Recent", icon=ft.icons.DELETE_SWEEP, on_click=self.delete_last_expense, bgcolor=ft.colors.ORANGE_700, color=ft.colors.WHITE), # Renamed button
                ft.ElevatedButton("Clear All", icon=ft.icons.CLEAR_ALL, on_click=self.clear_all_expenses, bgcolor=ft.colors.RED_700, color=ft.colors.WHITE),
            ],
            alignment=ft.MainAxisAlignment.SPACE_EVENLY # Changed alignment
        )

        return ft.Column(
            controls=[
                ft.Text("Expense Tracker", size=30, weight=ft.FontWeight.BOLD, color="#2196F3"),
                ft.Divider(height=10, color=ft.colors.TRANSPARENT),
                ft.Container(
                    content=ft.Column([
                        self.expense_name,
                        self.expense_amount,
                        self.expense_category,
                        date_input_row,
                        ft.Divider(height=15, color=ft.colors.TRANSPARENT),
                        action_buttons_row,
                    ], spacing=15),
                    padding=20, bgcolor="#f0f4f8", border_radius=10
                ),
                ft.Divider(height=20, color=ft.colors.TRANSPARENT),
                ft.Text("Your Expenses", size=24, weight=ft.FontWeight.BOLD, color="#4CAF50"),
                self.search_expense,
                ft.Container(
                    content=self.expense_list, # The Column containing list items
                    padding=ft.padding.symmetric(horizontal=10, vertical=5),
                    border_radius=10,
                    expand=True, # Critical for list to take space and scroll
                    border=ft.border.all(1, "#e0e0e0"),
                    height=350 # Give the list container a defined height
                ),
                ft.Container(
                    content=self.total_expense_text, # The Text control for total
                    alignment=ft.alignment.center,
                    padding=15,
                    # bgcolor="#e3f2fd",
                    # border_radius=ft.border_radius.only(topLeft=10, topRight=10)
                )
            ],
            spacing=15,
            expand=True # Allow home column to expand
        )

    def build_add_expense(self):
        """Builds the Add Expense screen UI structure."""
        date_input_row = ft.Row(
            [self.date_display, self.date_picker_button],
            alignment=ft.MainAxisAlignment.START, spacing=5
        )
        return ft.Column(
            controls=[
                ft.Text("Add New Expense", size=28, weight=ft.FontWeight.BOLD, color="#2196F3"),
                ft.Divider(height=20, color=ft.colors.TRANSPARENT),
                self.expense_name,
                self.expense_amount,
                self.expense_category,
                date_input_row,
                ft.Divider(height=25, color=ft.colors.TRANSPARENT),
                ft.ElevatedButton(
                    "Add Expense", icon=ft.icons.SEND, on_click=self.add_expense,
                    bgcolor=ft.colors.GREEN_700, color=ft.colors.WHITE, width=200
                 )
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=20, expand=True
        )

    def build_analytics(self):
        """Builds the Analytics screen UI structure."""
        # Calculate stats, but don't update controls here
        self.calculate_total(update_control=False)

        if not self.expenses:
             return ft.Column(
                  controls=[
                       ft.Text("Expense Analytics", size=28, weight=ft.FontWeight.BOLD, color="#2196F3"),
                       ft.Text("No expense data available to analyze.", italic=True, color=ft.colors.GREY, size=16)
                  ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=20, expand=True
             )

        total = sum(exp["amount"] for exp in self.expenses)
        highest_exp = max(self.expenses, key=lambda x: x["amount"], default={"amount": 0, "name": "N/A"})
        lowest_exp = min(self.expenses, key=lambda x: x["amount"], default={"amount": 0, "name": "N/A"})
        avg = total / len(self.expenses) if self.expenses else 0

        category_totals = {}
        for exp in self.expenses:
            category_totals[exp["category"]] = category_totals.get(exp["category"], 0) + exp["amount"]
        category_summary = [
            ft.Row([ft.Text(f"{cat}:", weight=ft.FontWeight.BOLD), ft.Text(f"₹{amount:.2f}")], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
            for cat, amount in sorted(category_totals.items(), key=lambda item: item[1], reverse=True)
        ]

        # Build chart bars data (don't update self.chart_bars here)
        chart_bars_controls = []
        recent_expenses = self.expenses[:10] # Assumes sorted desc
        max_chart_amount = max(exp["amount"] for exp in recent_expenses) if recent_expenses else 1
        max_bar_height = 150

        for exp in recent_expenses:
            bar_height = (exp["amount"] / max_chart_amount) * max_bar_height if max_chart_amount > 0 else 0
            bar = ft.Container(
                height=max(bar_height, 5), width=25, bgcolor="#5c9ced",
                border_radius=ft.border_radius.only(topLeft=5, topRight=5),
                tooltip=f"{exp['name']} ({exp['category']})\n₹{exp['amount']:.2f}\n{exp['date']:%d-%b-%Y}"
            )
            chart_bars_controls.append(bar)
        # Assign the calculated bars to the Row control *after* calculation
        self.chart_bars.controls = chart_bars_controls

        # Return the Column structure for analytics
        return ft.Column(
            controls=[
                ft.Text("Expense Analytics", size=28, weight=ft.FontWeight.BOLD, color="#2196F3"),
                ft.Divider(height=15),
                ft.Container(
                    content=ft.Column([
                         ft.Text("Summary Statistics", style=ft.TextThemeStyle.TITLE_MEDIUM, weight=ft.FontWeight.BOLD), ft.Divider(height=5),
                        ft.Row([ft.Text("Total Expenses:", weight=ft.FontWeight.BOLD), self.total_expense_text]), # Embed total_expense_text here
                        ft.Row([ft.Text("Number of Expenses:", weight=ft.FontWeight.BOLD), ft.Text(f"{len(self.expenses)}")]),
                        ft.Row([ft.Text("Average Expense:", weight=ft.FontWeight.BOLD), ft.Text(f"₹{avg:.2f}")]),
                        ft.Row([ft.Text("Highest Expense:", weight=ft.FontWeight.BOLD), ft.Text(f"₹{highest_exp['amount']:.2f} ({highest_exp['name']})")]),
                        ft.Row([ft.Text("Lowest Expense:", weight=ft.FontWeight.BOLD), ft.Text(f"₹{lowest_exp['amount']:.2f} ({lowest_exp['name']})")]),
                    ], spacing=8),
                    padding=20, bgcolor="#f0f4f8", border_radius=10
                ),
                 ft.Divider(height=15),
                ft.Container(
                    content=ft.Column([
                        ft.Text("Spending by Category", style=ft.TextThemeStyle.TITLE_MEDIUM, weight=ft.FontWeight.BOLD), ft.Divider(height=5),
                        *category_summary
                    ], spacing=8),
                    padding=20, bgcolor="#e8f5e9", border_radius=10
                ),
                ft.Divider(height=15),
                ft.Text("Recent Expense Chart (Last 10)", size=20, weight=ft.FontWeight.BOLD, color="#4CAF50"),
                ft.Container(
                    content=self.chart_bars, # The Row containing the pre-calculated bars
                    padding=ft.padding.only(top=10, bottom=10), alignment=ft.alignment.center,
                    bgcolor="#ffffff", border=ft.border.all(1, "#e0e0e0"), border_radius=8,
                    height=max_bar_height + 30
                )
            ],
            horizontal_alignment=ft.CrossAxisAlignment.STRETCH, spacing=20, expand=True,
            # scroll=ft.ScrollMode.ADAPTIVE # Scrolling handled by parent main_content_area
        )

    def switch_tab(self, e):
        """Switches the content displayed based on the selected navbar index."""
        self.current_tab = e.control.selected_index
        self.main_content_area.controls.clear() # Clear previous tab content

        new_content = None
        if self.current_tab == 0:
            new_content = self.build_home()
        elif self.current_tab == 1:
            new_content = self.build_add_expense()
        elif self.current_tab == 2:
            new_content = self.build_analytics()

        if new_content:
             # Add the newly built structure to the content area
             self.main_content_area.controls.append(new_content)

        # Ensure navbar visually reflects the change (might be handled automatically by NavigationBar)
        # self.navbar.selected_index = self.current_tab # Usually not needed if triggered by on_change

        self.page.update() # Update the page to render the new content

    def build_page_structure(self):
        """Builds the initial page structure with main content area and navbar."""
        self.page.clean() # Clear any previous controls if rebuilding
        self.page.add(
            self.main_content_area, # Add the container for tab content
            self.navbar             # Add the navbar
        )

    def main(self):
        """Sets up the initial page configuration and loads the first view."""
        self.page.title = "Expense Tracker Pro"
        self.page.bgcolor = ft.colors.BLUE_GREY_50
        self.page.padding = 10
        self.page.theme_mode = ft.ThemeMode.LIGHT
        self.page.vertical_alignment = ft.MainAxisAlignment.START # Align content towards the top
        self.page.horizontal_alignment = ft.CrossAxisAlignment.CENTER # Center content horizontally

        # Build the page structure (content area + navbar)
        self.build_page_structure()

        # Build and load the initial content (Home tab)
        initial_content = self.build_home()
        self.main_content_area.controls.append(initial_content)

        # Perform the initial page render
        self.page.update()

# --- App Entry Point ---
def main(page: ft.Page):
    app = ExpenseTracker(page)
    app.main() # Run the app's setup

# Run the Flet app
ft.app(target=main)
