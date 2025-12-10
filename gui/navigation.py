import os
import customtkinter as ctk
from customtkinter import ThemeManager
import PIL.Image as Image
from gui.helpers import resource_path

class NavigationMixin:

    #--------------------------------------------------
    #-- Navigation Pane
    #-- init and handlers
    #--------------------------------------------------

    def initNavgiationPane(self):

        self.fNavigation = ctk.CTkFrame(self, corner_radius=0)
        self.fNavigation.grid(row=0, column=0, sticky="nsew")
        self.fNavigation.grid_rowconfigure(6, weight=1)
        # logo
        self.mLRS_Logo_image = ctk.CTkImage(Image.open(resource_path(os.path.join("assets", "mLRS_logo_long_w_slogan_378x194.png"))), size=(150, 194/378*170))
        self.fNavigation_Logo_logo = ctk.CTkLabel(self.fNavigation,
            text="", image=self.mLRS_Logo_image)
        self.fNavigation_Logo_logo.grid(row=0, column=0, padx=10, pady=10)

        self.fNavigation_Logo_label = ctk.CTkLabel(self.fNavigation,
            text="mLRS Flasher",
            font=ctk.CTkFont(size=15, weight="bold"))
        self.fNavigation_Logo_label.grid(row=1, column=0, padx=20, pady=10)

        # navigation options

        self.fNavigation_fg_color = ThemeManager.theme["CTkSegmentedButton"]["fg_color"]
        self.fNavigation_hover_color = ThemeManager.theme["CTkSegmentedButton"]["unselected_hover_color"]
        self.fNavigation_selected_color = ThemeManager.theme["CTkSegmentedButton"]["selected_color"]
        self.fNavigation_selected_hover_color = ThemeManager.theme["CTkSegmentedButton"]["selected_hover_color"]
        #print(ThemeManager.theme["CTkSegmentedButton"])

        self.fNavigation_TxModuleExternal_button = ctk.CTkButton(self.fNavigation,
            text="Tx Module (external)",
            corner_radius=0, height=40, border_spacing=10,
            #image=self.home_image,
            #anchor="w",
            command=self.fNavigation_TxModuleExternal_button_event)
        self.fNavigation_TxModuleExternal_button.grid(row=2, column=0, sticky="ew")

        self.fNavigation_Receiver_button = ctk.CTkButton(self.fNavigation,
            text="Receiver",
            corner_radius=0, height=40, border_spacing=10,
            #image=self.chat_image,
            #anchor="w",
            command = self.fNavigation_Receiver_button_event)
        self.fNavigation_Receiver_button.grid(row=3, column=0, sticky="ew")

        self.fNavigation_TxModuleInternal_button = ctk.CTkButton(self.fNavigation,
            text = "Tx Module (internal)",
            corner_radius=0, height=40, border_spacing=10,
            #image=self.add_user_image,
            #anchor="w",
            command = self.fNavigation_TxModuleInternal_button_event)
        self.fNavigation_TxModuleInternal_button.grid(row=4, column=0, sticky="ew")

        self.fNavigation_LuaScript_button = ctk.CTkButton(self.fNavigation,
            text = "Lua Script",
            corner_radius=0, height=40, border_spacing=10,
            #image=self.add_user_image,
            #anchor="w",
            command = self.fNavigation_LuaScript_button_event)
        self.fNavigation_LuaScript_button.grid(row=5, column=0, sticky="ew")

        # appearance options

        self.fNavigation_SetAppearanceMode_menu = ctk.CTkOptionMenu(self.fNavigation,
            values=["Light", "Dark", "System"],
            command=self.fNavigation_SetAppearanceMode_menu_event)
        self.fNavigation_SetAppearanceMode_menu.grid(row=6, column=0, padx=20, pady=20, sticky="s")

        #self.fNavigation_SetColorTheme_menu = ctk.CTkOptionMenu(self.fNavigation,
        #    values=["Blue", "Green", "Dark-Blue"],
        #    command=self.fNavigation_SetColorTheme_menu_event)
        #self.fNavigation_SetColorTheme_menu.grid(row=7, column=0, padx=20, pady=20, sticky="s")


    def fNavigation_select_frame_by_name(self, name):
        # show selected frame, and adjust color
        if name == "tx_module_ext":
            self.fNavigation_TxModuleExternal_button.configure(
                fg_color=self.fNavigation_selected_color,
                hover_color=self.fNavigation_selected_hover_color
                )
            self.fTxModuleExternal.grid(row=0, column=1, sticky="nsew")
        else:
            self.fNavigation_TxModuleExternal_button.configure(
                fg_color=self.fNavigation_fg_color,
                hover_color=self.fNavigation_hover_color)
            self.fTxModuleExternal.grid_forget()

        if name == "receiver":
            self.fNavigation_Receiver_button.configure(
                fg_color=self.fNavigation_selected_color,
                hover_color=self.fNavigation_selected_hover_color)
            self.fReceiver.grid(row=0, column=1, sticky="nsew")
        else:
            self.fNavigation_Receiver_button.configure(
                fg_color=self.fNavigation_fg_color,
                hover_color=self.fNavigation_hover_color)
            self.fReceiver.grid_forget()

        if name == "tx_module_int":
            self.fNavigation_TxModuleInternal_button.configure(
                fg_color=self.fNavigation_selected_color,
                hover_color=self.fNavigation_selected_hover_color)
            self.fTxModuleInternal.grid(row=0, column=1, sticky="nsew")
        else:
            self.fNavigation_TxModuleInternal_button.configure(
                fg_color=self.fNavigation_fg_color,
                hover_color=self.fNavigation_hover_color)
            self.fTxModuleInternal.grid_forget()

        if name == "lua_script":
            self.fNavigation_LuaScript_button.configure(
                fg_color=self.fNavigation_selected_color,
                hover_color=self.fNavigation_selected_hover_color)
            self.fLuaScript.grid(row=0, column=1, sticky="nsew")
        else:
            self.fNavigation_LuaScript_button.configure(
                fg_color=self.fNavigation_fg_color,
                hover_color=self.fNavigation_hover_color)
            self.fLuaScript.grid_forget()

    def fNavigation_TxModuleExternal_button_event(self):
        self.fNavigation_select_frame_by_name("tx_module_ext")

    def fNavigation_Receiver_button_event(self):
        self.fNavigation_select_frame_by_name("receiver")

    def fNavigation_TxModuleInternal_button_event(self):
        self.fNavigation_select_frame_by_name("tx_module_int")

    def fNavigation_LuaScript_button_event(self):
        self.fNavigation_select_frame_by_name("lua_script")

    def fNavigation_SetAppearanceMode_menu_event(self, opt):
        ctk.set_appearance_mode(opt)

    #def fNavigation_SetColorTheme_menu_event(self, opt):
    #    ctk.set_default_color_theme(opt.lower())
