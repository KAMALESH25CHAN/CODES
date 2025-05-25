import flet as ft # type: ignore
class ExpenseTracker:
    def __init__(self, page):
        self.page = page
        self.expenses = []
        self.current_tab = 0

        self.expense_name = ft.TextField(
            label="Expense Name", prefix_icon=ft.icons.TITLE, width=300, border_radius=10
        )
        self.expense_amount = ft.TextField(
            label="Expense Amount", prefix_icon=ft.icons.ATTACH_MONEY, width=300, border_radius=10, keyboard_type=ft.KeyboardType.NUMBER
        )
        self.expense_list = ft.Column(scroll=ft.ScrollMode.AUTO, height=300)
        self.total_expense_text = ft.Text("Total Expense: ₹0", style=ft.TextThemeStyle.HEADLINE_SMALL, weight=ft.FontWeight.BOLD, color="#2196F3")
        self.toast = None

        self.chart_bars = ft.Row([], alignment=ft.MainAxisAlignment.CENTER, spacing=5)

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

    def add_expense(self, e):
        try:
            name = self.expense_name.value.strip()
            amount = float(self.expense_amount.value.strip())

            if not name:
                self.page.snack_bar = ft.SnackBar(content=ft.Text("Please enter an expense name!"))
                self.page.snack_bar.open = True
                self.page.update()
                return

            self.expenses.append({"name": name, "amount": amount})

            self.expense_list.controls.append(
                ft.Container(
                    content=ft.Row([
                        ft.Icon(ft.icons.LABEL, color="#4CAF50"),
                        ft.Text(name, size=16),
                        ft.Text(f"₹{amount:.2f}", size=16, weight=ft.FontWeight.BOLD, color="#2196F3"),
                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                    padding=10,
                    bgcolor="#f5f5f5",
                    border_radius=10
                )
            )
            self.expense_name.value = ""
            self.expense_amount.value = ""

            self.page.snack_bar = ft.SnackBar(content=ft.Text("Expense Added Successfully!"))
            self.page.snack_bar.open = True
            self.page.update()
        except:
            self.page.snack_bar = ft.SnackBar(content=ft.Text("Enter valid amount!"))
            self.page.snack_bar.open = True
            self.page.update()

    def calculate_total(self):
        total = sum(expense["amount"] for expense in self.expenses)
        self.total_expense_text.value = f"Total Expense: ₹{total:.2f}"

    def delete_last_expense(self, e):
        if not self.expenses:
            self.page.snack_bar = ft.SnackBar(content=ft.Text("No expenses to delete!"))
            self.page.snack_bar.open = True
            self.page.update()
            return

        def delete_confirmed(d):
            self.expenses.pop()
            self.expense_list.controls.pop()
            self.calculate_total()
            self.page.snack_bar = ft.SnackBar(content=ft.Text("Last Expense Deleted"))
            self.page.snack_bar.open = True
            self.page.dialog.open = False
            self.page.update()

        self.page.dialog = ft.AlertDialog(
            title=ft.Text("Delete Last Expense?"),
            content=ft.Text("Are you sure you want to delete the last expense?"),
            actions=[
                ft.TextButton("Cancel", on_click=lambda e: setattr(self.page.dialog, 'open', False)),
                ft.TextButton("Delete", on_click=delete_confirmed),
            ],
            open=True,
        )
        self.page.update()

    def build_home(self):
        self.calculate_total()
        return ft.Column(
            controls=[
                ft.Text("Expense Tracker", size=30, weight=ft.FontWeight.BOLD, color="#2196F3"),
                ft.Container(
                    content=ft.Column([
                        self.expense_name,
                        self.expense_amount,
                        ft.Row([
                            ft.ElevatedButton("Add Expense", icon=ft.icons.ADD, on_click=self.add_expense, bgcolor="#4CAF50"),
                            ft.ElevatedButton("Delete Last", icon=ft.icons.DELETE, on_click=self.delete_last_expense, bgcolor="#F44336"),
                        ], alignment=ft.MainAxisAlignment.SPACE_EVENLY),
                    ]),
                    padding=20,
                    bgcolor="#f0f0f0",
                    border_radius=10
                ),
                ft.Text("Your Expenses", size=24, weight=ft.FontWeight.BOLD, color="#4CAF50"),
                ft.Container(
                    content=self.expense_list,
                    padding=10,
                    bgcolor="#ffffff",
                    border_radius=10,
                    height=300,
                    border=ft.border.all(1, "#cccccc")
                ),
                ft.Container(
                    content=self.total_expense_text,
                    alignment=ft.alignment.center,
                    padding=10
                )
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=20,
        )

    def build_add_expense(self):
        return ft.Column(
            controls=[
                ft.Text("Add New Expense", size=28, weight=ft.FontWeight.BOLD, color="#2196F3"),
                self.expense_name,
                self.expense_amount,
                ft.ElevatedButton("Add Expense", icon=ft.icons.SEND, on_click=self.add_expense, bgcolor="#4CAF50")
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=20,
            alignment=ft.MainAxisAlignment.CENTER
        )

    def build_analytics(self):
        total = sum(exp["amount"] for exp in self.expenses)
        highest = max(self.expenses, key=lambda x: x["amount"], default={"amount": 0})["amount"]
        lowest = min(self.expenses, key=lambda x: x["amount"], default={"amount": 0})["amount"]
        avg = total / len(self.expenses) if self.expenses else 0

        # Create bar chart (simple)
        self.chart_bars.controls = []
        for exp in self.expenses[-5:]:  # show last 5 expenses
            bar = ft.Container(
                height=exp["amount"] * 2 if exp["amount"] <= 150 else 150,
                width=20,
                bgcolor="#2196F3",
                border_radius=5,
                tooltip=f"{exp['name']}: ₹{exp['amount']}"
            )
            self.chart_bars.controls.append(bar)

        return ft.Column(
            controls=[
                ft.Text("Expense Analytics", size=28, weight=ft.FontWeight.BOLD, color="#2196F3"),
                ft.Container(
                    content=ft.Column([
                        ft.Text(f"Total Expenses: ₹{total:.2f}"),
                        ft.Text(f"Number of Expenses: {len(self.expenses)}"),
                        ft.Text(f"Average Expense: ₹{avg:.2f}"),
                        ft.Text(f"Highest Expense: ₹{highest:.2f}"),
                        ft.Text(f"Lowest Expense: ₹{lowest:.2f}"),
                    ], spacing=5),
                    padding=20,
                    bgcolor="#f5f5f5",
                    border_radius=10
                ),
                ft.Text("Recent Expense Chart", size=20, weight=ft.FontWeight.BOLD, color="#4CAF50"),
                ft.Container(
                    content=self.chart_bars,
                    height=180,
                    padding=10
                )
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=20
        )

    def switch_tab(self, e):
        self.current_tab = e.control.selected_index
        self.page.controls.clear()

        if self.current_tab == 0:
            self.page.add(self.build_home())
        elif self.current_tab == 1:
            self.page.add(self.build_add_expense())
        elif self.current_tab == 2:
            self.page.add(self.build_analytics())

        self.page.add(self.navbar)
        self.page.update()

    def main(self):
        self.page.title = "Expense Tracker"
        self.page.bgcolor = "#ffffff"
        self.page.padding = 20
        self.page.scroll = ft.ScrollMode.AUTO
        self.page.theme_mode = ft.ThemeMode.LIGHT

        self.page.add(self.build_home(), self.navbar)


def main(page: ft.Page):
    app = ExpenseTracker(page)
    app.main()
    
ft.app(target=main)