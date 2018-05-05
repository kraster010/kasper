from evennia.commands import cmdset

from commands import command
from typeclasses.defaults.default_objects import Object


class ExitCommand(command.Command):
    """
    This is a command that simply cause the caller to traverse
    the object it is attached to.

    """
    obj = None

    def func(self):
        """
        Default exit traverse if no syscommand is defined.
        """

        if self.obj.access(self.caller, 'traverse'):
            # we may traverse the exit.
            self.obj.at_traverse(self.caller, self.obj.destination)
        else:
            # exit is locked
            if self.obj.db.err_traverse:
                # if exit has a better error message, let's use it.
                self.caller.msg(self.obj.db.err_traverse)
            else:
                # No shorthand error message. Call hook.
                self.obj.at_failed_traverse(self.caller)

    def get_extra_info(self, caller, **kwargs):
        """
        Shows a bit of information on where the exit leads.

        Args:
            caller (Object): The object (usually a character) that entered an ambiguous command.
            **kwargs (dict): Arbitrary, optional arguments for users
                overriding the call (unused by default).

        Returns:
            A string with identifying information to disambiguate the command, conventionally with a preceding space.
        """
        if self.obj.destination:
            return " (exit to %s)" % self.obj.destination.get_display_name(caller)
        else:
            return " (%s)" % self.obj.get_display_name(caller)


class Exit(Object):
    """
        Exits are connectors between rooms. Exits are normal Objects except
        they defines the `destination` property. It also does work in the
        following methods:

         basetype_setup() - sets default exit locks (to change, use `at_object_creation` instead).
         at_cmdset_get(**kwargs) - this is called when the cmdset is accessed and should
                                  rebuild the Exit cmdset along with a command matching the name
                                  of the Exit object. Conventionally, a kwarg `force_init`
                                  should force a rebuild of the cmdset, this is triggered
                                  by the `@alias` command when aliases are changed.
         at_failed_traverse() - gives a default error message ("You cannot
                                go there") if exit traversal fails and an
                                attribute `err_traverse` is not defined.

        Relevant hooks to overload (compared to other types of Objects):
        at_traverse(traveller, target_loc) - called to do the actual traversal and calling of the other hooks.
                                            If overloading this, consider using super() to use the default
                                            movement implementation (and hook-calling).
        at_after_traverse(traveller, source_loc) - called by at_traverse just after traversing.
        at_failed_traverse(traveller) - called by at_traverse if traversal failed for some reason. Will
                                        not be called if the attribute `err_traverse` is
                                        defined, in which case that will simply be echoed.

        This is the base exit object - it connects a location to another.
        This is done by the exit assigning a "command" on itself with the
        same name as the exit object (to do this we need to remember to
        re-create the command when the object is cached since it must be
        created dynamically depending on what the exit is called). This
        command (which has a high priority) will thus allow us to traverse
        exits simply by giving the exit-object's name on its own.

        """

    exit_command = ExitCommand
    priority = 101

    # Helper classes and methods to implement the Exit. These need not
    # be overloaded unless one want to change the foundation for how
    # Exits work. See the end of the class for hook methods to overload.

    def create_exit_cmdset(self, exidbobj):
        """
        Helper function for creating an exit command set + command.

        The command of this cmdset has the same name as the Exit
        object and allows the exit to react when the account enter the
        exit's name, triggering the movement between rooms.

        Args:
            exidbobj (Object): The DefaultExit object to base the command on.

        """

        # create an exit command. We give the properties here,
        # to always trigger metaclass preparations
        cmd = self.exit_command(key=exidbobj.db_key.strip().lower(),
                                aliases=exidbobj.aliases.all(),
                                locks=str(exidbobj.locks),
                                auto_help=False,
                                destination=exidbobj.db_destination,
                                arg_regex=r"^$",
                                is_exit=True,
                                obj=exidbobj)
        # create a cmdset
        exit_cmdset = cmdset.CmdSet(None)
        exit_cmdset.key = 'ExitCmdSet'
        exit_cmdset.priority = self.priority
        exit_cmdset.duplicates = True
        # add command to cmdset
        exit_cmdset.add(cmd)
        return exit_cmdset

    # Command hooks

    def basetype_setup(self):
        """
        Setup exit-security

        You should normally not need to overload this - if you do make
        sure you include all the functionality in this method.

        """
        super(Exit, self).basetype_setup()

        # setting default locks (overload these in at_object_creation()
        self.locks.add(";".join(["puppet:false()",  # would be weird to puppet an exit ...
                                 "traverse:all()",  # who can pass through exit by default
                                 "get:false()"]))  # noone can pick up the exit

        # an exit should have a destination (this is replaced at creation time)
        if self.location:
            self.destination = self.location

    def at_cmdset_get(self, **kwargs):
        """
        Called just before cmdsets on this object are requested by the
        command handler. If changes need to be done on the fly to the
        cmdset before passing them on to the cmdhandler, this is the
        place to do it. This is called also if the object currently
        has no cmdsets.

        Kwargs:
          force_init (bool): If `True`, force a re-build of the cmdset
            (for example to update aliases).

        """

        if "force_init" in kwargs or not self.cmdset.has_cmdset("ExitCmdSet", must_be_default=True):
            # we are resetting, or no exit-cmdset was set. Create one dynamically.
            self.cmdset.add_default(self.create_exit_cmdset(self), permanent=False)

    def at_init(self):
        """
        This is called when this objects is re-loaded from cache. When
        that happens, we make sure to remove any old ExitCmdSet cmdset
        (this most commonly occurs when renaming an existing exit)
        """
        self.cmdset.remove_default()

    def at_traverse(self, traversing_object, target_location, **kwargs):
        """
        This implements the actual traversal. The traverse lock has
        already been checked (in the Exit command) at this point.

        Args:
            traversing_object (Object): Object traversing us.
            target_location (Object): Where target is going.
            **kwargs (dict): Arbitrary, optional arguments for users
                overriding the call (unused by default).

        """
        source_location = traversing_object.location
        if traversing_object.move_to(target_location):
            self.at_after_traverse(traversing_object, source_location)
        else:
            if self.db.err_traverse:
                # if exit has a better error message, let's use it.
                self.caller.msg(self.db.err_traverse)
            else:
                # No shorthand error message. Call hook.
                self.at_failed_traverse(traversing_object)

    def at_failed_traverse(self, traversing_object, **kwargs):
        """
        Overloads the default hook to implement a simple default error message.

        Args:
            traversing_object (Object): The object that failed traversing us.
            **kwargs (dict): Arbitrary, optional arguments for users
                overriding the call (unused by default).

        Notes:
            Using the default exits, this hook will not be called if an
            Attribute `err_traverse` is defined - this will in that case be
            read for an error string instead.

        """
        traversing_object.msg("You cannot go there.")
