#!/usr/bin/env python
#

from gi.repository import Gtk, GLib

import ConfigParser
import fnmatch
import logging
import os
import pwd
import sys
import subprocess

from optparse import OptionParser

UI_FILE="/usr/share/debathena-session-fixer/fix-my-session.ui"
ACTIONS_DIR="/usr/share/debathena-session-fixer/actions"

STRIP_ENVIRON = ('DISPLAY', )

logger = logging.getLogger('account-repair')
stderr_handler = logging.StreamHandler()
stderr_handler.setFormatter(
    logging.Formatter("%(name)s %(levelname)s: %(message)s"))
logger.addHandler(stderr_handler)

class WizardActionException(Exception):
    pass

class WizardConfigException(Exception):
    pass

class WizardAction:
    _mandatory_options = ['title', 'script']
    _section = 'AccountWizardAction'

    def __init__(self, dirname, filename, builder):
        config = ConfigParser.RawConfigParser({'help': None,
                                               'title': None,
                                               'script': None,
                                               'confirm': None})
        config.read(os.path.join(dirname, filename))
        if not config.has_section(self._section):
            raise WizardConfigException('Not a valid action file')
        self.script = os.path.join(dirname, config.get(self._section, 'script'))
        self.title = config.get(self._section, 'title')
        self.help = config.get(self._section, 'help')
        self.confirm = config.get(self._section, 'confirm')
        if self.title is None or self.script is None:
            raise WizardConfigException('Not a valid action file')
        self.builder = builder

    def run_callback(self, widget, data=None):
        ask = self.builder.get_object("confirm_dialog")
        self.builder.get_object("confirm_title_label").set_text(self.title)
        if self.confirm is None:
            self.builder.get_object("confirm_text_label").set_visible(False)
        else:
            self.builder.get_object("confirm_text_label").set_visible(True)
            self.builder.get_object("confirm_text_label").set_text(self.confirm)
        confirmed = ask.run() == Gtk.ResponseType.YES
        ask.hide()
        if not confirmed:
            return True
        try:
            env = {k:v for k,v in os.environ.items() if k not in STRIP_ENVIRON}
            p = subprocess.Popen(self.script, shell=False, stdin=None,
                                 env=env,
                                 stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            (out, err) = p.communicate()
            results = self.builder.get_object("output_dialog")
            errors = p.returncode != 0
            if len(out) < 1:
                out = "The command {0} successfully.".format(
                    "did not complete" if errors else "completed")
            if len(err) < 1 and errors:
                err = "Unknown error."
            self.builder.get_object("output_title_label").set_text(self.title)
            self.builder.get_object("output_label").set_text(out)
            self.builder.get_object("errors_label").set_text(err)
            self.builder.get_object("errors_label").set_visible(errors)
            self.builder.get_object("errors_occurred").set_visible(errors)
            results.run()
            results.hide()
        except OSError as e:
            dlg = Gtk.MessageDialog(self.builder.get_object("main_window"),
                                    Gtk.DialogFlags.MODAL,
                                    Gtk.MessageType.ERROR,
                                    Gtk.ButtonsType.CLOSE,
                                    "Unable to run script: " + e.strerror)
            dlg.run()
            dlg.destroy()
        return True

    def help_dialog(self, widget, data=None):
        dlg = self.builder.get_object("help_dialog")
        self.builder.get_object("help_title_label").set_text(self.title)
        self.builder.get_object("help_text_label").set_text(
            self.help.replace("\n", " "))
        dlg.run()
        dlg.hide()

    def widget(self):
        _internal_box = Gtk.Box()
        _lbl = Gtk.Label(label=self.title, halign=Gtk.Align.START)
        _internal_box.pack_start(_lbl, True, True, 2)
        _run_button = Gtk.Button(label="Run")
        _run_button.connect("clicked", self.run_callback)
        _internal_box.pack_start(_run_button, False, False, 2)
        _help_button = Gtk.Button(label="Help")
        _help_button.connect("clicked", self.help_dialog)
        _internal_box.pack_start(_help_button, False, False, 2)
        _internal_box.show_all()
        return _internal_box


class SessionFixer:
    def __init__(self, options):
        self.logger = logging.getLogger('fix-my-session')
        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter('%(levelname)s:%(message)s'))
        self.logger.addHandler(handler)
        if options.debug:
            self.logger.setLevel(logging.DEBUG)
        self.builder = Gtk.Builder()
        try: 
            self.builder.add_from_file(options.ui_file)
            self.logger.debug("Builder UI loaded")
        except GLib.GError as e:
            self.logger.exception("Unable to load UI:")
            sys.exit(1)
        self.builder.connect_signals(self)
        pwent = pwd.getpwuid(os.getuid())
        userlabel = "{0} ({1}@mit.edu)".format(pwent.pw_gecos.split(',')[0],
                                               pwent.pw_name)
        self.builder.get_object("username_label").set_text(userlabel)
        self.builder.get_object("main_window").show_all()
        self._populate_actions()
    
    def _populate_actions(self):
        self.actions = []
        box = self.builder.get_object("actions_box")
        try:
            for f in fnmatch.filter(os.listdir(options.actions_dir),
                                    '*.action'):
                self.actions.append(WizardAction(options.actions_dir,
                                                 f, self.builder))
        except OSError as e:
            error = Gtk.Label()
            error.show()
            if e.errno == errno.ENOENT:
                error.set_text("Cannot find any actions for the wizard to run.")
            else:
                error.set_text("Unexpected error: " + e.message)
            box.pack_start(error, False, False, 2)
        
        for a in self.actions:
            box.pack_start(a.widget(), False, False, 2)
            


    def quit(self):
        Gtk.main_quit()

    def on_quit_button_clicked(self, widget, data=None):
        self.quit()

if __name__ == '__main__':
    parser = OptionParser()
    parser.set_defaults(debug=False,
                        ui_file=UI_FILE,
                        actions_dir=ACTIONS_DIR)
    parser.add_option("--debug", action="store_true", dest="debug")
    parser.add_option("--ui", action="store", type="string", dest="ui_file")
    parser.add_option("--dir", action="store", type="string", dest="actions_dir")
    (options, args) = parser.parse_args()
    app = SessionFixer(options)
    Gtk.main()
