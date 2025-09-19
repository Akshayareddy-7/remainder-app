import tkinter as tk
from tkinter import messagebox
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from ttkbootstrap.toast import ToastNotification
import json
import os
from datetime import datetime, timedelta
import threading
import time
import sys

# For system notifications
try:
    from plyer import notification
    NOTIFICATIONS_AVAILABLE = True
except ImportError:
    NOTIFICATIONS_AVAILABLE = False
    print("Install 'plyer' for system notifications: pip install plyer")

class ReminderApp:
    def __init__(self):
        # Create main window with modern theme
        self.root = ttk.Window(themename="cosmo")  # Dark modern theme
        self.root.title("🔔 Personal Reminder Manager")
        self.root.geometry("800x600")
        self.root.resizable(True, True)
        
        # Set minimum window size
        self.root.minsize(600, 500)
        
        # Data file for storing reminders
        self.data_file = "reminders.json"
        self.reminders = self.load_reminders()
        
        # Create GUI
        self.create_widgets()
        
        # Start the reminder checker thread
        self.running = True
        self.checker_thread = threading.Thread(target=self.check_reminders, daemon=True)
        self.checker_thread.start()
        
        # Handle window close
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # Refresh the display
        self.refresh_reminder_list()
    
    def create_widgets(self):
        # Main container with padding
        main_frame = ttk.Frame(self.root, padding=20)
        main_frame.pack(fill=BOTH, expand=True)
        
        # Header section
        header_frame = ttk.Frame(main_frame)
        header_frame.pack(fill=X, pady=(0, 20))
        
        # App title with icon
        title_label = ttk.Label(
            header_frame, 
            text="🔔 Personal Reminder Manager", 
            font=("Segoe UI", 24, "bold"),
            bootstyle="primary"
        )
        title_label.pack(anchor=W)
        
        # Subtitle
        subtitle_label = ttk.Label(
            header_frame, 
            text="Never forget important tasks again", 
            font=("Segoe UI", 11),
            bootstyle="secondary"
        )
        subtitle_label.pack(anchor=W, pady=(5, 0))
        
        # Add reminder section
        add_frame = ttk.LabelFrame(
            main_frame, 
            text="➕ Add New Reminder", 
            padding=20,
            bootstyle="info"
        )
        add_frame.pack(fill=X, pady=(0, 20))
        
        # Input grid
        input_frame = ttk.Frame(add_frame)
        input_frame.pack(fill=X)
        
        # Configure grid weights
        input_frame.columnconfigure(1, weight=1)
        
        # Reminder message
        ttk.Label(input_frame, text="📝 Message:", font=("Segoe UI", 10, "bold")).grid(
            row=0, column=0, sticky=W, padx=(0, 15), pady=(0, 10)
        )
        self.message_entry = ttk.Entry(
            input_frame, 
            font=("Segoe UI", 10),
            bootstyle="primary"
        )
        self.message_entry.grid(row=0, column=1, sticky=(W, E), pady=(0, 10))
        
        # Date and time container
        datetime_frame = ttk.Frame(input_frame)
        datetime_frame.grid(row=1, column=0, columnspan=2, sticky=(W, E), pady=(0, 15))
        
        # Date input
        ttk.Label(datetime_frame, text="📅 Date:", font=("Segoe UI", 10, "bold")).pack(
            side=LEFT, padx=(0, 10)
        )
        self.date_entry = ttk.Entry(
            datetime_frame, 
            width=12,
            font=("Segoe UI", 10),
            bootstyle="success"
        )
        self.date_entry.pack(side=LEFT, padx=(0, 20))
        self.date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))
        
        # Time input
        ttk.Label(datetime_frame, text="⏰ Time:", font=("Segoe UI", 10, "bold")).pack(
            side=LEFT, padx=(0, 10)
        )
        self.time_entry = ttk.Entry(
            datetime_frame, 
            width=8,
            font=("Segoe UI", 10),
            bootstyle="success"
        )
        self.time_entry.pack(side=LEFT, padx=(0, 20))
        self.time_entry.insert(0, (datetime.now() + timedelta(minutes=5)).strftime("%H:%M"))
        
        # Add button
        add_btn = ttk.Button(
            datetime_frame, 
            text="✅ Add Reminder", 
            command=self.add_reminder,
            bootstyle="success-outline",
            width=15
        )
        add_btn.pack(side=RIGHT)
        
        # Format info
        info_label = ttk.Label(
            add_frame, 
            text="💡 Format: Date (YYYY-MM-DD), Time (HH:MM - 24 hour format)", 
            font=("Segoe UI", 9),
            bootstyle="secondary"
        )
        info_label.pack(anchor=W, pady=(10, 0))
        
        # Reminder list section
        list_frame = ttk.LabelFrame(
            main_frame, 
            text="📋 Active Reminders", 
            padding=20,
            bootstyle="warning"
        )
        list_frame.pack(fill=BOTH, expand=True, pady=(0, 20))
        
        # Treeview container
        tree_frame = ttk.Frame(list_frame)
        tree_frame.pack(fill=BOTH, expand=True)
        
        # Treeview for reminders
        columns = ("ID", "Message", "Date", "Time", "Status")
        self.tree = ttk.Treeview(
            tree_frame, 
            columns=columns, 
            show="headings", 
            height=12,
            bootstyle="primary"
        )
        
        # Define column headings and widths
        self.tree.heading("ID", text="ID")
        self.tree.heading("Message", text="📝 Message")
        self.tree.heading("Date", text="📅 Date")
        self.tree.heading("Time", text="⏰ Time")
        self.tree.heading("Status", text="📊 Status")
        
        self.tree.column("ID", width=60, minwidth=50)
        self.tree.column("Message", width=300, minwidth=200)
        self.tree.column("Date", width=120, minwidth=100)
        self.tree.column("Time", width=100, minwidth=80)
        self.tree.column("Status", width=100, minwidth=80)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(
            tree_frame, 
            orient=VERTICAL, 
            command=self.tree.yview,
            bootstyle="primary-round"
        )
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side=LEFT, fill=BOTH, expand=True)
        scrollbar.pack(side=RIGHT, fill=Y)
        
        # Buttons frame
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill=X, pady=(0, 10))
        
        # Control buttons
        delete_btn = ttk.Button(
            btn_frame, 
            text="🗑️ Delete Selected", 
            command=self.delete_reminder,
            bootstyle="danger-outline",
            width=18
        )
        delete_btn.pack(side=LEFT, padx=(0, 15))
        
        refresh_btn = ttk.Button(
            btn_frame, 
            text="🔄 Refresh", 
            command=self.refresh_reminder_list,
            bootstyle="info-outline",
            width=12
        )
        refresh_btn.pack(side=LEFT, padx=(0, 15))
        
        # Quick add buttons
        quick_frame = ttk.Frame(btn_frame)
        quick_frame.pack(side=RIGHT)
        
        ttk.Button(
            quick_frame, 
            text="⚡ +5 min", 
            command=lambda: self.quick_add_minutes(5),
            bootstyle="secondary-outline",
            width=10
        ).pack(side=LEFT, padx=(0, 5))
        
        ttk.Button(
            quick_frame, 
            text="⚡ +1 hour", 
            command=lambda: self.quick_add_minutes(60),
            bootstyle="secondary-outline",
            width=10
        ).pack(side=LEFT, padx=(0, 5))
        
        ttk.Button(
            quick_frame, 
            text="⚡ +1 day", 
            command=lambda: self.quick_add_minutes(1440),
            bootstyle="secondary-outline",
            width=10
        ).pack(side=LEFT)
        
        # Status bar
        status_frame = ttk.Frame(main_frame)
        status_frame.pack(fill=X)
        
        self.status_label = ttk.Label(
            status_frame, 
            text="✅ Ready", 
            font=("Segoe UI", 10),
            bootstyle="success"
        )
        self.status_label.pack(side=LEFT)
        
        # Reminder count
        self.count_label = ttk.Label(
            status_frame, 
            text="", 
            font=("Segoe UI", 10),
            bootstyle="info"
        )
        self.count_label.pack(side=RIGHT)
        
        # Bind Enter key to add reminder
        self.root.bind('<Return>', lambda e: self.add_reminder())
        
        # Bind double-click to edit (placeholder for future feature)
        self.tree.bind('<Double-1>', self.on_item_double_click)
    
    def quick_add_minutes(self, minutes):
        """Quick add time buttons"""
        new_time = datetime.now() + timedelta(minutes=minutes)
        self.date_entry.delete(0, tk.END)
        self.date_entry.insert(0, new_time.strftime("%Y-%m-%d"))
        self.time_entry.delete(0, tk.END)
        self.time_entry.insert(0, new_time.strftime("%H:%M"))
    
    def on_item_double_click(self, event):
        """Handle double-click on treeview item"""
        selected_item = self.tree.selection()
        if selected_item:
            item_values = self.tree.item(selected_item[0])['values']
            message = item_values[1]
            # Future: Open edit dialog
            self.show_toast(f"📝 Edit feature coming soon for: {message[:30]}...", "info")
    
    def load_reminders(self):
        """Load reminders from JSON file"""
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r') as f:
                    return json.load(f)
            except:
                return []
        return []
    
    def save_reminders(self):
        """Save reminders to JSON file"""
        with open(self.data_file, 'w') as f:
            json.dump(self.reminders, f, indent=2)
    
    def show_toast(self, message, style="success"):
        """Show toast notification"""
        toast = ToastNotification(
            title="Reminder Manager",
            message=message,
            duration=3000,
            bootstyle=style
        )
        toast.show_toast()
    
    def add_reminder(self):
        """Add a new reminder"""
        message = self.message_entry.get().strip()
        date_str = self.date_entry.get().strip()
        time_str = self.time_entry.get().strip()
        
        if not message:
            self.show_toast("❌ Please enter a reminder message", "danger")
            return
        
        try:
            # Parse date and time
            reminder_datetime = datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M")
            
            # Check if the datetime is in the future
            if reminder_datetime <= datetime.now():
                self.show_toast("⚠️ Reminder time must be in the future", "warning")
                return
            
            # Create reminder object
            reminder = {
                "id": len(self.reminders) + 1,
                "message": message,
                "datetime": reminder_datetime.strftime("%Y-%m-%d %H:%M"),
                "status": "Active",
                "notified": False
            }
            
            self.reminders.append(reminder)
            self.save_reminders()
            self.refresh_reminder_list()
            
            # Clear input fields
            self.message_entry.delete(0, tk.END)
            self.time_entry.delete(0, tk.END)
            self.time_entry.insert(0, (datetime.now() + timedelta(minutes=5)).strftime("%H:%M"))
            
            # Show success toast
            time_diff = reminder_datetime - datetime.now()
            days = time_diff.days
            hours, remainder = divmod(time_diff.seconds, 3600)
            minutes, _ = divmod(remainder, 60)
            
            if days > 0:
                time_str = f"{days} day{'s' if days > 1 else ''}"
            elif hours > 0:
                time_str = f"{hours} hour{'s' if hours > 1 else ''}"
            else:
                time_str = f"{minutes} minute{'s' if minutes > 1 else ''}"
            
            self.show_toast(f"✅ Reminder added! Due in {time_str}", "success")
            
        except ValueError:
            self.show_toast("❌ Invalid date or time format", "danger")
    
    def delete_reminder(self):
        """Delete selected reminder"""
        selected_item = self.tree.selection()
        if not selected_item:
            self.show_toast("⚠️ Please select a reminder to delete", "warning")
            return
        
        # Get the ID of the selected reminder
        item_values = self.tree.item(selected_item[0])['values']
        reminder_id = item_values[0]
        message = item_values[1]
        
        # Confirm deletion
        if messagebox.askyesno("Confirm Delete", f"Delete reminder:\n\n'{message}'?"):
            # Remove reminder from list
            self.reminders = [r for r in self.reminders if r['id'] != reminder_id]
            self.save_reminders()
            self.refresh_reminder_list()
            
            self.show_toast("🗑️ Reminder deleted", "info")
    
    def refresh_reminder_list(self):
        """Refresh the reminder list display"""
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Add current reminders
        active_count = 0
        for reminder in self.reminders:
            if reminder['status'] == 'Active':
                active_count += 1
                datetime_obj = datetime.strptime(reminder['datetime'], "%Y-%m-%d %H:%M")
                date_str = datetime_obj.strftime("%Y-%m-%d")
                time_str = datetime_obj.strftime("%H:%M")
                
                # Check if reminder is overdue
                status = reminder['status']
                if datetime_obj < datetime.now():
                    status = "⚠️ Overdue"
                
                self.tree.insert('', 'end', values=(
                    reminder['id'],
                    reminder['message'],
                    date_str,
                    time_str,
                    status
                ))
        
        # Update count label
        self.count_label.config(text=f"📊 {active_count} active reminder{'s' if active_count != 1 else ''}")
    
    def check_reminders(self):
        """Background thread to check for due reminders"""
        while self.running:
            current_time = datetime.now()
            
            for reminder in self.reminders:
                if reminder['status'] == 'Active' and not reminder['notified']:
                    reminder_time = datetime.strptime(reminder['datetime'], "%Y-%m-%d %H:%M")
                    
                    if current_time >= reminder_time:
                        self.show_notification(reminder)
                        reminder['notified'] = True
                        reminder['status'] = 'Completed'
                        self.save_reminders()
                        
                        # Update GUI in main thread
                        self.root.after(0, self.refresh_reminder_list)
            
            time.sleep(30)  # Check every 30 seconds
    
    def show_notification(self, reminder):
        """Show system notification"""
        title = "🔔 Reminder Alert!"
        message = reminder['message']
        
        if NOTIFICATIONS_AVAILABLE:
            try:
                notification.notify(
                    title=title,
                    message=message,
                    timeout=10,
                    app_name="Personal Reminder"
                )
            except:
                pass  # Fallback to messagebox if notification fails
        
        # Also show a popup dialog
        self.root.after(0, lambda: messagebox.showinfo(title, f"🔔 {message}"))
        
        # Show toast notification
        self.root.after(0, lambda: self.show_toast(f"🔔 {message}", "warning"))
    
    def on_closing(self):
        """Handle application closing"""
        self.running = False
        self.root.destroy()
    
    def run(self):
        """Start the application"""
        self.root.mainloop()

def main():
    try:
        app = ReminderApp()
        app.run()
    except Exception as e:
        print(f"Error starting application: {e}")
        print("Make sure you have ttkbootstrap installed: pip install ttkbootstrap")

if __name__ == "__main__":
    main()