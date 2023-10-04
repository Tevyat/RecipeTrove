from sqlite3 import connect
from customtkinter import *
from tkinter import messagebox

# For packaging, swap <iconname> with the name of the icon
# pyinstaller --onefile --noconfirm --icon=<iconname>.ico --windowed  --add-data <path to customtkinter> RecipeHub.py
# icon at https://www.flaticon.com/free-icon/cook-book_2253457

class RecipeDatabase:
    def __init__(self, db_name='recipes.db'):
        self.conn = connect(db_name)
        self.cursor = self.conn.cursor()
        self.create_table()

    def create_table(self):
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS recipes (
                food_name TEXT PRIMARY KEY,
                ingredients TEXT,
                steps TEXT
            )
        ''')
        self.conn.commit()

    def recipe_exists(self, food_name):
        if not food_name:
            return False
        
        self.cursor.execute('SELECT food_name FROM recipes WHERE food_name LIKE ?', ('%' + food_name + '%',))
        result = self.cursor.fetchone()
        return result is not None

    def get_recipe(self, food_name):
        if self.recipe_exists(food_name):
            self.cursor.execute('''
                SELECT food_name, ingredients, steps FROM recipes
                WHERE food_name LIKE ?
            ''', ('%' + food_name + '%',))
            recipe_details = self.cursor.fetchall()
            return recipe_details
        return False

    def add_recipe(self, food_name, ingredients, steps):
        if not self.recipe_exists(food_name):
            self.cursor.execute('''
                INSERT INTO recipes (food_name, ingredients, steps)
                VALUES (?, ?, ?)
            ''', (food_name, ingredients, steps))
            self.conn.commit()
            return True
        return False

    def edit_recipe(self, food_name, ingredients, steps):
        if self.recipe_exists(food_name):
            self.cursor.execute('''
                UPDATE recipes
                SET ingredients = ?, steps = ?
                WHERE food_name LIKE ?
            ''', (ingredients, steps, '%' + food_name + '%'))
            self.conn.commit()
            return True
        return False

    def remove_recipe(self, food_name):
        if self.recipe_exists(food_name):
            self.cursor.execute('''
                DELETE FROM recipes
                WHERE food_name LIKE ?
            ''', ('%' + food_name + '%',))
            self.conn.commit()
            return True
        return False

    def get_all_recipes(self):
        self.cursor.execute('SELECT food_name FROM recipes')
        food_names = [row[0] for row in self.cursor.fetchall()]
        return food_names

    def close(self):
        self.conn.close()


class rh_add_level(CTkToplevel):
    def __init__(self, *args):
        super().__init__()

        WIDTH = self.winfo_screenwidth()
        HEIGHT = self.winfo_screenheight()

        screen_width = round(WIDTH*0.45)
        screen_height = round(HEIGHT*0.45)

        self.title('Add Recipe')        
        self.geometry(f'{screen_width}x{screen_height}+{screen_width//2}+{screen_height//2}')
        self.configure(fg_color='#9A7B4F')
        self.resizable(False, False)

        self.rowconfigure((0,3), weight=0)
        self.rowconfigure((1,2), weight=2)
        self.columnconfigure(0, weight=1)

        self.button_text = StringVar()
        self.button_text.set('SUBMIT')

        self.rh_textbox_name = CTkTextbox(self, height=screen_height*0.08, width=screen_width*0.55)
        self.rh_textbox_name.grid(row=0, column=0, padx=(20, 20), pady=(20,20), sticky='ew')

        self.rh_textbox_ingredients = CTkTextbox(self, height=screen_height*0.08, width=screen_width*0.55)
        self.rh_textbox_ingredients.grid(row=1, column=0, padx=(20, 20), pady=10, sticky='nsew')

        self.rh_textbox_steps = CTkTextbox(self, height=screen_height*0.08, width=screen_width*0.55)
        self.rh_textbox_steps.grid(row=2, column=0, padx=(20, 20), pady=10, sticky='nsew')

        self.rh_textbox_name.insert('0.0', '<Name here>')
        self.rh_textbox_ingredients.insert('0.0', '- <ingredient>\n- <ingredient>\n- <ingredient>\n- <ingredient>')
        self.rh_textbox_steps.insert('0.0', '1. <step>\n2. <step>\n3. <step>\n4. <step>')
        
        self.rh_submit_button = CTkButton(self, textvariable=self.button_text, fg_color="transparent", hover_color='black', border_width=2, text_color=("gray10", "#DCE4EE"), command=self.add_recipe)
        self.rh_submit_button.grid(row=3, column=0, padx=(20, 20), pady=(20, 20), sticky="nsew")
        
    def add_recipe(self):
        
        name_placeholder = '<Name here>'
        ingredients_placeholder = '- <ingredient>\n- <ingredient>\n- <ingredient>\n- <ingredient>'
        steps_placeholder = '1. <step>\n2. <step>\n3. <step>\n4. <step>'
        
        name_text = self.rh_textbox_name.get('0.0', 'end').strip()
        ingredients_text = self.rh_textbox_ingredients.get('0.0', 'end').strip()
        steps_text = self.rh_textbox_steps.get('0.0', 'end').strip()
        
        try:
            if (name_text == '' or ingredients_text == '' or steps_text == ''):
                raise AssertionError
            elif (name_placeholder in name_text) or (ingredients_placeholder in ingredients_text) or (steps_placeholder in steps_text):
                raise Exception
        except AssertionError:
            messagebox.showerror(title='Unfilled textbox', message='Please fill all the textboxes!')
        except Exception:
            messagebox.showerror(title='Placeholder Detected', message='Please replace placeholder text with actual content!')

        rh.add_recipe(self.rh_textbox_name.get('0.0','end').strip(), self.rh_textbox_ingredients.get('0.0','end').strip(), self.rh_textbox_steps.get('0.0','end'.strip()))
        self.button_text.set('DONE')


class rh_edit_level(CTkToplevel):
    def __init__(self, food_name):
        super().__init__()

        WIDTH = self.winfo_screenwidth()
        HEIGHT = self.winfo_screenheight()

        screen_width = round(WIDTH*0.45)
        screen_height = round(HEIGHT*0.45)

        self.title('Edit Recipe')        
        self.geometry(f'{screen_width}x{screen_height}+{screen_width//2}+{screen_height//2}')
        self.configure(fg_color='#9A7B4F')
        self.resizable(False, False)

        self.rowconfigure((0,3), weight=0)
        self.rowconfigure((1,2), weight=2)
        self.columnconfigure(0, weight=1)

        self.food_name = food_name

        self.button_text = StringVar()
        self.button_text.set('SUBMIT')

        self.rh_textbox_name = CTkTextbox(self, height=screen_height*0.08, width=screen_width*0.55)
        self.rh_textbox_name.grid(row=0, column=0, padx=(20, 20), pady=(20,20), sticky='ew')

        self.rh_textbox_ingredients = CTkTextbox(self, height=screen_height*0.08, width=screen_width*0.55)
        self.rh_textbox_ingredients.grid(row=1, column=0, padx=(20, 20), pady=10, sticky='nsew')

        self.rh_textbox_steps = CTkTextbox(self, height=screen_height*0.08, width=screen_width*0.55)
        self.rh_textbox_steps.grid(row=2, column=0, padx=(20, 20), pady=10, sticky='nsew')

        self.name, ingredients, steps = self.food_name[0][0], self.food_name[0][1], self.food_name[0][2]

        self.rh_textbox_name.insert('0.0', f'{self.name}')
        self.rh_textbox_name.configure(state='disabled')
        self.rh_textbox_ingredients.insert('0.0', f'{ingredients}')
        self.rh_textbox_steps.insert('0.0', f'{steps}')
        
        self.rh_submit_button = CTkButton(self, textvariable=self.button_text, fg_color="transparent", hover_color='black', border_width=2, text_color=("gray10", "#DCE4EE"), command=self.edit_recipe)
        self.rh_submit_button.grid(row=3, column=0, padx=(20, 20), pady=(20, 20), sticky="nsew")

    def edit_recipe(self):
        rh.edit_recipe(self.food_name[0][0], self.rh_textbox_ingredients.get('0.0', 'end'), self.rh_textbox_steps.get('0.0', 'end'))
        self.button_text.set('DONE')

class all_recipes(CTkToplevel):
    def __init__(self):
        super().__init__()

        WIDTH = self.winfo_screenwidth()
        HEIGHT = self.winfo_screenheight()

        screen_width = round(WIDTH*0.2)
        screen_height = round(HEIGHT*0.4)

        self.title('Edit Recipe')        
        self.geometry(f'{screen_width}x{screen_height}+{screen_width/2}+{screen_height/2}')
        self.configure(fg_color='#9A7B4F')
        self.resizable(False, False)

        self.textbox_recipes = CTkTextbox(self)
        self.textbox_recipes.pack(fill='both', expand=True, padx=20, pady=20)

        self.line = '0.0'

        for food in rh.get_all_recipes():
            self.textbox_recipes.insert(self.line, f'{food}\n')
            self.line = str(eval(self.line)+1)

        self.textbox_recipes.configure(state='disabled')


class RecipeHub(CTk):
    def __init__(self):
        super().__init__()

        set_appearance_mode('System')
        set_default_color_theme("blue")

        WIDTH = self.winfo_screenwidth()
        HEIGHT = self.winfo_screenheight()
        
        screen_width = round(WIDTH*0.45)
        screen_height = round(HEIGHT*0.45)

        self.title('RecipeHub')        
        self.geometry(f'{screen_width}x{screen_height}')
        self.configure(fg_color='#C48022')
        self.resizable(False, False)

        self.toplevel_window = None

        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure((2, 3), weight=0)
        self.grid_rowconfigure(0)
        self.grid_rowconfigure(1, weight=1)
        self.grid_rowconfigure(5)

        self.rh_sidebar = CTkFrame(self, width=screen_width*0.3, fg_color='#5A380C', corner_radius=0)
        self.rh_sidebar.grid(row = 0, column=0, rowspan=2, sticky="nsew")
        self.rh_sidebar.grid_rowconfigure(4, weight=1)

        self.rh_label = CTkLabel(self.rh_sidebar, text="RecipeHub", font=CTkFont(size=30, weight="bold"))
        self.rh_label.grid(row=0, column=0, padx=20, pady=(20, 10))

        self.add_recipe_button = CTkButton(self.rh_sidebar, text="Add Recipe", fg_color='#784C12', hover_color='#A96A17', command=self.add_recipe)
        self.add_recipe_button.grid(row=1, column=0, padx=20, pady=(20, 0))

        self.edit_recipe_button = CTkButton(self.rh_sidebar, text="Edit Recipe", fg_color='#784C12', hover_color='#A96A17', command=self.edit_recipe)
        self.edit_recipe_button.grid(row=2, column=0, padx=20, pady=(40, 0))

        self.remove_recipe_button = CTkButton(self.rh_sidebar, text="Delete Recipe", fg_color='#784C12', hover_color='#A96A17', command=self.remove_recipe)
        self.remove_recipe_button.grid(row=3, column=0, padx=20, pady=(40, 0))

        self.show_all_recipe_button = CTkButton(self.rh_sidebar, text="Show Recipes", fg_color='#784C12', hover_color='#A96A17', command=self.show_recipes)
        self.show_all_recipe_button.grid(row=5, column=0, padx=20, pady=40)

        self.rh_entry = CTkEntry(self, height=screen_height*0.08, width=screen_width*0.55, placeholder_text="Enter the recipe you want here...")
        self.rh_entry.grid(row=0, column=1, padx=(20, 20), pady=(20,20), sticky='w')

        self.rh_entry_button = CTkButton(self, text='Find Recipe', fg_color="transparent", hover_color='black', border_width=2, text_color=("gray10", "#DCE4EE"), command=self.find_recipe)
        self.rh_entry_button.grid(row=0, column=3, padx=(10, 25), pady=(20, 20), sticky="nsew")

        self.rh_textbox = CTkTextbox(self)
        self.rh_textbox.grid(row=1, column=1, columnspan=4, padx=(20, 20), pady=(10, 20), sticky="nsew")
        self.rh_textbox.insert('0.0', 'Recipes will appear here...')
        self.rh_textbox.configure(state='disabled')

        self.mainloop()

    def find_recipe(self):
        food_name = self.rh_entry.get()
      
        if rh.recipe_exists(food_name):
            
            recipe = rh.get_recipe(food_name)
            name = recipe[0][0]
            ingredients = recipe[0][1]
            steps = recipe[0][2]

            self.rh_textbox.configure(state='normal')
            self.rh_textbox.delete("0.0", "end")
            self.rh_textbox.insert('0.0', f'{name}\n\n\n{ingredients}\n\n\n{steps}')
            self.rh_textbox.configure(state='disabled')

        else:
            self.rh_textbox.configure(state='normal')
            self.rh_textbox.delete("0.0", "end")
            self.rh_textbox.insert('0.0', 'Recipe not found...')
            self.rh_textbox.configure(state='disabled')

    def add_recipe(self):
        if self.toplevel_window is None or not self.toplevel_window.winfo_exists():
            self.toplevel_window = rh_add_level(self)
            self.toplevel_window.focus()
        else:
            self.toplevel_window.focus()

    def edit_recipe(self):
        food_name = self.rh_entry.get()

        if rh.recipe_exists(food_name):
            food_name = rh.get_recipe(food_name)
            if self.toplevel_window is None or not self.toplevel_window.winfo_exists():
                self.toplevel_window = rh_edit_level(food_name)
                self.toplevel_window.focus()
            else:
                self.toplevel_window.focus()
        else:
            messagebox.showerror(title='Error', message='No recipe indicated.')

    def remove_recipe(self):
        food_name = self.rh_entry.get()

        if rh.recipe_exists(food_name):
            food_name = rh.get_recipe(food_name)
            if messagebox.askyesno(title='Remove Recipe', message=f'Do you want to remove "{food_name[0][0]}" from the database?'):
                try:
                    rh.remove_recipe(food_name[0][0])
                    messagebox.showinfo(title='Successful', message='Recipe successfully deleted.')
                except:
                    messagebox.showerror(title='Error', message='An error occured.')
                    
        else:
            messagebox.showerror(title='Error', message='No recipe indicated.')

    def show_recipes(self):
        if self.toplevel_window is None or not self.toplevel_window.winfo_exists():
            self.toplevel_window = all_recipes()
            self.toplevel_window.focus()
        else:
            self.toplevel_window.focus()
            

if __name__ == '__main__':    
    rh = RecipeDatabase()
    RecipeHub()

