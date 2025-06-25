import tkinter as tk
from tkinter import messagebox
from tkinter.scrolledtext import ScrolledText
import sqlite3


class RecipeBook:
    def __init__(self):
        self.conn = sqlite3.connect('recipe_book.db')
        self.cursor = self.conn.cursor()
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS recipes (
                name TEXT PRIMARY KEY,
                ingredients TEXT,
                instructions TEXT
            )
        ''')
        self.conn.commit()

    def add_recipe(self, name, ingredients, instructions):
        try:
            if not name.strip() or not ingredients.strip() or not instructions.strip():
                messagebox.showerror("Error", "Please fill in all fields.")
                return False
            if not all(x.isalpha() or x.isspace() for x in name):
                messagebox.showerror("Error", "Recipe name can only contain letters and spaces.")
                return False
            if ',' in name:
                messagebox.showerror("Error", "Recipe name cannot contain commas.")
                return False

            self.cursor.execute('INSERT INTO recipes VALUES (?, ?, ?)', (name, ingredients, instructions))
            self.conn.commit()
            return True
        except sqlite3.IntegrityError:
            messagebox.showerror("Error", "Recipe with the same name already exists.")
            return False

    def get_recipe(self, name):
        self.cursor.execute('SELECT ingredients, instructions FROM recipes WHERE name = ?', (name,))
        result = self.cursor.fetchone()
        return result if result else None

    def list_recipes(self):
        self.cursor.execute('SELECT name FROM recipes')
        return [row[0] for row in self.cursor.fetchall()]

    def update_recipe(self, name, new_ingredients, new_instructions):
        try:
            self.cursor.execute('UPDATE recipes SET ingredients=?, instructions=? WHERE name=?',
                                (new_ingredients, new_instructions, name))
            self.conn.commit()
            return True
        except sqlite3.IntegrityError:
            messagebox.showerror("Error", "Error updating recipe.")
            return False

    def delete_recipe(self, name):
        try:
            self.cursor.execute('DELETE FROM recipes WHERE name = ?', (name,))
            self.conn.commit()
            return True
        except sqlite3.IntegrityError:
            messagebox.showerror("Error", "Error deleting recipe.")
            return False


class RecipeAddWindow:
    def __init__(self, parent, recipe_book):
        self.recipe_book = recipe_book
        self.window = tk.Toplevel(parent)
        self.window.title("Add Recipe")
        self.window.geometry("450x350")
        self.window.configure(bg="#FAFAD2")

        tk.Label(self.window, text="Recipe Name:", bg="#FAFAD2", font=("Arial", 10)).pack(pady=(10, 0))
        self.recipe_name_entry = tk.Entry(self.window, width=40)
        self.recipe_name_entry.pack()

        tk.Label(self.window, text="Ingredients (comma-separated):", bg="#FAFAD2", font=("Arial", 10)).pack(pady=(10, 0))
        self.ingredients_entry = tk.Entry(self.window, width=40)
        self.ingredients_entry.pack()

        tk.Label(self.window, text="Instructions (one per line):", bg="#FAFAD2", font=("Arial", 10)).pack(pady=(10, 0))
        self.instructions_text = ScrolledText(self.window, height=6, width=40)
        self.instructions_text.pack()

        self.add_button = tk.Button(self.window, text="Add Recipe", command=self.add_recipe,
                                    bg="#32CD32", fg="white", font=("Arial", 10, "bold"))
        self.add_button.pack(pady=10)

    def add_recipe(self):
        name = self.recipe_name_entry.get().strip()
        ingredients = self.ingredients_entry.get().strip()
        instructions = self.instructions_text.get("1.0", tk.END).strip()
        if self.recipe_book.add_recipe(name, ingredients, instructions):
            messagebox.showinfo("Success", "Recipe added successfully.")
            self.window.destroy()
        else:
            messagebox.showerror("Error", "Recipe could not be added.")


class RecipeGetWindow:
    def __init__(self, parent, recipe_book):
        self.recipe_book = recipe_book
        self.window = tk.Toplevel(parent)
        self.window.title("Get Recipe")
        self.window.geometry("400x150")
        self.window.configure(bg="#E0FFFF")

        tk.Label(self.window, text="Recipe Name:", bg="#E0FFFF", font=("Arial", 10)).pack(pady=(20, 0))
        self.recipe_name_entry = tk.Entry(self.window, width=30)
        self.recipe_name_entry.pack()

        self.get_button = tk.Button(self.window, text="Get Recipe", command=self.get_recipe,
                                    bg="#20B2AA", fg="white", font=("Arial", 10, "bold"))
        self.get_button.pack(pady=10)

    def get_recipe(self):
        name = self.recipe_name_entry.get().strip()
        recipe = self.recipe_book.get_recipe(name)
        if recipe:
            ingredients, instructions = recipe
            messagebox.showinfo(name, f"Ingredients:\n{ingredients}\n\nInstructions:\n{instructions}")
        else:
            messagebox.showerror("Error", "Recipe not found.")


class RecipeUpdateWindow:
    def __init__(self, parent, recipe_book, recipe_name):
        self.recipe_book = recipe_book
        self.recipe_name = recipe_name

        ingredients, instructions = self.recipe_book.get_recipe(recipe_name)

        self.window = tk.Toplevel(parent)
        self.window.title("Update Recipe")
        self.window.geometry("450x350")
        self.window.configure(bg="#FFEFD5")

        tk.Label(self.window, text="Recipe Name:", bg="#FFEFD5", font=("Arial", 10)).pack(pady=(10, 0))
        self.recipe_name_entry = tk.Entry(self.window, state=tk.DISABLED, width=40)
        self.recipe_name_entry.insert(0, recipe_name)
        self.recipe_name_entry.pack()

        tk.Label(self.window, text="Ingredients (comma-separated):", bg="#FFEFD5", font=("Arial", 10)).pack(pady=(10, 0))
        self.ingredients_entry = tk.Entry(self.window, width=40)
        self.ingredients_entry.insert(0, ingredients)
        self.ingredients_entry.pack()

        tk.Label(self.window, text="Instructions (one per line):", bg="#FFEFD5", font=("Arial", 10)).pack(pady=(10, 0))
        self.instructions_text = ScrolledText(self.window, height=6, width=40)
        self.instructions_text.insert(tk.END, instructions)
        self.instructions_text.pack()

        self.update_button = tk.Button(self.window, text="Update Recipe", command=self.update_recipe,
                                       bg="#FF8C00", fg="white", font=("Arial", 10, "bold"))
        self.update_button.pack(pady=10)

    def update_recipe(self):
        new_ingredients = self.ingredients_entry.get().strip()
        new_instructions = self.instructions_text.get("1.0", tk.END).strip()
        if self.recipe_book.update_recipe(self.recipe_name, new_ingredients, new_instructions):
            messagebox.showinfo("Success", "Recipe updated successfully.")
            self.window.destroy()
        else:
            messagebox.showerror("Error", "Recipe could not be updated.")


class RecipeBookGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("🍲 My Recipe Book")
        self.root.geometry("500x600")
        self.root.configure(bg="#FFF8DC")

        self.recipe_book = RecipeBook()

        self.heading = tk.Label(
            root, text="🍳 Welcome to My Recipe Book!", font=("Helvetica", 20, "bold"),
            fg="#8B0000", bg="#FFF8DC"
        )
        self.heading.pack(pady=(20, 10))

        self.subheading = tk.Label(
            root,
            text="“A recipe has no soul. You as the cook must bring soul to the recipe.”",
            font=("Comic Sans MS", 12, "italic"),
            fg="#4B0082", bg="#FFF8DC", wraplength=400, justify="center"
        )
        self.subheading.pack(pady=(0, 20))

        self.add_button = tk.Button(
            root, text="➕ Add Recipe", command=self.open_add_recipe_window,
            bg="#32CD32", fg="white", font=("Arial", 12, "bold"), width=20
        )
        self.add_button.pack(pady=10)

        self.list_button = tk.Button(
            root, text="📋 List Recipes", command=self.list_recipes,
            bg="#4682B4", fg="white", font=("Arial", 12, "bold"), width=20
        )
        self.list_button.pack(pady=10)

        self.get_button = tk.Button(
            root, text="🔍 Get Recipe", command=self.open_get_recipe_window,
            bg="#FFA500", fg="white", font=("Arial", 12, "bold"), width=20
        )
        self.get_button.pack(pady=10)

        self.info_label = tk.Label(
            root,
            text="✨ Explore, Create & Relish your Recipes ✨",
            font=("Verdana", 11, "bold"),
            fg="#DA70D6", bg="#FFF8DC"
        )
        self.info_label.pack(pady=(20, 10))

        self.recipe_listbox = tk.Listbox(root, selectmode=tk.SINGLE, font=("Courier", 10), height=10)
        self.recipe_listbox.pack(padx=20, pady=10, fill=tk.BOTH, expand=True)

    def open_add_recipe_window(self):
        RecipeAddWindow(self.root, self.recipe_book)

    def list_recipes(self):
        self.recipe_listbox.delete(0, tk.END)
        recipes = self.recipe_book.list_recipes()

        list_window = tk.Toplevel(self.root)
        list_window.title("📘 List of Recipes")
        list_window.geometry("400x400")
        list_window.configure(bg="#FAFAD2")

        for recipe in recipes:
            frame = tk.Frame(list_window, bg="#FAFAD2")
            frame.pack(fill=tk.X, padx=10, pady=3)

            label = tk.Label(frame, text=recipe, bg="#FAFAD2", font=("Arial", 10))
            label.pack(side=tk.LEFT)

            delete_btn = tk.Button(frame, text="🗑 Delete", command=lambda r=recipe: self.delete_recipe(r),
                                   bg="#FF6347", fg="white", font=("Arial", 9, "bold"))
            delete_btn.pack(side=tk.RIGHT, padx=5)

            update_btn = tk.Button(frame, text="✏ Update", command=lambda r=recipe: self.open_update_recipe_window(r),
                                   bg="#FFD700", fg="black", font=("Arial", 9, "bold"))
            update_btn.pack(side=tk.RIGHT)

    def open_get_recipe_window(self):
        RecipeGetWindow(self.root, self.recipe_book)

    def open_update_recipe_window(self, recipe_name):
        RecipeUpdateWindow(self.root, self.recipe_book, recipe_name)

    def delete_recipe(self, recipe_name):
        result = self.recipe_book.delete_recipe(recipe_name)
        if result:
            messagebox.showinfo("Success", f"Recipe '{recipe_name}' deleted successfully.")
            self.list_recipes()
        else:
            messagebox.showerror("Error", "Error deleting recipe.")


if __name__ == "__main__":
    root = tk.Tk()
    app = RecipeBookGUI(root)
    root.mainloop()
