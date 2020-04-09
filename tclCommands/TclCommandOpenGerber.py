from tclCommands.TclCommand import TclCommandSignaled
from camlib import ParseError
from FlatCAMObj import FlatCAMGerber

import collections


class TclCommandOpenGerber(TclCommandSignaled):
    """
    Tcl shell command to opens a Gerber file
    """

    # array of all command aliases, to be able use  old names for backward compatibility (add_poly, add_polygon)
    aliases = ['open_gerber']

    # dictionary of types from Tcl command, needs to be ordered
    arg_names = collections.OrderedDict([
        ('filename', str)
    ])

    # dictionary of types from Tcl command, needs to be ordered , this  is  for options  like -optionname value
    option_types = collections.OrderedDict([
        ('outname', str)
    ])

    # array of mandatory options for current Tcl command: required = {'name','outname'}
    required = ['filename']

    # structured help for current command, args needs to be ordered
    help = {
        'main': "Opens a Gerber file.",
        'args': collections.OrderedDict([
            ('filename', 'Absolute path to file to open. Required.\n'
                         'WARNING: no spaces are allowed. If unsure enclose the entire path with quotes.'),
            ('outname', 'Name of the resulting Gerber object.')
        ]),
        'examples': ["open_gerber gerber_object_path -outname bla",
                     'open_gerber "D:\\my_gerber_file with spaces in the name.GRB"']
    }

    def execute(self, args, unnamed_args):
        """
        execute current TCL shell command

        :param args: array of known named arguments and options
        :param unnamed_args: array of other values which were passed into command
            without -somename and  we do not have them in known arg_names
        :return: None or exception
        """

        # How the object should be initialized
        def obj_init(gerber_obj, app_obj):

            if not isinstance(gerber_obj, FlatCAMGerber):
                self.raise_tcl_error('Expected FlatCAMGerber, got %s %s.' % (outname, type(gerber_obj)))

            # Opening the file happens here
            try:
                gerber_obj.parse_file(filename)
            except IOError:
                app_obj.inform.emit("[ERROR_NOTCL] Failed to open file: %s " % filename)
                self.raise_tcl_error('Failed to open file: %s' % filename)

            except ParseError as e:
                app_obj.inform.emit("[ERROR_NOTCL] Failed to parse file: %s, %s " % (filename, str(e)))
                self.log.error(str(e))
                return

        filename = args['filename']

        if ' ' in filename:
            return "The absolute path to the project file contain spaces which is not allowed.\n" \
                   "Please enclose the path within quotes."

        if 'outname' in args:
            outname = args['outname']
        else:
            outname = filename.split('/')[-1].split('\\')[-1]

        if 'follow' in args:
            self.raise_tcl_error("The 'follow' parameter is obsolete. To create 'follow' geometry use the 'follow' "
                                 "parameter for the Tcl Command isolate()")

        with self.app.proc_container.new("Opening Gerber"):

            # Object creation
            self.app.new_object("gerber", outname, obj_init, plot=False)

            # Register recent file
            self.app.file_opened.emit("gerber", filename)

            # GUI feedback
            self.app.inform.emit("[success] Opened: " + filename)
