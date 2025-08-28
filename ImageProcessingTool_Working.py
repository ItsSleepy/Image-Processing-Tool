import tkinter as tk
from tkinter import ttk, filedialog, messagebox, colorchooser
from PIL import Image, ImageTk, ImageFilter, ImageEnhance, ImageDraw, ImageFont, ImageOps
import os
import numpy as np
import threading
from datetime import datetime
from collections import deque
import json

class AdvancedImageProcessor:
    def __init__(self, root):
        self.root = root
        self.root.title("🚀 Advanced Image Processing Studio")
        self.root.geometry("1400x900")
        self.root.configure(bg='#0d1117')
        
        # Variables
        self.current_image = None
        self.original_image = None
        self.image_path = None
        self.preview_size = (500, 400)
        self.history = deque(maxlen=20)
        self.history_index = -1
        self.zoom_factor = 1.0
        
        # Colors
        self.colors = {
            'bg_dark': '#0d1117',
            'bg_medium': '#161b22',
            'bg_light': '#21262d',
            'accent': '#58a6ff',
            'accent_hover': '#1f6feb',
            'text_primary': '#f0f6fc',
            'text_secondary': '#8b949e',
            'success': '#56d364',
            'warning': '#e3b341',
            'error': '#f85149'
        }
        
        self.setup_styles()
        self.create_widgets()
        self.create_menu()
        
        # Session stats
        self.session_stats = {
            'images_processed': 0,
            'operations_performed': 0,
            'session_start': datetime.now()
        }
        
    def setup_styles(self):
        """Configure styles"""
        style = ttk.Style()
        style.theme_use('clam')
        
        style.configure('Custom.TButton',
                       background=self.colors['accent'],
                       foreground='white',
                       padding=(12, 6),
                       font=('Segoe UI', 9, 'bold'))
        
        style.map('Custom.TButton',
                 background=[('active', self.colors['accent_hover'])])
        
        style.configure('Success.TButton',
                       background=self.colors['success'],
                       foreground='white',
                       padding=(12, 6))
        
        style.configure('Warning.TButton',
                       background=self.colors['warning'],
                       foreground='black',
                       padding=(12, 6))
        
        style.configure('Error.TButton',
                       background=self.colors['error'],
                       foreground='white',
                       padding=(12, 6))
        
        style.configure('Custom.TNotebook',
                       background=self.colors['bg_medium'])
        style.configure('Custom.TNotebook.Tab',
                       background=self.colors['bg_light'],
                       foreground=self.colors['text_secondary'],
                       padding=(15, 8))
        style.map('Custom.TNotebook.Tab',
                 background=[('selected', self.colors['accent'])])
    
    def create_menu(self):
        """Create menu bar"""
        menubar = tk.Menu(self.root, bg=self.colors['bg_dark'], fg=self.colors['text_primary'])
        self.root.config(menu=menubar)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0, bg=self.colors['bg_medium'], fg=self.colors['text_primary'])
        menubar.add_cascade(label="📁 File", menu=file_menu)
        file_menu.add_command(label="Open Image", command=self.open_image, accelerator="Ctrl+O")
        file_menu.add_command(label="Save Image", command=self.save_image, accelerator="Ctrl+S")
        file_menu.add_command(label="Export All Formats", command=self.export_all_formats)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        
        # Edit menu
        edit_menu = tk.Menu(menubar, tearoff=0, bg=self.colors['bg_medium'], fg=self.colors['text_primary'])
        menubar.add_cascade(label="✏️ Edit", menu=edit_menu)
        edit_menu.add_command(label="Undo", command=self.undo, accelerator="Ctrl+Z")
        edit_menu.add_command(label="Redo", command=self.redo, accelerator="Ctrl+Y")
        edit_menu.add_command(label="Reset", command=self.reset_image, accelerator="Ctrl+R")
        
        # Tools menu
        tools_menu = tk.Menu(menubar, tearoff=0, bg=self.colors['bg_medium'], fg=self.colors['text_primary'])
        menubar.add_cascade(label="🛠️ Tools", menu=tools_menu)
        tools_menu.add_command(label="Auto Enhance", command=self.auto_enhance)
        tools_menu.add_command(label="Batch Process", command=self.batch_process)
        tools_menu.add_command(label="Session Stats", command=self.show_session_stats)
        
        # Bind shortcuts
        self.root.bind('<Control-o>', lambda e: self.open_image())
        self.root.bind('<Control-s>', lambda e: self.save_image())
        self.root.bind('<Control-z>', lambda e: self.undo())
        self.root.bind('<Control-y>', lambda e: self.redo())
        self.root.bind('<Control-r>', lambda e: self.reset_image())
    
    def create_widgets(self):
        """Create main interface"""
        # Title
        title_frame = tk.Frame(self.root, bg=self.colors['bg_dark'], height=70)
        title_frame.pack(fill=tk.X)
        title_frame.pack_propagate(False)
        
        title_label = tk.Label(title_frame, 
                              text="🚀 Advanced Image Processing Studio",
                              bg=self.colors['bg_dark'], 
                              fg=self.colors['text_primary'],
                              font=('Segoe UI', 20, 'bold'))
        title_label.pack(pady=20)
        
        # Main content
        main_frame = tk.Frame(self.root, bg=self.colors['bg_dark'])
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Paned window
        paned = tk.PanedWindow(main_frame, orient=tk.HORIZONTAL, 
                              bg=self.colors['bg_dark'], sashwidth=5)
        paned.pack(fill=tk.BOTH, expand=True)
        
        # Left panel - Controls
        left_panel = tk.Frame(paned, bg=self.colors['bg_medium'], width=400)
        # Right panel - Image
        right_panel = tk.Frame(paned, bg=self.colors['bg_medium'])
        
        paned.add(left_panel, minsize=350)
        paned.add(right_panel, minsize=500)
        
        self.create_control_panel(left_panel)
        self.create_image_panel(right_panel)
        
        # Status bar
        self.status_frame = tk.Frame(self.root, bg=self.colors['bg_medium'], height=30)
        self.status_frame.pack(fill=tk.X, side=tk.BOTTOM)
        self.status_frame.pack_propagate(False)
        
        self.status_label = tk.Label(self.status_frame, text="Ready for image processing",
                                   bg=self.colors['bg_medium'], fg=self.colors['text_secondary'],
                                   font=('Segoe UI', 10))
        self.status_label.pack(side=tk.LEFT, padx=10, pady=5)
        
        self.image_info_label = tk.Label(self.status_frame, text="No image loaded",
                                       bg=self.colors['bg_medium'], fg=self.colors['accent'],
                                       font=('Segoe UI', 10))
        self.image_info_label.pack(side=tk.RIGHT, padx=10, pady=5)
    
    def create_control_panel(self, parent):
        """Create control panel with tabs"""
        notebook = ttk.Notebook(parent, style='Custom.TNotebook')
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Basic tab
        basic_tab = tk.Frame(notebook, bg=self.colors['bg_medium'])
        notebook.add(basic_tab, text="  🎛️ Basic  ")
        
        # Filters tab
        filters_tab = tk.Frame(notebook, bg=self.colors['bg_medium'])
        notebook.add(filters_tab, text="  🎭 Filters  ")
        
        # Advanced tab
        advanced_tab = tk.Frame(notebook, bg=self.colors['bg_medium'])
        notebook.add(advanced_tab, text="  ⚡ Advanced  ")
        
        # Tools tab
        tools_tab = tk.Frame(notebook, bg=self.colors['bg_medium'])
        notebook.add(tools_tab, text="  🛠️ Tools  ")
        
        self.create_basic_controls(basic_tab)
        self.create_filter_controls(filters_tab)
        self.create_advanced_controls(advanced_tab)
        self.create_tool_controls(tools_tab)
    
    def create_basic_controls(self, parent):
        """Create basic adjustment controls"""
        # File operations
        file_frame = tk.LabelFrame(parent, text="📁 File Operations",
                                  bg=self.colors['bg_medium'], fg=self.colors['text_primary'],
                                  font=('Segoe UI', 10, 'bold'))
        file_frame.pack(fill=tk.X, padx=10, pady=5)
        
        btn_frame = tk.Frame(file_frame, bg=self.colors['bg_medium'])
        btn_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(btn_frame, text="📂 Open", command=self.open_image, 
                  style='Custom.TButton', width=10).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_frame, text="💾 Save", command=self.save_image,
                  style='Custom.TButton', width=10).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_frame, text="🔄 Reset", command=self.reset_image,
                  style='Error.TButton', width=10).pack(side=tk.LEFT, padx=2)
        
        # History controls
        history_frame = tk.Frame(file_frame, bg=self.colors['bg_medium'])
        history_frame.pack(fill=tk.X, padx=5, pady=2)
        
        ttk.Button(history_frame, text="↶ Undo", command=self.undo,
                  style='Custom.TButton', width=15).pack(side=tk.LEFT, padx=2)
        ttk.Button(history_frame, text="↷ Redo", command=self.redo,
                  style='Custom.TButton', width=15).pack(side=tk.LEFT, padx=2)
        
        # Adjustments
        adj_frame = tk.LabelFrame(parent, text="🎛️ Adjustments",
                                 bg=self.colors['bg_medium'], fg=self.colors['text_primary'],
                                 font=('Segoe UI', 10, 'bold'))
        adj_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Brightness
        self.create_slider(adj_frame, "☀️ Brightness", 0.1, 3.0, 1.0, 'brightness_var')
        
        # Contrast
        self.create_slider(adj_frame, "🌗 Contrast", 0.1, 3.0, 1.0, 'contrast_var')
        
        # Saturation
        self.create_slider(adj_frame, "🎨 Saturation", 0.0, 3.0, 1.0, 'saturation_var')
        
        # Apply button
        ttk.Button(adj_frame, text="✨ Apply Adjustments", command=self.apply_adjustments,
                  style='Success.TButton').pack(fill=tk.X, padx=5, pady=10)
        
        # Transform controls
        transform_frame = tk.LabelFrame(parent, text="📐 Transform",
                                      bg=self.colors['bg_medium'], fg=self.colors['text_primary'],
                                      font=('Segoe UI', 10, 'bold'))
        transform_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Size inputs
        size_frame = tk.Frame(transform_frame, bg=self.colors['bg_medium'])
        size_frame.pack(fill=tk.X, padx=5, pady=5)
        
        tk.Label(size_frame, text="Width:", bg=self.colors['bg_medium'], 
                fg=self.colors['text_primary']).pack(side=tk.LEFT)
        self.width_var = tk.StringVar()
        tk.Entry(size_frame, textvariable=self.width_var, width=8,
                bg=self.colors['bg_light'], fg=self.colors['text_primary']).pack(side=tk.LEFT, padx=5)
        
        tk.Label(size_frame, text="Height:", bg=self.colors['bg_medium'], 
                fg=self.colors['text_primary']).pack(side=tk.LEFT, padx=(10,0))
        self.height_var = tk.StringVar()
        tk.Entry(size_frame, textvariable=self.height_var, width=8,
                bg=self.colors['bg_light'], fg=self.colors['text_primary']).pack(side=tk.LEFT, padx=5)
        
        # Transform buttons
        transform_btn_frame = tk.Frame(transform_frame, bg=self.colors['bg_medium'])
        transform_btn_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(transform_btn_frame, text="📐 Resize", command=self.resize_image,
                  style='Custom.TButton', width=8).pack(side=tk.LEFT, padx=2)
        ttk.Button(transform_btn_frame, text="↰ 90°", command=lambda: self.rotate_image(90),
                  style='Custom.TButton', width=6).pack(side=tk.LEFT, padx=2)
        ttk.Button(transform_btn_frame, text="↱ -90°", command=lambda: self.rotate_image(-90),
                  style='Custom.TButton', width=6).pack(side=tk.LEFT, padx=2)
        ttk.Button(transform_btn_frame, text="🔄 Flip", command=self.flip_horizontal,
                  style='Custom.TButton', width=6).pack(side=tk.LEFT, padx=2)
    
    def create_slider(self, parent, label, min_val, max_val, default, var_name):
        """Create a labeled slider"""
        frame = tk.Frame(parent, bg=self.colors['bg_medium'])
        frame.pack(fill=tk.X, padx=5, pady=2)
        
        tk.Label(frame, text=label, bg=self.colors['bg_medium'], 
                fg=self.colors['text_primary'], font=('Segoe UI', 9)).pack(anchor=tk.W)
        
        var = tk.DoubleVar(value=default)
        setattr(self, var_name, var)
        
        value_label = tk.Label(frame, text=f"{default:.1f}",
                             bg=self.colors['bg_medium'], fg=self.colors['accent'],
                             font=('Segoe UI', 8))
        value_label.pack(anchor=tk.E)
        
        def update_label(value):
            value_label.config(text=f"{float(value):.1f}")
        
        scale = tk.Scale(frame, from_=min_val, to=max_val, resolution=0.1,
                        orient=tk.HORIZONTAL, variable=var, command=update_label,
                        bg=self.colors['bg_light'], fg=self.colors['text_primary'],
                        troughcolor=self.colors['bg_dark'], highlightthickness=0)
        scale.pack(fill=tk.X, pady=2)
    
    def create_filter_controls(self, parent):
        """Create filter controls"""
        # Quick filters
        quick_frame = tk.LabelFrame(parent, text="⚡ Quick Filters",
                                   bg=self.colors['bg_medium'], fg=self.colors['text_primary'],
                                   font=('Segoe UI', 10, 'bold'))
        quick_frame.pack(fill=tk.X, padx=10, pady=5)
        
        filters_grid = tk.Frame(quick_frame, bg=self.colors['bg_medium'])
        filters_grid.pack(fill=tk.X, padx=5, pady=5)
        
        filters = [
            ("🌟 Blur", self.apply_blur),
            ("✨ Sharpen", self.apply_sharpen),
            ("🔍 Edge", self.apply_edge_enhance),
            ("🎪 Emboss", self.apply_emboss),
            ("📺 Grayscale", self.apply_grayscale),
            ("🌈 Sepia", self.apply_sepia)
        ]
        
        for i, (text, command) in enumerate(filters):
            row = i // 2
            col = i % 2
            ttk.Button(filters_grid, text=text, command=command,
                      style='Custom.TButton', width=15).grid(row=row, column=col, padx=2, pady=2)
        
        # Artistic filters
        artistic_frame = tk.LabelFrame(parent, text="🎨 Artistic Effects",
                                     bg=self.colors['bg_medium'], fg=self.colors['text_primary'],
                                     font=('Segoe UI', 10, 'bold'))
        artistic_frame.pack(fill=tk.X, padx=10, pady=5)
        
        artistic_grid = tk.Frame(artistic_frame, bg=self.colors['bg_medium'])
        artistic_grid.pack(fill=tk.X, padx=5, pady=5)
        
        artistic = [
            ("🖼️ Oil Paint", self.apply_oil_painting),
            ("📰 Posterize", self.apply_posterize),
            ("🌈 Psychedelic", self.apply_psychedelic),
            ("🎭 Vintage", self.apply_vintage)
        ]
        
        for i, (text, command) in enumerate(artistic):
            row = i // 2
            col = i % 2
            ttk.Button(artistic_grid, text=text, command=command,
                      style='Custom.TButton', width=15).grid(row=row, column=col, padx=2, pady=2)
    
    def create_advanced_controls(self, parent):
        """Create advanced controls"""
        # Color adjustments
        color_frame = tk.LabelFrame(parent, text="🌈 Color Effects",
                                   bg=self.colors['bg_medium'], fg=self.colors['text_primary'],
                                   font=('Segoe UI', 10, 'bold'))
        color_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.create_slider(color_frame, "🌡️ Temperature", -100, 100, 0, 'temperature_var')
        
        ttk.Button(color_frame, text="🌡️ Apply Temperature", command=self.apply_temperature,
                  style='Custom.TButton').pack(fill=tk.X, padx=5, pady=5)
        
        # Advanced processing
        advanced_frame = tk.LabelFrame(parent, text="⚡ Advanced Processing",
                                     bg=self.colors['bg_medium'], fg=self.colors['text_primary'],
                                     font=('Segoe UI', 10, 'bold'))
        advanced_frame.pack(fill=tk.X, padx=10, pady=5)
        
        advanced_buttons = [
            ("🧹 Denoise", self.apply_denoise),
            ("📊 Histogram Eq", self.histogram_equalization),
            ("🎯 Auto Enhance", self.auto_enhance),
            ("🔍 Unsharp Mask", self.apply_unsharp_mask)
        ]
        
        for text, command in advanced_buttons:
            ttk.Button(advanced_frame, text=text, command=command,
                      style='Custom.TButton').pack(fill=tk.X, padx=5, pady=2)
    
    def create_tool_controls(self, parent):
        """Create tool controls"""
        # Watermark
        watermark_frame = tk.LabelFrame(parent, text="💧 Watermark",
                                      bg=self.colors['bg_medium'], fg=self.colors['text_primary'],
                                      font=('Segoe UI', 10, 'bold'))
        watermark_frame.pack(fill=tk.X, padx=10, pady=5)
        
        tk.Label(watermark_frame, text="Text:", bg=self.colors['bg_medium'], 
                fg=self.colors['text_primary']).pack(anchor=tk.W, padx=5)
        self.watermark_text = tk.StringVar(value="© Your Name")
        tk.Entry(watermark_frame, textvariable=self.watermark_text,
                bg=self.colors['bg_light'], fg=self.colors['text_primary']).pack(fill=tk.X, padx=5, pady=2)
        
        position_frame = tk.Frame(watermark_frame, bg=self.colors['bg_medium'])
        position_frame.pack(fill=tk.X, padx=5, pady=2)
        
        tk.Label(position_frame, text="Position:", bg=self.colors['bg_medium'], 
                fg=self.colors['text_primary']).pack(side=tk.LEFT)
        self.watermark_position = ttk.Combobox(position_frame, 
                                             values=["bottom-right", "bottom-left", "top-right", "top-left", "center"],
                                             state="readonly", width=12)
        self.watermark_position.set("bottom-right")
        self.watermark_position.pack(side=tk.RIGHT)
        
        ttk.Button(watermark_frame, text="🏷️ Add Watermark", command=self.add_watermark,
                  style='Custom.TButton').pack(fill=tk.X, padx=5, pady=5)
        
        # Export tools
        export_frame = tk.LabelFrame(parent, text="📤 Export Tools",
                                   bg=self.colors['bg_medium'], fg=self.colors['text_primary'],
                                   font=('Segoe UI', 10, 'bold'))
        export_frame.pack(fill=tk.X, padx=10, pady=5)
        
        export_buttons = [
            ("📄 Export PNG", lambda: self.convert_format('PNG')),
            ("🖼️ Export JPEG", lambda: self.convert_format('JPEG')),
            ("🌐 Export WebP", lambda: self.convert_format('WebP')),
            ("📦 Export All", self.export_all_formats)
        ]
        
        for text, command in export_buttons:
            ttk.Button(export_frame, text=text, command=command,
                      style='Custom.TButton').pack(fill=tk.X, padx=5, pady=2)
    
    def create_image_panel(self, parent):
        """Create image display panel"""
        # Toolbar
        toolbar = tk.Frame(parent, bg=self.colors['bg_medium'], height=40)
        toolbar.pack(fill=tk.X, padx=10, pady=5)
        toolbar.pack_propagate(False)
        
        self.info_label = tk.Label(toolbar, text="📷 No image loaded",
                                  bg=self.colors['bg_medium'], fg=self.colors['text_primary'],
                                  font=('Segoe UI', 11, 'bold'))
        self.info_label.pack(side=tk.LEFT, pady=8)
        
        # Zoom controls
        zoom_frame = tk.Frame(toolbar, bg=self.colors['bg_medium'])
        zoom_frame.pack(side=tk.RIGHT, pady=5)
        
        ttk.Button(zoom_frame, text="🔍+", command=self.zoom_in, width=4).pack(side=tk.LEFT, padx=1)
        ttk.Button(zoom_frame, text="🔍-", command=self.zoom_out, width=4).pack(side=tk.LEFT, padx=1)
        ttk.Button(zoom_frame, text="📐", command=self.fit_to_window, width=4).pack(side=tk.LEFT, padx=1)
        
        # Image display
        display_frame = tk.Frame(parent, bg=self.colors['bg_dark'])
        display_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
        
        self.canvas = tk.Canvas(display_frame, bg=self.colors['bg_dark'], highlightthickness=0)
        
        v_scrollbar = ttk.Scrollbar(display_frame, orient=tk.VERTICAL, command=self.canvas.yview)
        h_scrollbar = ttk.Scrollbar(display_frame, orient=tk.HORIZONTAL, command=self.canvas.xview)
        
        self.canvas.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Placeholder
        self.image_label = tk.Label(self.canvas,
                                   text="🖼️\n\nDrop an image here\nor use 'Open Image' button\n\nSupported formats:\nJPEG, PNG, BMP, GIF, TIFF, WebP",
                                   bg=self.colors['bg_dark'], fg=self.colors['text_secondary'],
                                   font=('Segoe UI', 12), justify=tk.CENTER)
        
        self.canvas_image = self.canvas.create_window(0, 0, anchor=tk.NW, window=self.image_label)
        
        # Mouse events
        self.canvas.bind("<MouseWheel>", self.on_mousewheel)
        self.canvas.bind("<Button-1>", self.canvas_click)
        self.canvas.bind("<B1-Motion>", self.canvas_drag)
    
    # Image processing methods
    def open_image(self):
        """Open image file"""
        file_path = filedialog.askopenfilename(
            title="Select an image",
            filetypes=[
                ("All supported", "*.jpg *.jpeg *.png *.bmp *.gif *.tiff *.webp"),
                ("JPEG files", "*.jpg *.jpeg"),
                ("PNG files", "*.png"),
                ("All files", "*.*")
            ]
        )
        
        if file_path:
            try:
                self.image_path = file_path
                self.original_image = Image.open(file_path).convert('RGB')
                self.current_image = self.original_image.copy()
                
                # Update info
                width, height = self.original_image.size
                file_size = os.path.getsize(file_path) / 1024
                filename = os.path.basename(file_path)
                
                self.info_label.config(text=f"📷 {filename} | {width}×{height} | {file_size:.1f} KB")
                
                # Update size inputs
                self.width_var.set(str(width))
                self.height_var.set(str(height))
                
                # Reset adjustments
                self.brightness_var.set(1.0)
                self.contrast_var.set(1.0)
                self.saturation_var.set(1.0)
                self.temperature_var.set(0)
                self.zoom_factor = 1.0
                
                # Clear history and add initial state
                self.history.clear()
                self.history.append(self.current_image.copy())
                self.history_index = 0
                
                self.update_image_display()
                self.update_status(f"Loaded: {filename}")
                self.session_stats['images_processed'] += 1
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to open image: {str(e)}")
    
    def save_image(self):
        """Save current image"""
        if self.current_image is None:
            messagebox.showwarning("Warning", "No image to save!")
            return
        
        file_path = filedialog.asksaveasfilename(
            title="Save processed image",
            defaultextension=".png",
            filetypes=[
                ("PNG files", "*.png"),
                ("JPEG files", "*.jpg"),
                ("WebP files", "*.webp"),
                ("All files", "*.*")
            ]
        )
        
        if file_path:
            try:
                if file_path.lower().endswith(('.jpg', '.jpeg')):
                    self.current_image.save(file_path, 'JPEG', quality=95)
                else:
                    self.current_image.save(file_path)
                
                self.update_status(f"Saved: {os.path.basename(file_path)}")
                messagebox.showinfo("Success", f"Image saved successfully!\n{file_path}")
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save image: {str(e)}")
    
    def add_to_history(self):
        """Add current state to history"""
        if self.current_image:
            # Remove any redo states
            if self.history_index < len(self.history) - 1:
                for _ in range(len(self.history) - self.history_index - 1):
                    self.history.pop()
            
            self.history.append(self.current_image.copy())
            self.history_index = len(self.history) - 1
    
    def undo(self):
        """Undo last operation"""
        if self.history_index > 0:
            self.history_index -= 1
            self.current_image = self.history[self.history_index].copy()
            self.update_image_display()
            self.update_status("Undo applied")
    
    def redo(self):
        """Redo last undone operation"""
        if self.history_index < len(self.history) - 1:
            self.history_index += 1
            self.current_image = self.history[self.history_index].copy()
            self.update_image_display()
            self.update_status("Redo applied")
    
    def reset_image(self):
        """Reset to original"""
        if self.original_image and messagebox.askyesno("Reset", "Reset all changes?"):
            self.current_image = self.original_image.copy()
            self.brightness_var.set(1.0)
            self.contrast_var.set(1.0)
            self.saturation_var.set(1.0)
            self.temperature_var.set(0)
            self.zoom_factor = 1.0
            self.history.clear()
            self.history.append(self.current_image.copy())
            self.history_index = 0
            self.update_image_display()
            self.update_status("Image reset")
    
    def update_image_display(self):
        """Update image display"""
        if self.current_image:
            display_image = self.current_image.copy()
            
            # Apply zoom
            if self.zoom_factor != 1.0:
                new_width = int(display_image.width * self.zoom_factor)
                new_height = int(display_image.height * self.zoom_factor)
                display_image = display_image.resize((new_width, new_height), Image.Resampling.LANCZOS)
            
            self.photo = ImageTk.PhotoImage(display_image)
            self.canvas.delete("all")
            self.canvas.create_image(0, 0, anchor=tk.NW, image=self.photo)
            self.canvas.configure(scrollregion=self.canvas.bbox("all"))
    
    def zoom_in(self):
        """Zoom in"""
        self.zoom_factor *= 1.2
        self.update_image_display()
    
    def zoom_out(self):
        """Zoom out"""
        self.zoom_factor /= 1.2
        self.update_image_display()
    
    def fit_to_window(self):
        """Fit image to window"""
        if self.current_image:
            canvas_width = self.canvas.winfo_width()
            canvas_height = self.canvas.winfo_height()
            img_width, img_height = self.current_image.size
            
            zoom_x = canvas_width / img_width
            zoom_y = canvas_height / img_height
            self.zoom_factor = min(zoom_x, zoom_y) * 0.9
            
            self.update_image_display()
    
    def on_mousewheel(self, event):
        """Handle mouse wheel zoom"""
        if event.delta > 0:
            self.zoom_in()
        else:
            self.zoom_out()
    
    def canvas_click(self, event):
        """Handle canvas click"""
        self.canvas.scan_mark(event.x, event.y)
    
    def canvas_drag(self, event):
        """Handle canvas drag"""
        self.canvas.scan_dragto(event.x, event.y, gain=1)
    
    def process_with_progress(self, message, process_func):
        """Process with threading"""
        if self.current_image is None:
            return
        
        self.add_to_history()
        self.update_status(message)
        
        def run_process():
            try:
                result = process_func()
                if result:
                    self.current_image = result
                    self.root.after(0, self.update_image_display)
                    self.root.after(0, lambda: self.update_status("Operation completed"))
                    self.session_stats['operations_performed'] += 1
            except Exception as e:
                self.root.after(0, lambda: messagebox.showerror("Error", f"Processing failed: {str(e)}"))
        
        threading.Thread(target=run_process, daemon=True).start()
    
    def update_status(self, message):
        """Update status bar"""
        self.status_label.config(text=message)
    
    # Image processing operations
    def apply_adjustments(self):
        """Apply brightness, contrast, saturation"""
        if self.original_image is None:
            return
        
        def adjust():
            adjusted = self.original_image.copy()
            
            brightness = self.brightness_var.get()
            if brightness != 1.0:
                enhancer = ImageEnhance.Brightness(adjusted)
                adjusted = enhancer.enhance(brightness)
            
            contrast = self.contrast_var.get()
            if contrast != 1.0:
                enhancer = ImageEnhance.Contrast(adjusted)
                adjusted = enhancer.enhance(contrast)
            
            saturation = self.saturation_var.get()
            if saturation != 1.0:
                enhancer = ImageEnhance.Color(adjusted)
                adjusted = enhancer.enhance(saturation)
            
            return adjusted
        
        self.process_with_progress("Applying adjustments...", adjust)
    
    def apply_blur(self):
        """Apply blur filter"""
        if self.current_image:
            self.process_with_progress("Applying blur...", 
                                     lambda: self.current_image.filter(ImageFilter.GaussianBlur(radius=2)))
    
    def apply_sharpen(self):
        """Apply sharpen filter"""
        if self.current_image:
            self.process_with_progress("Applying sharpen...", 
                                     lambda: self.current_image.filter(ImageFilter.SHARPEN))
    
    def apply_edge_enhance(self):
        """Apply edge enhance"""
        if self.current_image:
            self.process_with_progress("Enhancing edges...", 
                                     lambda: self.current_image.filter(ImageFilter.EDGE_ENHANCE))
    
    def apply_emboss(self):
        """Apply emboss filter"""
        if self.current_image:
            self.process_with_progress("Applying emboss...", 
                                     lambda: self.current_image.filter(ImageFilter.EMBOSS))
    
    def apply_grayscale(self):
        """Convert to grayscale"""
        if self.current_image:
            self.process_with_progress("Converting to grayscale...", 
                                     lambda: self.current_image.convert('L').convert('RGB'))
    
    def apply_sepia(self):
        """Apply sepia effect"""
        if self.current_image:
            def sepia_effect():
                img_array = np.array(self.current_image)
                sepia_filter = np.array([
                    [0.393, 0.769, 0.189],
                    [0.349, 0.686, 0.168],
                    [0.272, 0.534, 0.131]
                ])
                sepia_img = img_array.dot(sepia_filter.T)
                return Image.fromarray(np.clip(sepia_img, 0, 255).astype(np.uint8))
            
            self.process_with_progress("Applying sepia...", sepia_effect)
    
    def apply_oil_painting(self):
        """Apply oil painting effect"""
        if self.current_image:
            def oil_effect():
                blurred = self.current_image.filter(ImageFilter.GaussianBlur(radius=1))
                return ImageOps.posterize(blurred, 4)
            
            self.process_with_progress("Applying oil painting...", oil_effect)
    
    def apply_posterize(self):
        """Apply posterize effect"""
        if self.current_image:
            self.process_with_progress("Applying posterize...", 
                                     lambda: ImageOps.posterize(self.current_image, 3))
    
    def apply_psychedelic(self):
        """Apply psychedelic effect"""
        if self.current_image:
            def psychedelic():
                img_array = np.array(self.current_image)
                img_array[:,:,0] = np.sin(img_array[:,:,0] * 0.02) * 127 + 128
                img_array[:,:,1] = np.cos(img_array[:,:,1] * 0.02) * 127 + 128
                img_array[:,:,2] = np.sin(img_array[:,:,2] * 0.02 + 1) * 127 + 128
                return Image.fromarray(np.clip(img_array, 0, 255).astype(np.uint8))
            
            self.process_with_progress("Applying psychedelic...", psychedelic)
    
    def apply_vintage(self):
        """Apply vintage effect"""
        if self.current_image:
            def vintage():
                # Sepia + reduced brightness + slight blur
                img_array = np.array(self.current_image)
                sepia_filter = np.array([
                    [0.393, 0.769, 0.189],
                    [0.349, 0.686, 0.168],
                    [0.272, 0.534, 0.131]
                ])
                sepia_img = img_array.dot(sepia_filter.T)
                sepia_img = np.clip(sepia_img, 0, 255).astype(np.uint8)
                vintage_image = Image.fromarray(sepia_img)
                vintage_image = vintage_image.filter(ImageFilter.GaussianBlur(radius=0.5))
                enhancer = ImageEnhance.Brightness(vintage_image)
                return enhancer.enhance(0.9)
            
            self.process_with_progress("Applying vintage...", vintage)
    
    def apply_temperature(self):
        """Apply temperature adjustment"""
        if self.current_image:
            def temp_adjust():
                temp_value = self.temperature_var.get()
                img_array = np.array(self.current_image).astype(np.float32)
                
                if temp_value > 0:  # Warmer
                    img_array[:,:,0] *= (1 + temp_value * 0.01)
                    img_array[:,:,1] *= (1 + temp_value * 0.005)
                else:  # Cooler
                    img_array[:,:,2] *= (1 + abs(temp_value) * 0.01)
                
                return Image.fromarray(np.clip(img_array, 0, 255).astype(np.uint8))
            
            self.process_with_progress("Adjusting temperature...", temp_adjust)
    
    def apply_denoise(self):
        """Apply noise reduction"""
        if self.current_image:
            self.process_with_progress("Reducing noise...", 
                                     lambda: self.current_image.filter(ImageFilter.MedianFilter(3)))
    
    def histogram_equalization(self):
        """Apply histogram equalization"""
        if self.current_image:
            self.process_with_progress("Equalizing histogram...", 
                                     lambda: ImageOps.equalize(self.current_image))
    
    def auto_enhance(self):
        """Auto enhance image"""
        if self.current_image:
            def enhance():
                enhanced = self.current_image
                enhancer = ImageEnhance.Contrast(enhanced)
                enhanced = enhancer.enhance(1.2)
                enhancer = ImageEnhance.Color(enhanced)
                enhanced = enhancer.enhance(1.1)
                enhancer = ImageEnhance.Sharpness(enhanced)
                return enhancer.enhance(1.1)
            
            self.process_with_progress("Auto enhancing...", enhance)
    
    def apply_unsharp_mask(self):
        """Apply unsharp mask"""
        if self.current_image:
            self.process_with_progress("Applying unsharp mask...", 
                                     lambda: self.current_image.filter(ImageFilter.UnsharpMask(radius=2, percent=150, threshold=3)))
    
    def resize_image(self):
        """Resize image"""
        if self.current_image is None:
            messagebox.showwarning("Warning", "No image loaded!")
            return
        
        try:
            width = int(self.width_var.get())
            height = int(self.height_var.get())
            
            if width <= 0 or height <= 0:
                raise ValueError("Invalid dimensions")
            
            def resize():
                return self.current_image.resize((width, height), Image.Resampling.LANCZOS)
            
            self.process_with_progress("Resizing...", resize)
            
        except ValueError:
            messagebox.showerror("Error", "Invalid dimensions!")
    
    def rotate_image(self, angle):
        """Rotate image"""
        if self.current_image:
            def rotate():
                return self.current_image.rotate(angle, expand=True)
            
            self.process_with_progress(f"Rotating {angle}°...", rotate)
    
    def flip_horizontal(self):
        """Flip image horizontally"""
        if self.current_image:
            self.process_with_progress("Flipping horizontally...", 
                                     lambda: self.current_image.transpose(Image.FLIP_LEFT_RIGHT))
    
    def add_watermark(self):
        """Add watermark"""
        if self.current_image is None:
            messagebox.showwarning("Warning", "No image loaded!")
            return
        
        try:
            watermark_text = self.watermark_text.get().strip()
            if not watermark_text:
                messagebox.showwarning("Warning", "Enter watermark text!")
                return
            
            def add_wm():
                watermarked = self.current_image.copy().convert('RGBA')
                overlay = Image.new('RGBA', watermarked.size, (255, 255, 255, 0))
                draw = ImageDraw.Draw(overlay)
                
                try:
                    font_size = max(watermarked.size) // 30
                    font = ImageFont.truetype("arial.ttf", font_size)
                except:
                    font = ImageFont.load_default()
                
                bbox = draw.textbbox((0, 0), watermark_text, font=font)
                text_width = bbox[2] - bbox[0]
                text_height = bbox[3] - bbox[1]
                
                position = self.watermark_position.get()
                margin = 20
                
                if position == "bottom-right":
                    x = watermarked.width - text_width - margin
                    y = watermarked.height - text_height - margin
                elif position == "bottom-left":
                    x = margin
                    y = watermarked.height - text_height - margin
                elif position == "top-right":
                    x = watermarked.width - text_width - margin
                    y = margin
                elif position == "top-left":
                    x = margin
                    y = margin
                else:  # center
                    x = (watermarked.width - text_width) // 2
                    y = (watermarked.height - text_height) // 2
                
                # Draw background
                padding = 5
                draw.rectangle([x-padding, y-padding, x+text_width+padding, y+text_height+padding], 
                             fill=(255, 255, 255, 128))
                
                # Draw text
                draw.text((x, y), watermark_text, font=font, fill=(0, 0, 0, 180))
                
                watermarked = Image.alpha_composite(watermarked, overlay)
                return watermarked.convert('RGB')
            
            self.process_with_progress("Adding watermark...", add_wm)
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to add watermark: {str(e)}")
    
    def convert_format(self, format_name):
        """Convert to specific format"""
        if self.current_image is None:
            messagebox.showwarning("Warning", "No image loaded!")
            return
        
        extensions = {'PNG': '.png', 'JPEG': '.jpg', 'WebP': '.webp'}
        ext = extensions[format_name]
        
        if self.image_path:
            base_name = os.path.splitext(os.path.basename(self.image_path))[0]
            default_name = f"{base_name}_converted{ext}"
        else:
            default_name = f"converted_image{ext}"
        
        file_path = filedialog.asksaveasfilename(
            title=f"Save as {format_name}",
            initialname=default_name,
            defaultextension=ext,
            filetypes=[(f"{format_name} files", f"*{ext}")]
        )
        
        if file_path:
            try:
                if format_name == 'JPEG' and self.current_image.mode == 'RGBA':
                    rgb_image = Image.new('RGB', self.current_image.size, (255, 255, 255))
                    rgb_image.paste(self.current_image, mask=self.current_image.split()[-1])
                    rgb_image.save(file_path, format_name, quality=95)
                else:
                    self.current_image.save(file_path, format_name)
                
                self.update_status(f"Converted to {format_name}")
                messagebox.showinfo("Success", f"Image converted to {format_name}!")
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to convert: {str(e)}")
    
    def export_all_formats(self):
        """Export in all formats"""
        if self.current_image is None:
            messagebox.showwarning("Warning", "No image loaded!")
            return
        
        folder = filedialog.askdirectory(title="Select export folder")
        if folder:
            try:
                base_name = "exported_image"
                if self.image_path:
                    base_name = os.path.splitext(os.path.basename(self.image_path))[0]
                
                formats = [('PNG', '.png'), ('JPEG', '.jpg'), ('WebP', '.webp')]
                exported = []
                
                for fmt, ext in formats:
                    file_path = os.path.join(folder, f"{base_name}{ext}")
                    
                    if fmt == 'JPEG' and self.current_image.mode == 'RGBA':
                        rgb_image = Image.new('RGB', self.current_image.size, (255, 255, 255))
                        rgb_image.paste(self.current_image, mask=self.current_image.split()[-1])
                        rgb_image.save(file_path, fmt, quality=95)
                    else:
                        self.current_image.save(file_path, fmt)
                    
                    exported.append(fmt)
                
                self.update_status(f"Exported {len(exported)} formats")
                messagebox.showinfo("Success", f"Exported to {folder}\\n{', '.join(exported)}")
                
            except Exception as e:
                messagebox.showerror("Error", f"Export failed: {str(e)}")
    
    def batch_process(self):
        """Batch processing placeholder"""
        messagebox.showinfo("Batch Processing", "Batch processing feature coming soon!")
    
    def show_session_stats(self):
        """Show session statistics"""
        duration = datetime.now() - self.session_stats['session_start']
        hours, remainder = divmod(duration.total_seconds(), 3600)
        minutes, seconds = divmod(remainder, 60)
        
        stats_text = f"""Session Statistics:
        
📊 Images Processed: {self.session_stats['images_processed']}
⚡ Operations Performed: {self.session_stats['operations_performed']}
⏱️ Session Duration: {int(hours):02d}:{int(minutes):02d}:{int(seconds):02d}
🚀 Current Image: {os.path.basename(self.image_path) if self.image_path else 'None'}
📋 History States: {len(self.history)}
🔍 Current Zoom: {self.zoom_factor:.1f}x"""
        
        messagebox.showinfo("Session Statistics", stats_text)

def main():
    """Run the application"""
    root = tk.Tk()
    app = AdvancedImageProcessor(root)
    
    # Center window
    root.update_idletasks()
    x = (root.winfo_screenwidth() // 2) - (root.winfo_width() // 2)
    y = (root.winfo_screenheight() // 2) - (root.winfo_height() // 2)
    root.geometry(f"+{x}+{y}")
    
    root.mainloop()

if __name__ == "__main__":
    main()
