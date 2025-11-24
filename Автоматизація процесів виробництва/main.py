import csv
import uuid
from datetime import datetime
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

CSV_HEADERS = ['id', 'name', 'category', 'quantity', 'price', 'location', 'created_at']


class InventoryApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Inventory — Product Management")
        self.geometry("1000x600")
        self.minsize(800, 480)

        self.data = []

        self._create_menu()
        self._create_widgets()
        self._create_statusbar()

        self.current_file = None
        self._sort_column = None
        self._sort_reverse = False

    def _create_menu(self):
        menubar = tk.Menu(self)
        filem = tk.Menu(menubar, tearoff=False)
        filem.add_command(label="Open...", command=self.load_csv)
        filem.add_command(label="Save", command=self.save_csv)
        filem.add_command(label="Save As...", command=self.save_csv_as)
        filem.add_separator()
        filem.add_command(label="Exit", command=self.quit)
        menubar.add_cascade(label="File", menu=filem)
        self.config(menu=menubar)

    def _create_widgets(self):
        main = ttk.Frame(self)
        main.pack(fill=tk.BOTH, expand=True, padx=6, pady=6)

        left = ttk.Frame(main)
        left.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        right = ttk.Frame(main, width=320)
        right.pack(side=tk.RIGHT, fill=tk.Y, padx=(8,0))

        search_frame = ttk.Frame(left)
        search_frame.pack(fill=tk.X, pady=(0,6))
        ttk.Label(search_frame, text="Search:").pack(side=tk.LEFT)
        self.search_var = tk.StringVar()
        ent_search = ttk.Entry(search_frame, textvariable=self.search_var)
        ent_search.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(6,6))
        ent_search.bind("<KeyRelease>", lambda e: self.refresh_tree())
        ttk.Button(search_frame, text="Clear", command=self._clear_search).pack(side=tk.LEFT)

        cols = ['id','name','category','quantity','price','location']
        self.tree = ttk.Treeview(left, columns=cols, show='headings', selectmode='browse')
        for c in cols:
            self.tree.heading(c, text=c.capitalize(), command=lambda _c=c: self._on_heading_click(_c))
            self.tree.column(c, anchor=tk.W, width=100, minwidth=60)
        self.tree.pack(fill=tk.BOTH, expand=True)
        self.tree.bind("<<TreeviewSelect>>", self._on_tree_select)

        vsb = ttk.Scrollbar(left, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=vsb.set)
        vsb.place(in_=self.tree, relx=1.0, rely=0, relheight=1.0, bordermode="outside")

        form = ttk.Frame(right)
        form.pack(fill=tk.Y, padx=4, pady=4, anchor=tk.N)

        self.entries = {}
        fields = [
            ('id', 'ID (can be left empty)'),
            ('name', 'Name'),
            ('category', 'Category'),
            ('quantity', 'Quantity'),
            ('price', 'Price'),
            ('location', 'Location'),
        ]
        for key, label in fields:
            lbl = ttk.Label(form, text=label)
            lbl.pack(anchor=tk.W, pady=(6,0))
            var = tk.StringVar()
            ent = ttk.Entry(form, textvariable=var)
            ent.pack(fill=tk.X)
            self.entries[key] = (var, ent)

        btn_frame = ttk.Frame(form)
        btn_frame.pack(fill=tk.X, pady=(12,0))

        ttk.Button(btn_frame, text="Add", command=self.add_item).pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Button(btn_frame, text="Update", command=self.update_item).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(6,0))
        ttk.Button(btn_frame, text="Delete", command=self.delete_item).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(6,0))

        ttk.Button(form, text="Clear Form", command=self.clear_form).pack(fill=tk.X, pady=(8,0))

        self.entries['name'][1].focus_set()

    def _create_statusbar(self):
        self.status_var = tk.StringVar(value="Ready")
        status = ttk.Label(self, textvariable=self.status_var, anchor=tk.W, relief=tk.SUNKEN)
        status.pack(side=tk.BOTTOM, fill=tk.X)

    def _set_status(self, text, timeout_ms=None):
        self.status_var.set(text)
        if timeout_ms:
            self.after(timeout_ms, lambda: self.status_var.set("Ready"))

    def _clear_search(self):
        self.search_var.set("")
        self.refresh_tree()

    def _on_heading_click(self, col):
        if self._sort_column == col:
            self._sort_reverse = not self._sort_reverse
        else:
            self._sort_column = col
            self._sort_reverse = False
        self.refresh_tree()
        self._set_status(f"Sorting by '{col}' {'descending' if self._sort_reverse else 'ascending'}", 3000)

    def _on_tree_select(self, event):
        sel = self.tree.selection()
        if not sel:
            return
        iid = sel[0]
        item = self.tree.item(iid)['values']
        mapping = dict(zip(['id','name','category','quantity','price','location'], item))
        for k in ['id','name','category','quantity','price','location']:
            var, ent = self.entries[k]
            var.set(str(mapping.get(k,'')))
        self._set_status(f"Selected: {mapping.get('name','')}", 3000)

    def add_item(self):
        values, valid = self._read_form(validate=True)
        if not valid:
            return
        if not values['id']:
            values['id'] = str(uuid.uuid4())[:8]
        else:
            if any(d['id'] == values['id'] for d in self.data):
                self._set_status("ID already exists", 5000)
                self._highlight_field('id')
                return
        values['created_at'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.data.append(values)
        self.refresh_tree()
        self.clear_form()
        self._set_status("Record added", 4000)

    def update_item(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showinfo("Update", "Select a record in the table to update.")
            return
        iid = sel[0]
        old_values = self.tree.item(iid)['values']
        old_id = str(old_values[0])
        values, valid = self._read_form(validate=True)
        if not valid:
            return
        if values['id'] != old_id and any(d['id'] == values['id'] for d in self.data):
            self._set_status("ID already exists", 5000)
            self._highlight_field('id')
            return
        for d in self.data:
            if d['id'] == old_id:
                d.update(values)
                break
        self.refresh_tree()
        self._set_status("Record updated", 4000)

    def delete_item(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showinfo("Delete", "Select a record in the table to delete.")
            return
        if not messagebox.askyesno("Confirmation", "Are you sure you want to delete the selected record?"):
            return
        iid = sel[0]
        vals = self.tree.item(iid)['values']
        del_id = str(vals[0])
        self.data = [d for d in self.data if d['id'] != del_id]
        self.refresh_tree()
        self.clear_form()
        self._set_status("Record deleted", 4000)

    def clear_form(self):
        for var, ent in self.entries.values():
            var.set("")
            ent.configure(background='white')
        self._set_status("Form cleared", 2000)

    def _highlight_field(self, key):
        if key in self.entries:
            var, ent = self.entries[key]
            ent.configure(background='#ffcccc')
            self.after(2000, lambda: ent.configure(background='white'))

    def _read_form(self, validate=False):
       
        res = {}
        valid = True
        for _, ent in self.entries.values():
            ent.configure(background='white')

        idv = self.entries['id'][0].get().strip()
        res['id'] = idv

        name = self.entries['name'][0].get().strip()
        if validate and not name:
            self._set_status("Error: name cannot be empty", 5000)
            self._highlight_field('name')
            valid = False
        res['name'] = name

        cat = self.entries['category'][0].get().strip()
        if validate and not cat:
            self._set_status("Error: category cannot be empty", 5000)
            self._highlight_field('category')
            valid = False
        res['category'] = cat

        qraw = self.entries['quantity'][0].get().strip()
        if qraw == '':
            q = 0
        else:
            try:
                q = int(float(qraw))
                if q < 0:
                    raise ValueError()
            except Exception:
                if validate:
                    self._set_status("Error: quantity must be an integer ≥ 0", 5000)
                    self._highlight_field('quantity')
                    valid = False
                q = 0
        res['quantity'] = q

        praw = self.entries['price'][0].get().strip().replace(',', '.')
        if praw == '':
            p = 0.0
        else:
            try:
                p = float(praw)
                if p < 0:
                    raise ValueError()
            except Exception:
                if validate:
                    self._set_status("Error: price must be a number ≥ 0", 5000)
                    self._highlight_field('price')
                    valid = False
                p = 0.0
        res['price'] = round(p, 2)

        
        loc = self.entries['location'][0].get().strip()
        res['location'] = loc

        return res, valid

    def refresh_tree(self):
        for r in self.tree.get_children():
            self.tree.delete(r)
        q = self.search_var.get().strip().lower()
        rows = list(self.data)
        if q:
            rows = [r for r in rows if (q in r['name'].lower()) or (q in r['category'].lower())]
        if self._sort_column:
            key = self._sort_column
            def sort_key(x):
                v = x.get(key)
                if key in ('quantity', 'price'):
                    try:
                        return float(v)
                    except Exception:
                        return 0
                return str(v).lower()
            rows.sort(key=sort_key, reverse=self._sort_reverse)
        for r in rows:
            vals = (r.get('id',''), r.get('name',''), r.get('category',''), r.get('quantity',0), r.get('price',0.0), r.get('location',''))
            self.tree.insert('', tk.END, values=vals)

    def load_csv(self):
        path = filedialog.askopenfilename(filetypes=[("CSV files","*.csv"),("All files","*.*")])
        if not path:
            return
        try:
            with open(path, newline='', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                headers = [h.strip() for h in reader.fieldnames] if reader.fieldnames else []
                if not headers or any(h not in CSV_HEADERS for h in headers):
                    missing = [h for h in CSV_HEADERS if h not in headers]
                    if missing:
                        messagebox.showerror("Error", f"CSV does not contain required columns: {', '.join(missing)}")
                        return
                newdata = []
                for row in reader:
                    entry = {}
                    entry['id'] = row.get('id','').strip() or str(uuid.uuid4())[:8]
                    entry['name'] = row.get('name','').strip()
                    entry['category'] = row.get('category','').strip()
                    try:
                        entry['quantity'] = int(float(row.get('quantity',0) or 0))
                        if entry['quantity'] < 0:
                            entry['quantity'] = 0
                    except Exception:
                        entry['quantity'] = 0
                    try:
                        p = str(row.get('price','0')).strip().replace(',','.')
                        entry['price'] = round(float(p or 0.0), 2)
                        if entry['price'] < 0:
                            entry['price'] = 0.0
                    except Exception:
                        entry['price'] = 0.0
                    entry['location'] = row.get('location','').strip()
                    entry['created_at'] = row.get('created_at') or datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    newdata.append(entry)
            self.data = newdata
            self.current_file = path
            self.refresh_tree()
            self._set_status(f"Loaded from {path}", 4000)
        except Exception as e:
            messagebox.showerror("Error opening CSV", str(e))

    def save_csv(self):
        if not self.current_file:
            return self.save_csv_as()
        return self._write_csv(self.current_file)

    def save_csv_as(self):
        path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files","*.csv"),("All files","*.*")])
        if not path:
            return
        self.current_file = path
        return self._write_csv(path)

    def _write_csv(self, path):
        try:
            with open(path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=CSV_HEADERS)
                writer.writeheader()
                for r in self.data:
                    row = {k: r.get(k,'') for k in CSV_HEADERS}
                    if not row.get('created_at'):
                        row['created_at'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    writer.writerow(row)
            self._set_status(f"Saved to {path}", 4000)
            return True
        except Exception as e:
            messagebox.showerror("Error saving CSV", str(e))
            return False


def main():
    app = InventoryApp()
    app.mainloop()


if __name__ == "__main__":
    main()